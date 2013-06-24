from .. import xmlformat


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

class Type (object):

    @staticmethod
    def new(name):
        return _types[name]()

    def isUnreal(self):
        return False


class Integer (Type):
    def name(self): return "Integer"

class Real (Type):
    def name(self): return "Real"

class Char (Type):
    def name(self): return "Char"

class Unreal (Type):
    def name(self): return "Unreal"
    def isUnreal(self): return True

_types = {
        'Integer' : Integer,
        'Real' : Real,
        'Char' : Char,
        'Unreal' : Unreal
        }
