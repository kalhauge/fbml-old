"""
.. module:: fbml.dataflow.parser

"""

import xml.etree.ElementTree as ET
import logging

log = logging.getLogger(__name__)

from .. import exceptions

def getSinks(root):
    sinks = dict();
    for sink_root in root.iter('sink'):
        sink_id = sink_root.attrib['id'];
        if sink_id in sinks: 
            raise exceptions.MallformedFlowError(
                    "{!r} occuring multible times in tag {}".format(
                        sink_id,
                        root.tag)); 
        sinks[sink_id] = model.Sink(sink_id);
    return sinks;

def sortSlotList(slot_list):
    slot_list = list(slot_list)
    l = [None] * len(slot_list);
    for i,s in slot_list:
        s = int(s)
        if s > len(l) or s < 0: 
            raise exceptions.MallformedFlowError(
                    "Slot id is {} should in the range [0,{}[".format(
                        s,len(l))
                    );
        l[s] = i;
    return l;

def parseModule(moduleFile,extendFormats):
    return XMLParser(moduleFile,extendFormats).parse()


class XMLWriter (object):

    def writeMethodToTree(self,method,root):
        tree_method = ET.SubElement(root,'method',{'id':self.getId()})
        
        for i, s in enumerate(method.getSinks()):
            ET.SubElement(tree_method,'sink',{'id':s,'slot':str(i)})
        for i, s in enumerate(method.getSources()):
            ET.SubElement(tree_method,'source',{'id':s,'slot':str(i)})
       
        if method.hasImpl():
            self.writeImplToTree(self,method.getImpl(),root)

    def writeImplToTree(self,impl,root):
        tree_impl = ET.SubElement(root,'impl')
        tree_impl.set('method_id',impl.getMethod().getId())

        for function in impl.getFunctions():
            function.toTree(tree_impl)


class ParseObject(object):
    
    def __init__(self,**kargs):
        for k,v in kargs.items():
            setattr(self,k,v)
        self.check()

    def check(self):
        attributes = self.requriedAttributes()
        for attr in attributes:
            if not hasattr(self,attr):
                raise MallformedFlowError(
                    "{} needs the attribute {}".format(self,attr)
                    )

    def __repr__(self):
        return "<{} attr: {}>".format(self.__class__.__name__,vars(self))


class ExtendableParseObject (ParseObject):

    def setExtends(self,seq):
        self.extends = list(seq)


class Module(ParseObject):

    def requriedAttributes(self): return ['version']

    def setImports(self,seq):
        self.imports = list(seq) 

    def setExtensions(self,seq):
        self.extensions = list(seq)

    def setMethods(self,seq):
        self.methods = list(seq)

    def setImpls(self,seq):
        self.impls = list(seq)

class Method(ParseObject): 

    def requriedAttributes(self): return ['id']

    def setRequirements(self,seq):
        self.requirements = list(seq)

    def setEnsurances(self,seq):
        self.ensurances = list(seq)


class Impl(ParseObject):

    def requriedAttributes(self): return ['method_id']

    def setFunctions(self,seq):
        self.functions = list(seq)


class Extend(ParseObject):

    def requriedAttributes(self): return ['name']


class Function(ExtendableParseObject):
   
    def requriedAttributes(self): return ['id']
    
    def setSinks(self,seq):
        self.sinks = list(seq)

    def setSources(self,seq):
        self.sources = list(seq)


class Sink(ExtendableParseObject):

    def requriedAttributes(self): return ['id','slot']


class Source(ExtendableParseObject): 

    def requriedAttributes(self): return ['sink_id','slot']


class Require(ParseObject):

    def requriedAttributes(self): return ['name']

class Ensure(ParseObject):

    def requriedAttributes(self): return ['name']

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
                    'Found name %s, no known extension parser:', 
                    name)
            return XMLExtensionFormat().setName(name)

    def parse(self,extend,tree_extend): 
        extend.data = self.getExtendFormat(extend.name).parse(tree_extend)

    def parseRequire(self,require,tree_require):
        require.data = self.getExtendFormat(require.name).parseRequire(tree_require)

    def parseEnsure(self,ensure,tree_ensure):
        ensure.data = self.getExtendFormat(ensure.name).parseEnsure(tree_ensure)

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

    def write(self,tree,data):
        ET.SubElement(tree,'extend').text = data

class XMLParser (object):

    def __init__(self,filelike,extendFormats):
        self._moduleTree = ET.parse(filelike).getroot()
        self._extendFormats = extendFormats

    def parse(self):
        return self.parseModule(self._moduleTree)

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
