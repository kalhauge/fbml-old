"""
.. module:: pyfbml.dataflow.xmlformat

"""


import xml.etree.ElementTree as ET
import logging

log = logging.getLogger(__name__)

from .. import exceptions
from . import model
from .parser import *

class XMLWriter (object):

    def __init__(self,extendFormats):
        self._extendFormats = extendFormats;

    def write(self,module,filelike):
        e = ET.ElementTree()
        root = ET.Element('fbml',{'version':'0.0'})
        self.writeImportsToTree(module.getImports(),root) 
        self.writeExtensionsToTree(module.getExtensions(),root)
        self.writeMethodsToTree(module.getMethods(),root)
        e._setroot(root)
        e.write(filelike,xml_declaration="1.0",encoding="unicode")
        return e 

    def writeMethodsToTree(self,methods,root):
        for method in methods: self.writeMethodToTree(method,root)

    def writeImportsToTree(self,imports,root):
        for imp in imports: ET.SubElement(root,'import').text = imp.getName()

    def writeExtensionsToTree(self,exts,root):
        for ext in exts: 
            ET.SubElement(root,'extension').text = ext 

    def writeMethodToTree(self,method,root):
        tree_method = ET.SubElement(root,'method',{'id':method.getId()})
       
        self.writeRequirementsToTree(method.getRequirements(),tree_method)
        self.writeEnsurancesToTree(method.getEnsurances(),tree_method)
        self.writeImplToTree(method.getImpl(),root)

    def writeImplToTree(self,impl,root):
        if isinstance(impl,model.NoneImpl): return

        tree_impl = ET.SubElement(root,'impl',{'method_id':impl.getMethod().getId()})
        self.writeFunctionsToTree(impl.getFunctions(),tree_impl)

    def writeFunctionsToTree(self,funcs,root):
        for func in funcs: self.writeFunctionToTree(func,root)

    def writeFunctionToTree(self,func,root):
        tree_func = ET.SubElement(root,'function',{'id':func.getId()})
        self.writeExtendsToTree(func.getExtensions(),tree_func)
        self.writeSourcesToTree(func.getSources(),tree_func)
        self.writeSinksToTree(func.getSinks(),tree_func)

    def writeSourcesToTree(self,sources,root):
        for source in sources: self.writeSourceToTree(source,root)

    def writeSourceToTree(self,source,root):
        elm = ET.SubElement(root,'source')
        elm.set('sink_id',source.getSink().getId())
        elm.set('slot',source.getSlot())
        self.writeExtendsToTree(source.getExtensions(),elm)

    def writeSinksToTree(self,sinks,root):
        for sink in sinks: self.writeSinkToTree(sink,root)

    def writeSinkToTree(self,sink,root):
        elm = ET.SubElement(root,'sink')
        elm.set('id',sink.getId())
        elm.set('slot',sink.getSlot())
        self.writeExtendsToTree(sink.getExtensions(),elm)

    def writeRequirementsToTree(self,reqs,root):
        for req in reqs.values(): self._extendFormats.writeRequireToTree(req,root)

    def writeEnsurancesToTree(self,ens,root):
        for en in ens.values(): self._extendFormats.writeEnsureToTree(en,root)

    def writeExtendsToTree(self,exts,root):
        for ext in exts.values(): self._extendFormats.writeToTree(ext,root)


