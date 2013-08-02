"""
.. module:: fbml.extensions.llvm

"""

from . import Extension

from ..parsers import xmlformat
from ..util import visitors

from ..util import log_it

import xml.etree.ElementTree as ET

import llvm.core as llvmc
import llvm.ee as llvmee

import logging

log = logging.getLogger(__name__)

class LLVMFormat(object):
    name = 'llvm'

    def parse(self, parser, tree):
        return tree.text

    def write(self, writer, value, tree):
        ET.SubElement(tree,'llvm').text = str(value) 

class LLVMArgFormat(object):
    name = 'llvm_arg'

    def parse(self, parser, tree):
        return int(tree.text)

    def write(self, writer, value, tree):
        ET.SubElement(tree,'llvm').text = str(value) 

def compile_to_llvm(module):
    llvm_module = llvmc.Module.new('_'.join(module.label.to_name_list()))
    visitor = MethodCreater(module,llvm_module)
    for method in module.methods:
        result = visitor.visit(method)
    return llvm_module

int_ = llvmc.Type.int(32)
char = llvmc.Type.int(8)
void = llvmc.Type.void()
ptr = llvmc.Type.pointer
array = llvmc.Type.array

def execute_method(llvm_module, method, args):
   
    ### GLOBAL

    pfn = llvmc.Type.function(int_, [ptr(char)],True)
    printf = llvmc.Function.new(llvm_module,pfn,'printf')

    int_printer = llvm_module.add_global_variable(array(char,12),'iprt')
    int_printer.initializer = llvmc.GlobalVariable.stringz("Result: %i\n")
    
    ### LOCAL

    function_type = llvmc.Type.function(void,[])
    llvm_function = llvmc.Function.new(llvm_module,function_type,name='main')
    blok = llvm_function.append_basic_block('entry')
    bldr = llvmc.Builder.new(blok) 

    function_args = [] 
    str_ptr = bldr.gep(int_printer,[llvm_int(0), llvm_int(0)])

    for data, val in zip(sorted(method.req.slots,key=llvm_arg),args):
        function_args.append(llvm_constant(data.type, val))
    
    results = []
    for data in sorted(method.ens.slots,key=llvm_arg):
        results.append(bldr.alloca(llvm_type(data.type)))

    bldr.call(method.ens.llvm_function,function_args + results)
    
    for result, data in zip(results,sorted(method.ens.slots,key=llvm_arg)):
        bldr.call(printf,[str_ptr, bldr.load(result)])
    
    bldr.ret_void()
    llvm_function.verify()
    llvm_module.verify()

    return llvm_module

def get_llvm_types(elm):
    return llvm_types(s['Type'] for s in elm)
    
type_map = {
    'Integer'  : (llvmc.Type.int(),'int'),
    'Real'     : (llvmc.Type.double(),'real'),
    #'Char'     : llvmc.Type.int(8)
}

def llvm_type(fbml_type):
    return type_map[fbml_type.name][0]

def llvm_int(value, bit=32):
    return llvmc.Constant.int(llvmc.Type.int(bit),value)


def llvm_constant(fbml_type, value):
    name = type_map[fbml_type.name][1]
    return getattr(llvmc.Constant, name)(llvm_type(fbml_type), value)

def llvm_arg(data):
    return data.llvm_arg



