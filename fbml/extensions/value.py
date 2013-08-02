"""
.. module:: fbml.extensions.value
.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

"""

import logging
log = logging.getLogger(__name__)

from . import Extension

class ValueFormat (object):

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

class Value(object):

    def __init__(self, type_, value):
        self.value = value
        self.type = type_

    @classmehtod
    def constant(cls, type_, value): 
        return cls(type_, value) 

    def write(self): 
        return self.type.write_str(self.value)

class ValueVisitor(object):
    pass

class ValueExtension(Extension):
    XML_FORMATS = [ValueFormat]
    NAME = 'value'
