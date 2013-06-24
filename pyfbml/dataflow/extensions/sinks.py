from .. import xmlformat 
import xml.etree.ElementTree as ET


class SinksFormat(xmlformat.XMLExtensionFormat):
    
    def __init__(self): 
        self.setName('Sinks')

    def parseEnsure(self,tree):
        return dict((sink.attrib['id'],int(sink.attrib['slot']) )
                    for sink in tree.findall('sink'))

    def writeEnsureToTree(self,ensure,tree):
        tree_ens = ET.SubElement(tree,'ensure',{'name':self.getName()})
        for sid,slot in ensure.items():
            ET.SubElement(tree_ens,'sink',{'slot':str(slot),'id':sid})

        