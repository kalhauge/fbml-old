
from ..structure import Label
from . import Extension
from ..util import visitors
from ..parsers import xmlformat
from ..util import matchers
from ..util import exceptions
from .. import element

import xml.etree.ElementTree as ET

class MethodNameNotInScope(exceptions.FbmlError):
    def __init__(self, name):
        super(MethodNameNotInScope, self).__init__(
            'Method name {name} not found in scope'.format(**locals())
            )

class SourcesNotInMethods(exceptions.FbmlError):
    def __init__(self, function, methods):
        slots = tuple(vars(function.sources))
        super(SourcesNotInMethods, self).__init__(
            'Sources {slots} not found in {methods}'.format(**locals())
            )


class TargetNotInEnsurances(exceptions.FbmlError):
    def __init__(self, sink, method):
        super(TargetNotInEnsurances, self).__init__(
            'Target {sink.slot} not found in {method}'.format(**locals())
            )

class MethodWithoutMethodName(exceptions.FbmlError):
    def __init__(self, method):
        super(MethodWithoutMethodName, self).__init__(
            'Method {method} has no method_name in requirements {method.req.data}'
            .format(**locals())
            )


class MethodNameFormat (object):
    name = 'method_name'
    
    def parse(self, parser, tree):
        return tree.text

    def write(self, tag, data, tree):
        method_name = ET.SubElement(tree,'method_name').text = data

class MethodsFormat(object):
    name = 'methods'

    def parse(self, parser, tree):
        return parser.parse_objects(tree, 'id')

    def write(self, writer, value, root):
        xmlformat.write_list('methods', 'id')(writer,value, root)

def is_sources_in_method(function, method):
    return all(slot in method.req.slots for slot in vars(function.sources))

def is_target_in_method(sink, method):
    return sink.target.slot in method.ens.slots

def generate_find_method_calls(module):
    method_finder = MethodFinder(module)
    visited_impls = {}
    def find_method_calls(method):
        if not method.impl in visited_impls:
            visited_impls[method.impl] = method_finder.visit(method.impl)
        method.impl = visited_impls[method.impl]
        return method
    return find_method_calls

class MethodFinder(visitors.DataFlowVisitor):

    def __init__(self, module):
        self.module = module
        self.methods_by_name = {}
        for method in module.reachable_methods:
            try:
                l = self.methods_by_name.setdefault(method.req.data.method_name, [])
            except AttributeError as e:
                raise MethodWithoutMethodName(method)
            else: l.append(method)

    def setup(self, sink, impl):
        return sink

    def merge(self, sink, function):
        for method_label in function.data.methods:
            method = Label.find(method_label,self.module)
            if not is_target_in_method(sink, method):
                raise TargetNotInEnsurances(sink, method) 
        return sink.update_data(function,[])

    def apply(self, function, sinks):
        try:
            methods_with_name = self.methods_by_name[function.data.method_name]
        except KeyError: 
            raise MethodNameNotInScope(function.data.method_name)
        else:
            methods = tuple(repr(method.label) for method in methods_with_name 
                            if is_sources_in_method(function, method))
            if not methods:
                raise SourcesNotInMethods(function,methods_with_name)
            return function.update_data(sinks, {'methods':methods})

    def final(self, impl, functions, sinks):
        return element.Impl.new({slot: sinks[sink] for slot, sink in vars(impl.targets).items()})


class MethodNameExtension (Extension):
    XML_FORMATS = [MethodNameFormat(), MethodsFormat()]
    NAME = 'method_name'

