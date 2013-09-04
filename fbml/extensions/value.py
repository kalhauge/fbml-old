"""
.. currentmodule:: fbml.extensions.value
.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

"""

import logging
log = logging.getLogger(__name__)


from . import Extension

from ..util import visitors

class ValueFormat (object):
    name = 'value'

    def parse(self, parser, tree):
        return ValueFactory(tree.text)

    def write(self, writer, value, root):
        ET.SubElement(root,'type').text = value.write() 

class ValueFactory(object):

    def __init__(self, str_value):
        self.str_value = str_value

    def get_value(self, type_):
        return Value.constant(type_, type_.parse_str(self.str_value))

    def write(self):
        return self.str_value

    def build(self,data):
        return self.get_value(data.type)
        
        
class Value(object):

    def __init__(self, type_, value):
        self.value = value
        self.type = type_

    @classmethod
    def constant(cls, type_, value): 
        return cls(type_, value) 

    def write(self): 
        return self.type.write_str(self.value)

class ValueFinder(visitors.DataFlowVisitor):

    def __init__(self, module):
        self.module = module

    def setup(self, sink, impl):
        if hasattr(sink.data, 'value'):
            if isinstance(sink.data.value, ValueFactory):
                return sink.update_data({'value': 
                    sink.data.value.get_value(sink.data.type)})
        return sink

    def merge(self, sink, function):
        return sink.update_data(function)

    def apply(self, function, sinks):
        return function.update_data(sinks)

    def final(self, impl, functions, sinks):
        return impl.update_data(sinks)

class ValueExtension(Extension):
    XML_FORMATS = [ValueFormat()]
    NAME = 'value'
