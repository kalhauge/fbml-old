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
    return env.getModule(modulename) 

def readPath(modulename):
    """
    Reads a modulename, and returns a list of module names
    :param modulename: a . seperated list of the module path
    """
    return modulename.split('.')


class Builder (object):

    def __init__(self,paths,parser):
        self._parser = parser
        self._paths = paths
        self._packageEnvironment = PackageEnvironment()
        self._buildModules = set()

    def getModule(self,modulename):
        mod = self.getPackageEnvironment().getModuleFromName(modulename)
        if not mod in self._buildModules:
            self.buildModule(mod)
        return mod

    def parseModule(self,module):
        pars = None
        for path in self._paths:
            try:
                filename = os.path.join(path, self.getFilename(module))
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

    def buildModule(self,module):
        pars = self.parseModule(module)
        module.setImports(self.getModule(imp) for imp in pars.imports)
        module.setExtensions(pars.extensions)
        module.setMethods(self.buildMethods(pars))

    def buildMethods(self,pars):
        methods = dict()
        for pMethod in pars.methods:
            method = model.Method(pMethod.id)
            method.addRequirements(self.buildRequirements(pMethod.requirements))
            method.addEnsurances(self.buildEnsurances(pMethod.ensurances))
            methods[method.getId()] = method
        
        impls = [self.buildImpl(impl,methods) for impl in pars.impls]
        return methods.values()
        
    def buildImpl(self,pImpl,methods):
        from itertools import chain
        impl = model.Impl(methods[pImpl.method_id])
        sinks = chain.from_iterable((s for s in f.sinks) for f in pImpl.functions)
        sinks = dict((sink.id,self.buildSink(sink)) for sink in sinks)
        args = impl.getMethod().getRequirement('Sources').items()
        sinks.update((sid,model.Sink(sid,slot)) for slot,sid in args)
        impl.addSinks(sinks.values())
        impl.addFunctions(self.buildFunction(f,sinks) for f in pImpl.functions)
        return impl

    def buildFunction(self,pFunc,sinks):
        func = model.Function(pFunc.id)
        func.addSinks(sinks[sink.id] for sink in pFunc.sinks)
        func.addSources(self.buildSource(source,sinks) for source in pFunc.sources)
        func.setExtensions(self.buildExtensions(pFunc.extends))
        func.connect()
        return func

    def buildRequirements(self,pReqs):
        return (model.Require(req.name,req.data) for req in pReqs) 

    def buildEnsurances(self,pEns):
        return (model.Ensure(ens.name,ens.data) for ens in pEns)

    def buildExtensions(self,pExt):
        return (model.Extend(ens.name,ens.data) for ens in pExt)

    def buildSink(self,sink):
        return model.Sink(sink.id,sink.slot).setExtensions(
                self.buildExtensions(sink.extends))

    def buildSource(self,source,sinks):
        return model.Source(sinks[source.sink_id],source.slot).setExtensions(
                self.buildExtensions(source.extends))
        
    def getFilename(self,element):
        return self.getPackageEnvironment().getFilename(element)

    def getPackageEnvironment(self):
        return self._packageEnvironment

    def addBuildModule(self,module):
        self._buildModules.add(module)
        return self

class PackageEnvironment(object):
   
    def __init__(self):
        self._rootPackage = model.RootPackage() 

    def getFilename(self,element):
        return os.path.join(*element.getName().split('.')) + '.fl'
        
    def getModuleFromName(self,modulename):
        return self.getModule(readPath(modulename))
    
    def getModule(self,module_path):
        return self.getPackage(module_path[:-1]).getModule(module_path[-1])

    def getPackage(self,module_path):
        if len(module_path) == 0:
            return self.getRootPackage()
        else:
            return self.getPackage(module_path[:-1]).getPackage(module_path[-1])
    
    def getRootPackage(self):
        return self._rootPackage


def readPath(modulename):
    """
    Reads a modulename, and returns a list of module names
    :param modulename: a . seperated list of the module path
    """
    return modulename.split('.')



