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

def get_llvm_types(elm):
    return llvm_types(s['Type'] for s in elm)
    
type_map = {
    'Integer'  : llvmc.Type.int(),
    'Real'     : llvmc.Type.double(),
    'Char'     : llvmc.Type.int(8)
}

def llvm_type(fbml_type):
    return type_map[fbml_type.name]

class FunctionCodeBuilder (object):

    def __init__(self, llvm_module, method):
        self.llvm_module = llvm_module
        self.method = method
        self.var = dict()
        self._setup()

    def _get_types(self):
        types = [None] * ( len(self.source_index) + len(self.target_index) )
        impl = self.method.impl
        for slot_id, sink in impl.source_sinks.with_names:
            types[self.source_index[slot_id]] = llvm_type(sink.data.type)
        for slot_id, sink in impl.target_sinks.with_names:
            types[self.target_index[slot_id]] = \
                    llvmc.Type.pointer(llvm_type(sink.data.type))
        return types


    def _index_map(self, slots, start= 0):
        indices = enumerate(slots) 
        return dict((slot_id,index + start) for index,slot_id in indices )

    def _setup(self):
        self.source_index = self._index_map(sorted(self.method.req.slots.names))
        self.target_index = self._index_map(sorted(self.method.ens.slots.names),
            len(self.method.req.slots))
       
        args_types = self._get_types()

        self.llvm_function = llvmc.Function.new(
                self.llvm_module,
                llvmc.Type.function(llvmc.Type.void(),args_types),
                self.method.label.name
                )

        impl = self.method.impl
       
        for slot_id, sink in impl.source_sinks.with_names:
            index = self.source_index[slot_id]
            arg = self.llvm_function.args[index]
            arg.name = sink.label.name
            self.var[sink] = arg

        for slot_id, sink in impl.target_sinks.with_names:
            index = self.target_index[slot_id]
            arg = self.llvm_function.args[index]
            arg.name = sink.label.name
            self.var[sink] = arg

        blok = self.llvm_function.append_basic_block('entry')
        self.bldr = llvmc.Builder.new(blok) 

    def ret_void(self):
        self.bldr.ret_void()
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



class MethodCreater(visitors.ControlFlowVisitor):

    def __init__(self,module,llvm_module):
        super(MethodCreater,self).__init__()
        self._module = module
        self._llvm_module = llvm_module
        
    def setup(self,method):
        return FunctionCodeBuilder(self._llvm_module,method)

    def final(self,method,cb):
        cb.ret_void()
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

        return cb.call_buildin(method,function)
        

class LLVMExtension (Extension):
    NAME = 'llvm'
    XML_FORMATS = [LLVMFormat(),LLVMArgFormat()]

