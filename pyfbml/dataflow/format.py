from . import parser


class MethodName (parser.XMLExtensionFormat):
    def __init__(self):
        self.setName(self.__class__.__name__);

class Type (parser.XMLExtensionFormat):
    def __init__(self): 
        self.setName(self.__class__.__name__)

class Sources(parser.XMLExtensionFormat):
    
    def __init__(self): 
        self.setName(self.__class__.__name__)

    def parseRequire(self,tree):
        return dict((int(source.attrib['slot']),source.attrib['id'])
                    for source in tree.findall('source'))


class Sinks(parser.XMLExtensionFormat):
    
    def __init__(self): 
        self.setName(self.__class__.__name__)

    def parseEnsure(self,tree):
        return dict((sink.attrib['id'],sink.attrib['slot']) 
                    for sink in tree.findall('sink'))

        
        
xmlFormats = {
        'Sources' : Sources,
        'Sinks' : Sinks,
        'MethodName' : MethodName,
        'Type' : Type
    }
