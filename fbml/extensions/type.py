from . import Extension
from ..util import matchers
from ..util import exceptions
from ..util import visitors
from ..parsers import xmlformat 

import xml.etree.ElementTree as ET

class TypeFormat (xmlformat.XMLExtensionFormat):
    def __init__(self): 
        self.setName('Type')

    def parseRequire(self,tree):
        m = ((int(x.attrib['slot']),Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parseEnsure(self,tree):
        m = ((int(x.attrib['slot']),Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parse(self,tree):
        return Type.new(tree.find('type').text)

    def writeRequireToTree(self,req,tree):
        for slot,type_ in req.items():
            ET.SubElement(tree,'type',{'slot':str(slot)}).text = type_.getName()

    def writeEnsureToTree(self,req,tree):
        for slot,type_ in req.items():
            ET.SubElement(tree,'type',{'slot':str(slot)}).text = type_.getName()

    def writeToTree(self,ext,tree):
        ET.SubElement(tree,'type').text = ext.getName()


def could_be(t,method,i):
    try:
        return isinstance(t,Any) or t.getName() == method.getRequirement('Type')[i].getName() 
    except KeyError:
        return False

class has_types (matchers.Matcher):

    def __init__(self,source_types):
        self.types = source_types

    def _matches(self,method):
        could_be_types = [could_be(t,method,i) for i,t in self.types]
        return all(could_be_types)

    def describe_to(self,description): 
        description.append("has sources matching the pathern {}".format(self.types))

class Type (object):

    @staticmethod
    def new(name):
        return _types[name]()

    def isUnreal(self):
        return False

    def __repr__(self):
        return "<Type {}>".format(self.getName())

class Integer (Type):
    def getName(self): return "Integer"

class Real (Type):
    def getName(self): return "Real"

class Char (Type):
    def getName(self): return "Char"

class Unreal (Type):
    def getName(self): return "Unreal"
    def isUnreal(self): return True

class Any (Unreal):
    def getName(self): return "Any"

_types = {
        'Integer' : Integer,
        'Real' : Real,
        'Char' : Char,
        'Unreal' : Unreal,
        'Any' : Any,
        }


class TypeExtension(Extension):
    NAME = "Type"
    XML_FORMAT = TypeFormat()


class TypeSetter (visitors.DataFlowVisitor):

    def __init__(self,module):
        super(TypeSetter,self).__init__()
        self.module = module

    def setup(self,method):
        from .. import model
        sources = method.getSources()
        impl = method.getImpl()
        new_sources = [model.Sink(s.getId(),s.getSlot()) for s in sources]
        def getType(method,i):
            try:
                return method.getRequirement('Type')[i] 
            except KeyError:
                return Type.new('Any')

        s_types = [getType(method,i) for i in range(len(sources))]

        for i,t in enumerate(s_types):
            new_sources[i]['Type'] = t

        return new_sources

    def merge(self,function,sinks):
        from .. import model
        sinks = list(sinks)
        new_sources = [model.Source(s,i) for i,s in enumerate(sinks)]
        
        for new,old in zip(new_sources,function.getSources()):
            new.setExtensions(old.getExtensions().values())
        
        for source,sink in zip(new_sources,sinks):
            source['Type'] = sink['Type']

        return new_sources

    def apply(self,function,sources):
        from .. import model
        #Determine typesj
        types = [(source.getSlot(),source['Type'])
                    for source in sources]

        methodName = function['MethodName']
        from .methodname import has_method_name
        from .sources import has_sources_length
        from .sinks import has_sinks_length
        #Determine method
        method = self.module.getMethodWhere(
                matchers.all_of(
                    has_types(types),
                    has_method_name(methodName),
                    has_sources_length(len(sources)),
                    has_sinks_length(len(function.getSinks()))
                    )
                )
        
        if not 'Type' in method.getEnsurances(): 
            method = self.visit(method)
        
        new_sinks = [model.Sink(sink.getId(),sink.getSlot()) for sink in function.getSinks()]
        s_types = [method.getEnsurance('Type')[i] for i in range(len(new_sinks))]

        new_function = model.Function(function.getId())
        
        for new,old in zip(new_sinks,function.getSinks()):
            new.setExtensions(old.getExtensions().values())
        
        for i,t in enumerate(s_types):
            new_sinks[i]['Type'] = t
            new_sinks[i].addFunction(new_function)

        for s in sources:
            s.addFunction(new_function)

        new_function.addSources(sources)
        new_function.addSinks(new_sinks)
        new_function.setExtensions(function.getExtensions().values())
        
        return ((sink.getId(),sink) for sink in new_sinks)


    def final(self,method,sinks):
        from .. import model
        new_method = model.Method(method.getInternalId())
        new_method.addEnsurances(method.getEnsurances().values())
        new_method.addRequirements(method.getRequirements().values())

        new_impl = model.Impl(new_method)
        new_impl.addSinks(sinks.values())
        new_impl.addFunctions(visitors.calculateReachableFunctions(sinks.values()))

        sink_types = dict(
                (new_method.getEnsurance('Sinks')[sink.getId()],sink['Type']) 
                    for sink in new_method.getSinks())

        new_method.setEnsurance('Type',sink_types)
        return new_method
