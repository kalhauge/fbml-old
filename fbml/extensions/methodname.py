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
        xmlformat.writer_list('methods', 'id')(writer,value, root)

class MethodFinder(visitors.DataFlowVisitor):

    def __init__(self, module):
        super(MethodFinder, self).__init__()
        self.module = module
        self.methods_by_name = {}
        for method in module.reachable_methods:
            l = self.methods_by_name.setdefault(method.data.method_name, [])
            l.append(method)

    def merge(self, sink, functions):
        return sink

    def apply(self, function, sinks):
        try:
            methods = methods_by_name[function.data.method_name]
            return function.update_data(sinks, [('methods',methods)])
        except KeyError: 
            raise MethodNameNotInScope(function.data.method_name)

    def final(self, method, functions, sinks):
        method.impl = element.Impl.new(sinks[sink] for sink in method.impl.targets)


class MethodNameExtension (Extension):
    XML_FORMATS = [MethodNameFormat(), MethodsFormat()]
    NAME = 'method_name'

