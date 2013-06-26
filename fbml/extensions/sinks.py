from . import Extension
from ..util import matchers
from ..util import exceptions
from ..parsers import xmlformat 
import xml.etree.ElementTree as ET

class SinksFormat(xmlformat.XMLExtensionFormat):
    
    def __init__(self): 
        self.setName('Sinks')

    def parseEnsure(self,tree):
        sinks_trees = list(tree.findall('sink'))
        s_dict =((s.attrib['id'],int(s.attrib['slot'])) for s in sinks_trees )
        sinks = dict(s_dict)
        test = set(range(len(sinks_trees))) 
        if not all(i in test for i in sinks.values()):
            raise exceptions.MallformedFlowError(
                'Sinks in {} not squential : {}'.format(
                    tree.tag,sinks)
                )
        return sinks


    def writeEnsureToTree(self,ensure,tree):
        for sid,slot in ensure.items():
            ET.SubElement(tree,'sink',{'slot':str(slot),'id':sid})


class has_sinks_length (matchers.Matcher):

    def __init__(self,length):
        self._length = length

    def match (self,method):
        return self._length == len(method.getSinks())

class SinksExtension(Extension):
    NAME = "Sinks"
    XML_FORMAT = SinksFormat()
