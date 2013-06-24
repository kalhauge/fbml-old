from .. import xmlformat


class TypeFormat (xmlformat.XMLExtensionFormat):
    def __init__(self): 
        self.setName('Type')

    def parseRequire(self,tree):
        return dict((type_.attrib['id'],type_.text) for type_ in tree.findall('type'))    
    def parseEnsure(self,tree):
        return dict((type_.attrib['id'],type_.text) for type_ in tree.findall('type'))
