from . import Extension
from ..util import matchers
from ..util import exceptions
from ..parsers import xmlformat 
import xml.etree.ElementTree as ET

class SourcesFormat(xmlformat.XMLExtensionFormat):
    
    def __init__(self): 
        self.name = 'sources'

    def parse(self, tag, tree):
        if tag != 'require':
            raise exceptions.MallformedFlowError('Sources can only be in requiments, found')

        sources_trees = list(tree.findall('source'))
        s_dict =((s.attrib['slot'],s.attrib['id']) for s in sources_trees )
        sources = dict(s_dict)
        return sources

    def write(self, tag, require, tree):
        for slot,sid in require.items():
            ET.SubElement(tree,'source',{'slot':str(slot),'id':sid})


class has_sources_length (matchers.Matcher):

    def __init__(self,length):
        self._length = length

    def _matches (self,method):
        return self._length == len(method.req.sources)

    def describe_to(self,description):
        description.append("has {} number of sources".format(self._length))


class SourcesExtension(Extension):
    NAME = "sources"
    XML_FORMAT = SourcesFormat()