class FunctionCodeBuilder (object):

    def __init__(self, llvm_module, method):
        self.llvm_module = llvm_module
        self.method = method
        self.var = dict()
        self._setup()

    def _get_types(self):
        impl = self.method.impl
        types = [None] * ( len(impl.source_sinks) + len(impl.target_sinks))
        for data in self.method.req.slots:
            types[data.llvm_arg] = llvm_type(data.type)

        for data in self.method.ens.slots:
            types[data.llvm_arg] = llvmc.Type.pointer(llvm_type(data.type))
        return types


    def _index_map(self, slots, start= 0):
        indices = enumerate(slots) 
        return dict((slot_id,index + start) for index,slot_id in indices )

    def _setup(self):

        def assing_llvm_arg(pair):
            index,(name, data) = pair
            data.llvm_arg = index

        [assing_llvm_arg(pair) for pair in enumerate(
            sorted(self.method.req.slots.with_names,key=lambda x : x[0]) + 
            sorted(self.method.ens.slots.with_names,key=lambda x : x[0])
            )]
        args_types = self._get_types()

        self.llvm_function = llvmc.Function.new(
                self.llvm_module,
                llvmc.Type.function(llvmc.Type.void(),args_types),
                self.method.req.method_name
                )

        impl = self.method.impl
       
        for slot_id, sink in impl.source_sinks.with_names:
            arg = self.llvm_function.args[sink.data.llvm_arg]
            arg.name = sink.label.name
            self.var[sink] = arg

        for slot_id, sink in impl.target_sinks.with_names:
            arg = self.llvm_function.args[sink.data.llvm_arg]
            arg.name = sink.label.name
            self.var[sink] = arg

        for sink in impl.constant_sinks:
            self.var[sink] = llvm_constant(sink.type,sink.value.value) 

        blok = self.llvm_function.append_basic_block('entry')
        self.bldr = llvmc.Builder.new(blok) 

    def end(self):
        self.bldr.ret_void()
        self.llvm_function.verify()
        return self

    @log_it(log.debug)
    def call_buildin(self, method, function):
        buildin_function = getattr(self.bldr, method.ens.data.llvm)

        ret_sink = list(function.targets)[0]
        args = [None, None, ret_sink.name]

        for slot_id, sink in function.sources.with_names:
            slot = method.req.slots[slot_id]
            args[slot.llvm_arg] = self.var[sink]
    
        var = buildin_function(*args)
        if var.name != ret_sink.name:
             #Variable already exists
            self.bldr.store(var,self.var[ret_sink])
        else: 
            self.var[ret_sink] = var
        return self

    @log_it(log.debug)
    def call(self, method, function):
        
        for slot, sink in function.targets.with_names:
            # Test if sink is a target, do nothing
            if not sink in self.var:
                self.var[sink] = self.bldr.alloca(
                        llvm_type(sink.data.type),sink.name)
            

        source_values = dict((slot, self.var[sink]) 
                            for slot, sink in function.sources.with_names)
        target_values = dict((slot, self.var[sink]) 
                            for slot, sink in function.targets.with_names)

        number_of_slots = len(method.req.slots)
        number_of_slots += len(method.ens.slots)
        args = [None] * number_of_slots
        
        for slot, data in method.req.slots.with_names:
            args[data.llvm_arg] = source_values[slot]
        
        for slot, data in method.ens.slots.with_names:
            args[data.llvm_arg] = target_values[slot]
        
        self.bldr.call(method.ens.llvm_function, args,'')

        for sink in function.targets:
            # Test if sink is target for method, ugly
            if not hasattr(sink.data,'llvm_arg'):
                ptr = self.var[sink] 
                self.var[sink] = self.bldr.load(ptr,sink.name)
        
        return self


class MethodCreater(visitors.ControlFlowVisitor):

    def __init__(self,module,llvm_module):
        super(MethodCreater,self).__init__()
        self._module = module
        self._llvm_module = llvm_module
        
    def setup(self,method):
        return FunctionCodeBuilder(self._llvm_module,method)

    def final(self,method,cb):
        cb.end()
        method.ens.llvm_function = cb.llvm_function
        return cb.llvm_function

    def apply(self,function,cb):
        from ..util.matchers import all_of
        from .methodname import has_method_name
        from .type import has_types
        from ..util.matchers import has_sources, has_targets
        
        method_name = function.data.method_name
        types = [(slot,sink.data.type) 
                for slot, sink in function.sources.with_names]
       
        requirement = all_of(
                        has_method_name(method_name),
                        has_types(types),
                        has_sources(function.sources.names),
                        has_targets(function.targets.names)
                       )

        method = self._module.get_method_where(requirement)
        if hasattr(method.ens.data,'llvm'):
            return cb.call_buildin(method,function)
        else:
            self.visit(method)
            return cb.call(method,function)
        

class LLVMExtension (Extension):
    NAME = 'llvm'
    XML_FORMATS = [LLVMFormat(),LLVMArgFormat()]

