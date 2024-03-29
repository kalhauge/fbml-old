"""
.. module:: fbml.extensions.llvm

"""
import string
import random
import collections
import xml.etree.ElementTree as ET

import llvm.core as llvmc
import llvm.ee as llvmee

import logging
log = logging.getLogger(__name__)

from functools import partial

from . import Extension

from ..parsers import xmlformat
from ..util import visitors

from ..structure import Label
from .. import element

from ..util import log_it

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

int_ = llvmc.Type.int(64)
char = llvmc.Type.int(8)
void = llvmc.Type.void()
ptr = llvmc.Type.pointer
array = llvmc.Type.array

def add_main(llvm_module, method, args):
   
    ### GLOBAL

    pfn = llvmc.Type.function(int_, [ptr(char)],True)
    printf = llvmc.Function.new(llvm_module,pfn,'printf')

    printer_strs = {}
    printer_strs['Integer'] = llvm_module.add_global_variable(array(char,12),'iprt')
    printer_strs['Integer'].initializer = llvmc.GlobalVariable.stringz("Result: %d\n")
    
    printer_strs['Real'] = llvm_module.add_global_variable(array(char,12),'rprt')
    printer_strs['Real'].initializer = llvmc.GlobalVariable.stringz("Result: %f\n")   
    ### LOCAL

    function_type = llvmc.Type.function(void,[])
    llvm_function = llvmc.Function.new(llvm_module,function_type,name='main')
    blok = llvm_function.append_basic_block('entry')
    bldr = llvmc.Builder.new(blok) 

    function_args = [] 
   

    for data, val in zip(sorted(method.req.slots,key=llvm_arg),args):
        function_args.append(llvm_constant(data.type, val))
    
    results = []
    for data in sorted(method.ens.slots,key=llvm_arg):
        results.append(bldr.alloca(llvm_type(data.type)))

    bldr.call(method.ens.llvm_function,function_args + results)
    
    for result, data in zip(results,sorted(method.ens.slots,key=llvm_arg)):
        str_ptr = bldr.gep(printer_strs[data.type.name],[llvm_int(0), llvm_int(0)])
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
    'Boolean'  : (llvmc.Type.int(),'bool'),
}

function_map = {
    'gt'       :  (lambda self : partial(llvmc.Builder.icmp,self,llvmc.ICMP_SGT)),
}

def llvm_function(name, bldr):
    if hasattr(bldr,name):
        return getattr(bldr,name)
    else:
        return function_map[name](bldr)

def llvm_type(fbml_type):
    return type_map[fbml_type.name][0]

def llvm_int(value, bit=32):
    return llvmc.Constant.int(llvmc.Type.int(bit),value)

def llvm_constant(fbml_type, value):
    name = type_map[fbml_type.name][1]
    return getattr(llvmc.Constant, name)(llvm_type(fbml_type), value)

def llvm_arg(data):
    return data.llvm_arg

def source_data_in_order(method):
    return sorted(method.req.slots,key=llvm_arg)

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

BlockData = collections.namedtuple('Block',
        [
            'blocks',
            'values',
            'bldr',
            ])

def random_name(names):
    blockname = None
    while not blockname or blockname in names:
        blockname = ''.join(
                random.choice(string.ascii_lowercase) 
                for _ in range(8))
    return blockname

def llvm_function_from_impl(impl, name, llvm_module):
    """ Asumes only a single return value"""
    target, = impl.targets
    return llvmc.Function.new(
            llvm_module,
            llvmc.Type.function(llvm_type(target.data.type),
                [llvm_type(source.data.type) for source in impl.source_sinks]
                ),
            name 
            )

class BlockCompiler(visitors.ControlFlowVisitor):

    def __init__(self, module):
        self.module = module

    def setup(self, impl, data):
#        last_block = data.bldr.basic_block
#        block_name = random_name(data.blocks)
#        llvm_block = last_block.function.append_basic_block(block_name)
#        data.blocks[block_name] = llvm_block
#        
#        data.bldr.branch(llvm_block)
#        data.bldr.position_at_end(llvm_block)

        return data 

    def apply(self, data, function):
       
        values = dict()
        for slot, sink in vars(function.sources).items():
            if isinstance(sink,element.Constant):
                values[slot] = llvm_constant(sink.data.value.type,
                        sink.data.value.value)
            else:
                values[slot] = data.values[sink.owner][sink.slot]

        methods = [Label.find(method_label,self.module)
                        for method_label in function.data.methods]
        if len(methods) == 1:
            method, = methods
            try:
                llvm_name = method.ens.llvm
            except AttributeError:
                # Method is having an implenmations (we hope)
                impl = method.impl
                em_data = BlockData(
                            blocks = data.blocks,
                            values = {None: values},
                            bldr = data.bldr,
                            )
                self.visit(impl,em_data)
                data.values[function] = {slot: em_data.values[impl][slot]
                        for slot in vars(impl.targets)}

            else:
                func = llvm_function(llvm_name, data.bldr) 
                slot_name, = method.ens.slots.names
                args = [None, None, slot_name]
                for slot, data_ in method.req.slots.with_names:
                    args[data_.llvm_arg] = values[slot]
                data.values[function] = {slot_name: func(*args)}
        else:
            # Assume that the method should be matched.
            matchables = set()
            for slot, data_ in  methods[0].req.slots.with_names:
                if hasattr(data_,'match'): 
                    matchables.add(slot)
            if not matchables:
                raise Exception("Ambigues")
            
            match, = matchables
            
            true, false = (methods if methods[0].req.slots[match].match
                        else reversed(methods))

            current_block = data.bldr.basic_block
          
            func = data.bldr.basic_block.function
            
            true_block = func.append_basic_block(random_name(data.blocks))
            false_block = func.append_basic_block(random_name(data.blocks))
            merge_block = func.append_basic_block(random_name(data.blocks))

            data.bldr.position_at_end(true_block)
            true_data = BlockData(
                        blocks = data.blocks,
                        values = {None: dict(values)},
                        bldr = data.bldr,
                        )
            true_data = self.visit(true.impl,true_data)
            true_block = data.bldr.basic_block
            data.bldr.branch(merge_block)
            
            data.bldr.position_at_end(false_block)
            false_data = BlockData(
                        blocks = data.blocks,
                        values = {None: dict(values)},
                        bldr = data.bldr,
                        )
            false_data = self.visit(false.impl,false_data)
            false_block = data.bldr.basic_block 
            data.bldr.branch(merge_block)
            
            data.bldr.position_at_end(current_block)
            data.bldr.cbranch(values[match], true_block, false_block)
            
            data.bldr.position_at_end(merge_block)

            merge_values = dict()
            for slot in vars(true.impl.targets):
                phi = data.bldr.phi(llvm_type(true.ens.slots[slot].type))
                phi.add_incoming(true_data.values[true.impl][slot],true_block)
                phi.add_incoming(false_data.values[false.impl][slot],false_block)
                merge_values[slot] = phi

            data.values[function] = merge_values

        return data 

    def final(self, impl, data):
        data.values[impl] = dict()
        for slot, sink in vars(impl.targets).items():
            data.values[impl][slot] = data.values[sink.owner][sink.slot]
        return data



class LLVMExtension (Extension):
    NAME = 'llvm'
    XML_FORMATS = [LLVMFormat(),LLVMArgFormat()]

