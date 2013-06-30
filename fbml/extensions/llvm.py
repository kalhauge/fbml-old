"""
.. module:: fbml.extensions.llvm

"""

from . import Extension

from ..parsers import xmlformat
from ..util import visitors

import llvm.core as llvmc
import llvm.ee as llvmee


class LLVMFormat(xmlformat.XMLExtensionFormat):

    def __init__(self):
        self.setName('LLVM')


type_map = {
        'Integer':llvmc.Type.int(),
        'Real':llvmc.Type.double(),
        'Char':llvmc.Type.int(8)
        }

def llvm_types(fbml_type):
    for t in fbml_type: 
        if not t.isUnreal(): 
            yield type_map[t.getName()]

def compileToLLVM(module):
    llvm_module = llvmc.Module.new(module.getName().replace('.','_'))
    
    visitor = LLVMMethodCreater(module,llvm_module)
    for method in module.getMethods():
        result = visitor.visit(method)

    return llvm_module


class LLVMMethodCreater(visitors.DataFlowVisitor):

    def __init__(self,module):
        self._module = module

    def setup(self,method):
        pass



class LLVMMethodCreaterOld(visitors.ControlFlowVisitor):

    def __init__(self,module,llvm_module):
        super(LLVMMethodCreater,self).__init__()
        self._module = module
        self._llvm_module = llvm_module

    def setup(self,method):
        impl = method.getImpl()
        args_types = list(llvm_types(
                method.getRequirement('Type')[i] 
                    for i,s in enumerate(method.getSources())
                ))
        ret_types =  llvm_types(
                method.getEnsurance('Type')[i] 
                    for i,s in enumerate(method.getSinks())
                )

        args_types.extend(llvmc.Type.pointer(ret) for ret in ret_types)
        
        function = llvmc.Function.new(
                self._llvm_module,
                llvmc.Type.function(llvmc.Type.void(),list(args_types)),
                method.getInternalId()
                )
        
        argnames = list(x.getId() for i,x in enumerate(method.getSources())
                if not method.getRequirement('Type')[i].isUnreal())
        argnames.extend(s.getId() for i,s in enumerate(method.getSinks())
                if not method.getEnsurance('Type')[i].isUnreal()) 
        
        for arg,name in zip(function.args,argnames):
            arg.name = name
        
        blok = function.append_basic_block('entry')
        return llvmc.Builder.new(blok) 

    def final(self,bldr):
        bldr.ret_void()
        return bldr

    def apply(self,function,bldr):
        from ..util.matchers import all_of
        from .methodname import has_method_name
        from .type import has_types
        from .sources import has_sources_length
        from .sinks import has_sinks_length
        
        methodname = function['MethodName']

        if methodname == "Constant":
           sink = function.getSinks()[0]
           rst = llvmc.Constant.int(llvmc.Type.int(),42)
           self.set(sink,rst)
        else:
            types = [(i,s['Type']) for i,s in enumerate(function.getSources())]
            method = self._module.getMethodWhere(
                    all_of(
                        has_method_name(methodname),
                        has_types(types),
                        has_sources_length(len(function.getSources())),
                        has_sinks_length(len(function.getSinks()))
                        )
                    )
                    
            if method.hasImpl():
                required = self.visit(method)
                print("Found thing",required)
            else:
                llvm_func = method.getEnsurance('llvm')
                
                if llvm_func == "print": return bldr
                srcs = [s.getSink().getId() for s in function.getSources() ]
                sink = function.getSinks()[0] 
                rst = getattr(bldr,llvm_func)(srcs[0],srcs[1],sink.getId())
                
                if sink in method.getSinks():
                    bldr.store(rst,sink.getId())

                
        return bldr 

class LLVMExtension (Extension):
    NAME = 'LLVM'
    XML_FORMAT = LLVMFormat 

