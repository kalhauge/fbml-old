from . import Extension
from ..parsers import xmlformat
from ..util import matchers

import xml.etree.ElementTree as ET

class MethodNameFormat (object):
    name = 'method_name'
    
    def parse(self, parser, tree):
        return tree.text

    def write(self, tag, data, tree):
        method_name = ET.SubElement(tree,'method_name').text = data

class has_method_name (matchers.Matcher):
    
    def __init__(self,method_name):
        self._method_name = method_name

    def _matches(self,method):
        return method.req.data.method_name == self._method_name 

    def describe_to(self,description):
        description.append('has method name of "')
        description.append(self._method_name)
        description.append('"')

def get_method_name(function):
    return function['method_name']


class MethodNameExtension (Extension):
    XML_FORMATS = [MethodNameFormat()]
    NAME = 'method_name'

