from .. import xmlformat
from .. import visitor

import xml.etree.ElementTree as ET

class TypeFormat (xmlformat.XMLExtensionFormat):
    def __init__(self): 
        self.setName('Type')

    def parseRequire(self,tree):
        m = ((int(x.attrib['slot']),Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parseEnsure(self,tree):
        m = ((int(x.attrib['slot']),Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parse(self,tree):
        return Type.new(tree.find('type').text)

    def writeRequireToTree(self,req,tree):
        for slot,type_ in req.items():
            ET.SubElement(tree,'type',{'slot':str(slot)}).text = type_.getName()

    def writeEnsureToTree(self,req,tree):
        for slot,type_ in req.items():
            ET.SubElement(tree,'type',{'slot':str(slot)}).text = type_.getName()

    def writeToTree(self,ext,tree):
        ET.SubElement(tree,'type').text = ext.getName()

class has_types (object):

    def __init__(source_types):
        self.matcher = require('Type',has_entries(source_types)),

    def match(self,match):
        return self.matcher.match(match)

class TypeDistributor (visitor.DataFlowVisitor):

    def setup(self,method):
        for slot,name in method.getRequirements('Sources').items():
            ['Type']
        pass

    def apply(self,function):
        #Determine types
        types = [(source.getSlot(),source.getSink()['Type'])
                    for source in function.getSources()]

        methodName = function['MethodName']
        #Determine method
        modules = module.getMethodsWhere(
                all_of(
                    has_types(types),
                    has_mehtod_name(methodName),
                    has_sources(),
                    has_sinks()
                    )
                )
        function.getSinks()
class Type (object):

    @staticmethod
    def new(name):
        return _types[name]()

    def isUnreal(self):
        return False


class Integer (Type):
    def getName(self): return "Integer"

class Real (Type):
    def getName(self): return "Real"

class Char (Type):
    def getName(self): return "Char"

class Unreal (Type):
    def getName(self): return "Unreal"
    def isUnreal(self): return True

_types = {
        'Integer' : Integer,
        'Real' : Real,
        'Char' : Char,
        'Unreal' : Unreal
        }
