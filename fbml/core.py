"""
.. module: fbml.core 
    :platform: Unix
    :synopsis: The dataflow.module module. This is used for all assosiations.
.. moduleauthor: Christian Gram Kalhauge

"""
from . import model
from .util import exceptions

import os

def build(modulename,env):
    return env.get_module(modulename) 

def read_path(modulename):
    """
    Reads a modulename, and returns a list of module names
    :param modulename: a . seperated list of the module path
    """
    return modulename.split('.')


class Builder (object):

    def __init__(self,paths,parser):
        self._parser = parser
        self._paths = paths
        self.package_environment = PackageEnvironment()
        self._build_modules = set()

    def get_module(self,modulename):
        mod = self.package_environment.get_module_from_name(modulename)
        if not mod in self._build_modules:
            self.build_module(mod)
        return mod

    def parse_module(self,module):
        pars = None
        for path in self._paths:
            try:
                filename = os.path.join(path, self.get_filename(module))
                with open(filename) as moduleFile:
                    pars = self._parser.parse(moduleFile) 
                    break
            except IOError:
                continue
        if pars is None: 
            raise IOError("Module {} not found in paths {}".format(
                module,
                self._paths))
        return pars

    def build_module(self,module):
        pars = self.parse_module(module)
        module.setImports(self.get_module(imp) for imp in pars.imports)
        module.setExtensions(pars.extensions)
        module.setMethods(self.build_methods(pars))

    def build_methods(self,pars):
        methods = dict()
        for p_method in pars.methods:
            method = model.Method(p_method.id)
            method.addRequirements(self.build_requirements(p_method.requirements))
            method.addEnsurances(self.build_ensurances(p_method.ensurances))
            methods[method.getInternalId()] = method
        
        impls = [self.build_impl(impl,methods) for impl in pars.impls]
        return methods.values()
        
    def build_impl(self,p_impl,methods):
        from itertools import chain
        impl = model.Impl(methods[p_impl.method_id])
        sinks = chain.from_iterable((s for s in f.sinks) for f in p_impl.functions)
        sinks = dict((sink.id,self.build_sink(sink)) for sink in sinks)
        args = impl.getMethod().getRequirement('Sources').items()
        sinks.update((sid,model.Sink(sid,slot)) for slot,sid in args)
        impl.addSinks(sinks.values())
        impl.addFunctions(self.build_function(f,sinks) for f in p_impl.functions)
        return impl

    def build_function(self,pFunc,sinks):
        func = model.Function(pFunc.id)
        func.addSinks(sinks[sink.id] for sink in pFunc.sinks)
        func.addSources(self.build_source(source,sinks) for source in pFunc.sources)
        func.setExtensions(self.build_extension(pFunc.extends))
        func.connect()
        return func

    def build_requirements(self,pReqs):
        return (model.Require(req.name,req.data) for req in pReqs) 

    def build_ensurances(self,pEns):
        return (model.Ensure(ens.name,ens.data) for ens in pEns)

    def build_extension(self,pExt):
        return (model.Extend(ens.name,ens.data) for ens in pExt)

    def build_sink(self,sink):
        return model.Sink(sink.id,sink.slot).setExtensions(
                self.build_extension(sink.extends))

    def build_source(self,source,sinks):
        return model.Source(sinks[source.sink_id],source.slot).setExtensions(
                self.build_extension(source.extends))
        
    def get_filename(self,element):
        return self.package_environment.get_filename(element)

    def add_build_module(self,module):
        self._build_modules.add(module)
        return self

class PackageEnvironment(object):
   
    def __init__(self):
        self.root_package = model.RootPackage() 

    def get_filename(self,element):
        return os.path.join(*element.get_name().split('.')) + '.fl'
        
    def get_module_from_name(self,modulename):
        return self.get_module(read_path(modulename))
    
    def get_module(self,module_path):
        return self.get_package(module_path[:-1]).get_module(module_path[-1])

    def get_package(self,module_path):
        if len(module_path) == 0:
            return self.root_package
        else:
            return self.get_package(module_path[:-1]).get_package(module_path[-1])
    


def read_path(modulename):
    """
    Reads a modulename, and returns a list of module names
    :param modulename: a . seperated list of the module path
    """
    return modulename.split('.')



