from . import Extension
from ..util import matchers
from ..util import exceptions
from ..parsers import xmlformat 
import xml.etree.ElementTree as ET

class SinksFormat(xmlformat.XMLExtensionFormat):
    
    def __init__(self): 
        self.name = 'sinks'

    def parse(self, tag, tree):
        if tag != 'ensure':
            raise exceptions.MallformedFlowError('Sinks can only be in ensurances')
        sinks_trees = list(tree.findall('sink'))
        s_dict =((s.attrib['id'],int(s.attrib['slot'])) for s in sinks_trees )
        sinks = dict(s_dict)
        test = set(range(len(sinks_trees))) 
        return sinks


    def write(self, tag, ensure, tree):
        for sid,slot in ensure.items():
            ET.SubElement(tree,'sink',{'slot':str(slot),'id':sid})


class has_sinks_length (matchers.Matcher):

    def __init__(self,length):
        self._length = length

    def _matches (self,method):
        return self._length == len(method.ens.sinks)

    def describe_to(self,description):
        description.append("has {} number of sinks".format(self._length))

class SinksExtension(Extension):
    NAME = "sinks"
    XML_FORMAT = SinksFormat()