class XMLParser (object):

    def __init__(self,extendFormats):
        self._extendFormats = extendFormats

    def getExtendFormats(self):
        return self._extendFormats

    def parse(self,filelike):
        return self.parseModule(ET.parse(filelike).getroot())

    def parseModule(self,tree_module):
        module = Module(**tree_module.attrib)
        module.setImports(self._parseAll(tree_module,'import'))
        module.setExtensions(self._parseAll(tree_module,'extension'))
        module.setMethods(self._parseAll(tree_module,'method'))
        module.setImpls(self._parseAll(tree_module,'impl'))
        return module

    def parseMethod(self,tree_method):
        method = Method(**tree_method.attrib)
        method.setRequirements(self._parseAll(tree_method,'require'))
        method.setEnsurances(self._parseAll(tree_method,'ensure')) 
        return method

    def parseImpl(self,tree_impl):
        impl = Impl(**tree_impl.attrib)
        impl.setFunctions(self._parseAll(tree_impl,'function'))
        return impl

    def parseFunction(self,tree_func):
        func = Function(**tree_func.attrib)
        func.setExtends(self._parseAll(tree_func,'extend'))
        func.setSinks(self._parseAll(tree_func,'sink'))
        func.setSources(self._parseAll(tree_func,'source'))
        return func

    def parseRequire(self,tree_require):
        require = Require(**tree_require.attrib);
        self._extendFormats.parseRequire(require,tree_require)
        return require

    def parseEnsure(self,tree_ensure): 
        ensure = Ensure(**tree_ensure.attrib)
        self._extendFormats.parseEnsure(ensure,tree_ensure)
        return ensure

    def parseSink(self,tree_sink):
        sink = Sink(**tree_sink.attrib)
        sink.setExtends(self._parseAll(tree_sink,'extend'))
        return sink

    def parseSource(self,tree_source):
        source = Source(**tree_source.attrib)
        source.setExtends(self._parseAll(tree_source,'extend'))
        return source
        
    def parseExtend(self,tree_extend):
        extend = Extend(**tree_extend.attrib)
        self._extendFormats.parse(extend,tree_extend)
        return extend

    def parseImport(self,tree_import):
        return tree_import.text

    def parseExtension(self,tree_ext):
        return tree_ext.text

    def _parseAll(self,tree,name):
        function = getattr(self,"parse" + name.capitalize())
        return (function(elm) for elm in tree.findall(name))


class XMLExtensionFormats (object):

    def __init__(self,extendFormats={}):
        self._extendFormats = dict(extendFormats)

    def addExtensionFormat(self,eformat):
        self.addExtensionFormat({eformat.getName():eformat})

    def addExtensionFormats(self,formats):
        self._extendFormats.update(formats)

    def getExtendFormat(self,name):
        try: return self._extendFormats[name]
        except KeyError:
            log.warning(
                    'Found name %s, no known extension parser', 
                    name)
            return XMLExtensionFormat().setName(name)

    def parse(self,extend,tree_extend): 
        extend.data = self.getExtendFormat(extend.name).parse(tree_extend)

    def parseRequire(self,require,tree_require):
        require.data = self.getExtendFormat(require.name).parseRequire(tree_require)

    def parseEnsure(self,ensure,tree_ensure):
        ensure.data = self.getExtendFormat(ensure.name).parseEnsure(tree_ensure)

    def writeToTree(self,extend,root):
        self.getExtendFormat(extend.getName())\
                .writeToTree(extend.getData(),root);
    
    def writeRequireToTree(self,extend,root):
        self.getExtendFormat(extend.getName())\
                .writeRequireToTree(extend.getData(),root);
    
    def writeEnsureToTree(self,extend,root):
        self.getExtendFormat(extend.getName())\
                .writeEnsureToTree(extend.getData(),root);

class XMLExtensionFormat (object):

    def setName(self,name):
        self._name = name
        return self

    def getName(self):
        return self._name
    
    def parse(self,tree):
        return tree.text

    def parseRequire(self,tree):
        return tree.text

    def parseEnsure(self,tree):
        return tree.text

    def writeToTree(self,data,tree):
        ET.SubElement(tree,'extend',{'name':self.getName()}).text = str(data)

    def writeEnsureToTree(self,data,tree):
        ET.SubElement(tree,'ensure',{'name':self.getName()}).text = str(data)

    def writeRequireToTree(self,data,tree):
        ET.SubElement(tree,'require',{'name':self.getName()}).text = str(data)

