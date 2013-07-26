from . import Extension
from ..util import matchers
from ..util import exceptions
from ..parsers import xmlformat 
import xml.etree.ElementTree as ET

class SourcesFormat(xmlformat.XMLExtensionFormat):
    
    def __init__(self): 
        self.name = 'sources'

    def parse_require(self,tree):
        sources_trees = list(tree.findall('source'))
        s_dict =((int(s.attrib['slot']),s.attrib['id']) for s in sources_trees )
        sources = dict(s_dict)
        if not all(i in sources for i in range(len(sources_trees))):
            raise exceptions.MallformedFlowError(
                'Sources in {} not squential : {}'.format(
                    tree.tag,sources)
                )
        return sources


    def write_require_to_tree(self,require,tree):
        for slot,sid in require.items():
            ET.SubElement(tree,'source',{'slot':str(slot),'id':sid})


class has_sources_length (matchers.Matcher):

    def __init__(self,length):
        self._length = length

    def _matches (self,method):
        return self._length == len(method.req.source)

    def describe_to(self,description):
        description.append("has {} number of sources".format(self._length))



class SourcesExtension(Extension):
    NAME = "sources"
    XML_FORMAT = SourcesFormat()
