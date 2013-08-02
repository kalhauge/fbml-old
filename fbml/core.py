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

    def get_module_from_file(self, module_file, name='main', path = None):
        return self.root_package.make(name,
                lambda label: self.build_module(label,module_file,path))
                 
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
            with open(paths[0]) as module_file:
                return self.build_module(label,module_file, paths[0])

    def build_module(self, label, module_file, path):
        """
        Builds a module using the path to the file, and 
        a label. 
        """
        module_tree = self.parser.parse(module_file)
        imports = (self.get_module(imp) for imp in module_tree.imports)
        module = structure.Module(path, label, imports)
        for method in module_tree.methods:
            module.make_method(method.id,self.factory(method,'method'))
        for impl in module_tree.impls:
            method = module[impl.method_id]
            method.make_impl(self.factory(impl,'impl'))
        return module

    def build_method(self, label, tree):
        method = model.Method(label)
        method.make_condition('req',self.factory(tree.require,'condition'))
        method.make_condition('ens',self.factory(tree.ensure,'condition'))
        return method
    
    def build_condition(self, label, tree):
        condition = model.Condition(label)
        for slot in tree.slots:
            condition.make_slot(slot.id, 
                    lambda label: self.assing_extends(slot,model.Data()))
        self.assing_extends(tree,condition.data)
        return condition

    def build_impl(self, label, tree):
        impl = model.Impl(label)
        for sink in tree.sinks:
            impl.make_internal_sink(sink.id,self.factory(sink,'internal_sink'))
        for constant in tree.constants: 
            impl.make_constant_sink(constant.id,self.factory(constant,'constant_sink'))
        for remote in tree.targets:
            impl.make_target_sink(remote.id,remote.slot,self.factory(remote,'target_sink'))
        for remote in tree.sources:
            impl.make_source_sink(remote.id,remote.slot, self.factory(remote,'source_sink'))
        for function in tree.functions:
            impl.make_function(function.id,self.factory(function,'function'))
        return impl

    def build_function(self, label, tree):
        function = model.Function(label)
        for map_ in tree.sources:
            sink = function.impl.sinks[map_.sink]
            function.make_source(map_.slot,function.impl.sinks[map_.sink])
        for map_ in tree.targets:
            function.make_target(map_.slot,function.impl.sinks[map_.sink])
        self.assing_extends(tree,function.data)
        return function

    def build_target_sink(self, target_label, label, tree):
        sink = model.Sink(label)
        sink.data = sink.impl.method.ens.slots[tree.slot]
        return sink

    def build_source_sink(self, source_label, label, tree):
        sink = model.Sink(label)
        sink.data = sink.impl.method.req.slots[tree.slot]
        sink.target = source_label 
        return sink

    def build_constant_sink(self, constant_label, label, tree):
        sink = model.Sink(label)
        sink.target = constant_label 
        self.assing_extends(tree, sink.data)
        return sink

    def build_internal_sink(self, internal_label, label, tree):
        sink = model.Sink(label)
        self.assing_extends(tree, sink.data)
        return sink

    def factory(self, tree, name):
        return partial(getattr(self,'build_'+name),tree = tree)

    def assing_extends(self, tree, obj):
        for name, data in vars(tree.data).items():
            setattr(obj,name,data)
            try:
                data.build(obj)
            except AttributeError: 
                # Build is not required
                pass
        return obj
