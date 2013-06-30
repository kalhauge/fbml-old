from . import Extension
from ..parsers import xmlformat
from ..util import matchers


class MethodNameFormat (xmlformat.XMLExtensionFormat):
    def __init__(self):
        self.setName('MethodName');

class has_method_name (matchers.Matcher):
    
    def __init__(self,method_name):
        self._method_name = method_name

    def _matches(self,method):
        return method.getRequirement('MethodName') == self._method_name

    def describe_to(self,description):
        description.append('has method name of ')
        description.append(self._method_name)


class MethodNameExtension (Extension):
    XML_FORMAT = MethodNameFormat()
    NAME = 'MethodName'
