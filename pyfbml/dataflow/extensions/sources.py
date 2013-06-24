from .. import xmlformat 
import xml.etree.ElementTree as ET

class SourcesFormat(xmlformat.XMLExtensionFormat):
    
    def __init__(self): 
        self.setName('Sources')

    def parseRequire(self,tree):
        return dict((int(source.attrib['slot']),source.attrib['id'])
                    for source in tree.findall('source'))

    def writeRequireToTree(self,require,tree):
        tree_req = ET.SubElement(tree,'require',{'name':self.getName()})
        for slot,sid in require.items():
            ET.SubElement(tree_req,'source',{'slot':str(slot),'id':sid})

