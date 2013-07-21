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

def compile_to_llvm(module):
    llvm_module = llvmc.Module.new(module.get_name().replace('.','_'))
    
    visitor = MethodCreater(module,llvm_module)
    for method in module.getMethods():
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


#        argnames = list(x.getId() for i,x in enumerate(method.getSources())
#                if not method.getRequirement('Type')[i].isUnreal())
#        argnames.extend(s.getId() for i,s in enumerate(method.getSinks())
#                if not method.getEnsurance('Type')[i].isUnreal()) 
#        
#        for arg,name in zip(function.args,argnames):
#            arg.name = name
#        
#        blok = function.append_basic_block('entry')
#        return llvmc.Builder.new(blok) 
    


class MethodCreater(visitors.ControlFlowVisitor):

    def __init__(self,module,llvm_module):
        super(MethodCreater,self).__init__()
        self._module = module
        self._llvm_module = llvm_module
        
    def setup(self,method):
        return FunctionCodeBuilder(self._llvm_module,method)

    def final(self,method,cb):
        cb.ret_void()
        return cb.getFunction()

    def apply(self,function,cb):
        from ..util.matchers import all_of
        from .methodname import has_method_name, getMethodName
        from .type import has_types, getSourceTypes
        from .sources import has_sources_length
        from .sinks import has_sinks_length
        
        methodname = getMethodName(function)
        types      = getSourceTypes(function)
       
        requirement = all_of(
                        has_method_name(methodname),
                        has_types(enumerate(types)),
                        has_sources_length(len(function.getSources())),
                        has_sinks_length(len(function.getSinks()))
                       )

        methods = self._module.getMethodsWhere(requirement)

        if len(methods) == 0: raise exceptions.NoMethodCall(methods,requirement)
        if len(methods) >  1: raise exceptions.AmbiguousMethodCall(methods,requirement)

        method = methods[0]  
        if method.hasImpl():
            call_func = self.visit(method)
            print(call_func) 
            return cb.call(
                    call_func,
                    function.getSources(),
                    function.getSinks()) 
        else:
            print(method)
            return cb.call_buildin(method.ens('llvm'),
                    function.getSources(),
                    function.getSinks()[0])
                
        return cb 

class LLVMExtension (Extension):
    NAME = 'LLVM'
    XML_FORMAT = LLVMFormat 

