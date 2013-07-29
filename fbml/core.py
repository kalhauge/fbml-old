"""
.. module: fbml.core 
    :platform: Unix
    :synopsis: The dataflow.module module. This is used for all assosiations.
.. moduleauthor: Christian Gram Kalhauge

"""
from functools import partial 
import os
import sys
import logging
log = logging.getLogger(__name__)

from . import model
from . import structure
from .util import exceptions



class Builder (object):

    def __init__(self, root_package, parser):
        self.root_package = root_package 
        self.parser = parser

    def label_from_string(self,string):
        return structure.Label.from_string(string,self.root_package,self.package_factory)

    def get_module(self, module_name):
        return self.label_from_string(module_name).get()
             
    def package_factory(self,label):
        parrent = label.parrent
        
        paths = list(parrent.get_paths_from_name(label.name))
        if not paths:
            log.error("No paths for name %s in %s",
                    label.name,
                    label.parrent.paths)
            sys.exit(-1)
        if os.path.isdir(paths[0]): 
            return structure.Package(label,paths)
        elif os.path.isfile(paths[0]):
            return self.build_module(label,paths[0])

    def build_module(self, label, path):
        """
        Builds a module using the path to the file, and 
        a label. 
        """
        import pdb; pdb.set_trace()
        with open(path) as module_file:
            module_tree = self.parser.parse(module_file)
        imports = (self.get_module(imp) for imp in module_tree.imports)
        module = structure.Module(path, label, imports)
        for method in module_tree.methods:
            module.make_method(method.id,self.factory(method,'method'))
        for impl in module_tree.impls:
            method = module.find(impl.method_id)
            method.make_impl(self.factory(impl,'impl'))
        return module

    def build_method(self, label, tree):
        method = model.Method(label)
        for req in tree.requirements:
            method.req.set(req.name,req.data)
        for ens in tree.ensurances:
            method.ens.set(ens.name,ens.data)
        return method

    def build_impl(self, label, tree):
        impl = model.Impl(label)
        for slot, name in impl.method.req.sources.items():
            impl.make_function('f_load_' + str(slot),self.build_load_function(name)); 
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
            function.ext.method_name = name
            sink = function.make_sink('output',name,model.Sink)
            return function
        return factory

    def build_function(self, label, tree):
        function = model.Function(label)
        for sink in tree.sinks:
            function.make_sink(sink.slot, sink.id, self.factory(sink,'sink')) 
        self.assing_extends(tree,function)
        return function
   
    def build_sink(self, label, target, tree):
        sink = model.Sink(label,target)
        self.assing_extends(tree, sink)
        return sink

    def build_source(self, target, tree):
        source = model.Source(target.parrent.impl.sinks[tree.sink_id],target)
        self.assing_extends(tree,source)
        return source

    def assing_extends(self, tree, obj):
        for ext in tree.extends:
           obj.ext.set(ext.name,ext.data) 

    def factory(self, tree, name):
        return partial(getattr(self,'build_'+name),tree = tree)

        
        
