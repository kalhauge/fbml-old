"""
.. module: fbml.core 
    :platform: Unix
    :synopsis: The dataflow.module module. This is used for all assosiations.
.. moduleauthor: Christian Gram Kalhauge

"""
from . import model
from . import structure
from .util import exceptions

from functools import partial 
import os

class Builder (object):

    def __init__(self, paths, parser):
        self.root_package = structure.RootPackage(paths)
        self.parser = parser

    def get_module(self, module_name):
        name_list = module_name.split('.')
        def factory(paths):
            if os.path.isdir(paths[0]): 
                return partial(structure.Package,paths=paths)
            elif os.path.isfile(paths[0]):
                return partial(self.build_module,path=paths[0])
        try:
            return self.root_package.make_from_name_list(name_list,factory)
        except KeyError:
            return structure.Label.from_string(module_name,self.root_package) 
             

    def build_module(self, label, path):
        """
        Builds a module using the path to the file, and 
        a label. 
        """
        with open(path) as module_file:
            module_tree = self.parser.parse(module_file)
        imports = (self.get_module(imp) for imp in module_tree.imports)
        module = structure.Module(path, label, imports)
        for method in module_tree.methods:
            module.make_method(method.id,self.factory(method,'method'))
        for impl in module_tree.impls:
            method = structure.Label.from_string(impl.method_id,module).get()
            method.make_impl(self.factory(impl,'impl'))
        return module

    def build_method(self, label, tree):
        method = model.Method(label)
        for req in tree.requirements:
            method.req.set(req.name,req.data)
        for ens in tree.ensurances:
            method.ens.set(ens.name,req.data)
        return method

    def build_impl(self, label, tree):
        impl = model.Impl(label)
        for slot, name in impl.label.parrent.req.sources.items():
            impl.make_function(slot,self.build_load_function(name)); 
        functions = []
        for fun in tree.functions:
            functions.append(
                    impl.make_function(fun.id,self.factory(fun,'function'))
                    )
        for function, tree in zip(functions,tree.functions):
            for source in tree.sources:
                function.make_source(source.slot, self.factory(source,'source'))
        return impl

    def build_load_function(self, name):
        def factory(label):
            function = model.Function(label)
            function.req.method_name = "IN"
            sink = function.make_sink(0,name,model.Sink)
        return factory

    def build_function(self, label, tree):
        function = model.Function(label)
        for sink in tree.sinks:
            function.make_sink(sink.slot, sink.id, self.factory(sink,'sink')) 
        self.assing_extends(tree,function)
        return function
   
    def build_sink(self, target, label, tree):
        sink = model.Sink(label,target)
        self.assing_extends(tree, sink)
        return sink

    def build_source(self, target, tree):
        source = model.Source(target.parrent.impl.get_sink(tree.sink_id),target)
        self.assing_extends(tree,source)
        return source

    def assing_extends(self, tree, obj):
        for ext in tree.extends:
           obj.ext.set(ext.name,ext.data) 

    def factory(self, tree, name):
        return partial(getattr(self,'build_'+name),tree = tree)

        
        
