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
    

class FunctionCodeBuilder(object):

    def __init__(self,llvm_module,method):
        self._llvm_module = llvm_module
        self._vars = dict()
        self.new_function(method)

    def new_function(self,method):
        args_types = self.getArgumentTypes(method)
        ret_types = self.getReturnTypes(method)

        args_types.extend(llvmc.Type.pointer(ret) for ret in ret_types)
      
        self._function = llvmc.Function.new(
                self._llvm_module,
                llvmc.Type.function(llvmc.Type.void(),list(args_types)),
                method.getInternalId()
                )
        argnames = list(x.getId() for i,x in enumerate(method.getSources())
                if not method.getRequirement('Type')[i].isUnreal())
        argnames.extend(s.getId() for i,s in enumerate(method.getSinks())
                if not method.getEnsurance('Type')[i].isUnreal()) 
        
        for arg,name in zip(self._function.args,argnames):
            arg.name = name
            self.setVar(name,arg)
        
        blok = self._function.append_basic_block('entry')
        self._bldr = llvmc.Builder.new(blok) 
        return self 

    def getFunction(self):
        return self._function

    def call_buildin(self,name,srcs,sink):
        print(name,srcs,sink)
        arg = (
                self.getVar(srcs[0].getSink().getId()),
                self.getVar(srcs[1].getSink().getId()),
                sink.getId()
                )
        print(arg)
        var = getattr(self._bldr,name)(*arg)
        if var.name != sink.getId():
            print(var.name,sink.getId())
            #Variable already exists
            self._bldr.store(var,self.getVar(sink.getId()))
        else: self.setVar(sink.getId(),var)
        print("Done")
        return self

    def call(self,function,srcs,sinks):
        args = list(get_llvm_types(srcs))
        args.extend(get_llvm_types(sinks))
        print(function,args)
        self._bldr.call(function,args)
        return self

    def getArgumentTypes(self,method):
        return list(llvm_types(
                method.req('Type')[i] 
                    for i,s in enumerate(method.getSources())
                ))

    def getReturnTypes(self,method):
        return llvm_types(
                method.ens('Type')[i] 
                    for i,s in enumerate(method.getSinks())
                )


    def ret_void(self):
        self._bldr.ret_void()
        return self

    def getVar(self,name):
        return self._vars[name]

    def setVar(self,name,var):
        self._vars[name] = var
        return self


    def new_function(self,method):
        args_types = self.getArgumentTypes(method)
        ret_types = self.getReturnTypes(method)

        args_types.extend(llvmc.Type.pointer(ret) for ret in ret_types)
      
        self._function = llvmc.Function.new(
                self._llvm_module,
                llvmc.Type.function(llvmc.Type.void(),list(args_types)),
                method.getInternalId()
                )
        argnames = list(x.getId() for i,x in enumerate(method.getSources())
                if not method.getRequirement('Type')[i].isUnreal())
        argnames.extend(s.getId() for i,s in enumerate(method.getSinks())
                if not method.getEnsurance('Type')[i].isUnreal()) 
        
        for arg,name in zip(self._function.args,argnames):
            arg.name = name
            self.setVar(name,arg)
        
        blok = self._function.append_basic_block('entry')
        self._bldr = llvmc.Builder.new(blok) 
        return self 

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
        for slot_id, slot in self.method.req.sources.items():
            types[self.source_index[slot_id]] = llvm_type(slot.extends.type)
        for slot_id, slot in self.method.ens.targets.items():
            types[self.target_index[slot_id]] = \
                    llvmc.Type.pointer(llvm_type(slot.extends.type))
        return types


    def _index_map(self, slots, start= 0):
        indices = enumerate(slots) 
        return dict((slot_id,index + start) for index,slot_id in indices )

    def _setup(self):
        self.source_index = self._index_map(self.method.req.sources)
        self.target_index = self._index_map(self.method.ens.targets,
            len(self.method.req.sources))
        
        args_types = self._get_types()

        self.llvm_function = llvmc.Function.new(
                self.llvm_module,
                llvmc.Type.function(llvmc.Type.void(),args_types),
                self.method.label.name
                )
       
        for sink, slot_id in self.method.sources.items():
            index = self.source_index[slot_id]
            arg = self.llvm_function.args[index]
            arg.name = sink.label.name
            self.var[sink] = arg

        for sink, slot_id in self.method.targets.items():
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
        buildin_function = getattr(self.bldr, method.ens.llvm)

        args = [None, None, list(function.targets)[0].label.name]

        for sink, slot_id in function.source_slots.items():
            slot = method.req.sources[slot_id]
            args[slot.extends.llvm_arg] = self.var[sink]
    
        var = buildin_function(*args)
        log.debug("Got %r from %s",var,args[2])
        if var.name != args[2]:
            log.debug("REACHED TARGET")
             #Variable already exists
            self.bldr.store(var,self.var[list(function.targets)[0]])
        else: 
            self.var[list(function.targets)[0]] = var
        log.debug(self.var)
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
        
        method_name = function.ext.method_name
        types = [(slot,sink.ext.type) 
                for sink, slot in function.source_slots.items()]
       
        requirement = all_of(
                        has_method_name(method_name),
                        has_types(types),
                        has_sources(function.source_slots.values()),
                        has_targets(function.slot_targets)
                       )

        method = self._module.get_method_where(requirement)

        return cb.call_buildin(method,function)
        

class LLVMExtension (Extension):
    NAME = 'llvm'
    XML_FORMATS = [LLVMFormat(),LLVMArgFormat()]

