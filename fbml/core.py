"""
.. module: fbml.core 
    :platform: Unix
    :synopsis: The dataflow.module module. This is used for all assosiations.
.. moduleauthor: Christian Gram Kalhauge

"""
from . import model
from .util import exceptions

import os

def build(module_name,env):
    return env.get_module(module_name) 


class Builder (object):

    def __init__(self, paths, parser):
        self.root_package = structure.RootPackage(paths)
        self.parser = parser

    def get_module(self, module_name):
        name_list = module_name.split('.')
        def factory(paths):
            if os.path.isfolder(paths[0]): 
                return partial(structure.Package,paths=paths)
            elif os.path.isfile(paths[0]):
                return partial(Builder.build_module,path=paths[0],self=self)
        try:
            return self.root_package.make(name_list,factory)
        except KeyError:
            return structure.Label.from_string(module_name,root_package) 
             

    def build_module(self, path, label):
        """
        Builds a module using the path to the file, and 
        a label. 
        """
        with open(path) as module_file:
            module_tree = self.parser.parse(module_file)
        imports = (self.get_module(mn) for imp in module_tree.imports)
        module = structure.Module(label,imports)
        for method in module_tree.methods:
            module.make_method(method.method_id,self.factory(method,'method'))
        return module

    def build_method(self, tree, label):
        method = model.Method(label)
        method.make_impl(self.factory(tree.impl,'impl'))
        for req in tree.requirements:
            method.req.set(req.name,req.data)
        for ens in tree.ensurances:
            method.ens.set(ens.name,req.data)
        return method

    def build_impl(self, tree, label):
        impl = model.Impl(label)
        for fun in impl.functions:
            self.make_function(fun.function_id,self.factory(fun,'function'))
        return impl

    def build_function(self, tree, label):
        function = model.Function(location)
        for sink in tree.sinks:
            self.make_sink(sink.slot, self.factory(sink,'sink')) 
        for source in function_tree.source:
            self.make_source(source.slot, self.factory(source,'source')) 
        self.assing_extends(tree,function)
        return function
   
    def build_sink(self, tree, label, target):
        sink = model.Sink(label,target)
        self.assing_extends(tree, sink)
        return sink

    def build_source(self, tree, target):
        source = model.Source(label.parrent.impl.get_sink(tree.sink_id),target)
        self.assing_extends(tree,source)
        return source

    def assing_extends(self, tree, obj):
        for ext in tree.extends:
           obj.ext.set(ext.name,ext.data) 

    def factory(self, tree, name):
        return partial(getattr(self,name),tree = tree)

        
        
