from . import Extension
from ..parsers import xmlformat
from ..util import matchers


class MethodNameFormat (xmlformat.XMLExtensionFormat):
    def __init__(self):
        self.name = 'method_name'
    
    def parse(self, parser, tree):
        return tree.text

    def write(self, tag, data, tree):
        tree.text = data

class has_method_name (matchers.Matcher):
    
    def __init__(self,method_name):
        self._method_name = method_name

    def _matches(self,method):
        return method.req.method_name == self._method_name 

    def describe_to(self,description):
        description.append('has method name of ')
        description.append(self._method_name)

def get_method_name(function):
    return function['method_name']


class MethodNameExtension (Extension):
    XML_FORMAT = MethodNameFormat()
    NAME = 'method_name'

