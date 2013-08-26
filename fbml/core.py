"""
.. currentmodule: fbml.core 
    :platform: Unix
    :synopsis: The dataflow.module module. This is used for all assosiations.
.. moduleauthor: Christian Gram Kalhauge

"""
from functools import partial 
from itertools import chain, starmap
from collections import deque

import os
import sys

import logging
log = logging.getLogger(__name__)

from . import element
from . import util
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
            method.impl = self.build_impl(method,impl)
        return module

    def build_method(self, label, tree):
        method = model.Method(label)
        method.make_condition('req',self.factory(tree.require,'condition'))
        method.make_condition('ens',self.factory(tree.ensure,'condition'))
        return method
    
    def build_condition(self, label, tree):
        condition = model.Condition(label)
        for slot in tree.slots:
            def build_slot(label):
                return util.namedtuple_from_dict('Slot', slot.data)
            condition.make_slot(slot.id, build_slot)
        self.assing_extends(tree,condition)
        return condition


    def build_impl(self, method, tree):
        start_sinks = dict(
                map (
                    lambda x: (x.data.id,x), 
                    chain(
                        map(partial(self.build_source_sink,method),tree.sources), 
                        map(self.build_constant_sink, tree.constants)
                        )
                    )
                )
        sinks = dict(start_sinks)
        functions = dict()
        sink_builders = {s.data['id'] : partial(self.build_internal_sink,s.data)
                for s in tree.sinks}

        sink_builders.update((s.id,
            partial(self.build_target_sink,
                dict(
                    chain(
                        vars(method.ens.slots[s.slot]).items(),
                        (('id',s.id),('slot',s.slot))
                        )
                    )
            )) for s in tree.targets)

        function_descriptions, next_functions = [], list(tree.functions)
        while next_functions:
            function_descriptions, next_functions = next_functions, []
            improved = False
            for fun in function_descriptions:
                function = self.build_function(sinks,fun)
                if function:
                    functions[fun.data['id']] = function
                    try:
                        targets = [ sink_builders[target.sink](function, target.slot)
                                for target in fun.targets]
                    except KeyError as e:
                        raise exceptions.MallformedFlowError(
                                'Could not find {e} in sinks'.format(**locals()))
                    sinks.update((x.data.id, x) for x in targets)
                    improved = True
                else:
                    next_functions.append(fun)
            if not improved:
                raise Exception("Bad formatted fbml: functions missing sinks {}".format(
                        list(map(lambda x : x.data['id'],
                             next_functions))))
    
        target_sinks = {target.slot: sinks[target.id] for target in tree.targets }

        return element.Impl.new(target_sinks)

    def build_function(self, sinks, tree):
        try: 
            sources = {s.slot : sinks[s.sink] for s in tree.sources}
        except KeyError as e:
            return None
        else:
            return element.Function.new(sources,tree.data)
        
    def build_internal_sink(self, data, function, slot):
        return element.Internal.new(element.Target(function,slot), data)

    def build_target_sink(self, data, function, slot):
        return element.Sink.new(element.Target(function,slot), data)

    def build_source_sink(self, method, tree):
        return element.Source.new(tree.slot,
                dict(
                    chain(
                        vars(method.req.slots[tree.slot]).items(),
                        [('id',tree.id),('slot',tree.slot)]
                        )
                    )
                )

    def build_constant_sink(self, tree):
        return element.Constant.new(tree.data)

    def factory(self, tree, name):
        return partial(getattr(self,'build_'+name),tree = tree)

    def assing_extends(self, tree, obj):
        obj.data = util.namedtuple_from_dict("Data", tree.data)
        return obj
