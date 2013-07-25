from . import Extension
from ..util import matchers
from ..util import exceptions
from ..util import visitors
from ..parsers import xmlformat 

import xml.etree.ElementTree as ET


def get_source_types(function):
    return [s['Type'] for s in function.get_sources()]

class TypeFormat (xmlformat.XMLExtensionFormat):
    def __init__(self): 
        self.name = 'Type'

    def parse_require(self,tree):
        m = ((int(x.attrib['slot']),Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parse_ensure(self,tree):
        m = ((int(x.attrib['slot']),Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parse(self,tree):
        return Type.new(tree.find('type').text)

    def write_require_toTree(self,req,tree):
        for slot,type_ in req.items():
            ET.SubElement(tree,'type',{'slot':str(slot)}).text = type_.get_name()

    def write_ensure_to_tree(self,req,tree):
        for slot,type_ in req.items():
            ET.SubElement(tree,'type',{'slot':str(slot)}).text = type_.get_name()

    def write_toTree(self,ext,tree):
        ET.SubElement(tree,'type').text = ext.get_name()


def could_be(t,method,i):
    try:
        return isinstance(t,Any) or t.get_name() == method.get_requirement('Type')[i].get_name() 
    except KeyError:
        return False

class has_types (matchers.Matcher):

    def __init__(self,source_types):
        self.types = list(source_types)

    def _matches(self,method):
        could_be_types = [could_be(t,method,i) for i,t in self.types]
        return all(could_be_types)

    def describe_to(self,description): 
        description.append("has sources matching the pathern {}".format(self.types))

class Type (object):

    @staticmethod
    def new(name):
        return _types[name]()

    def is_unreal(self):
        return False

    def __repr__(self):
        return "<Type {}>".format(self.get_name())

class Integer (Type):
    def name(self): return "Integer"

class Real (Type):
    def name(self): return "Real"

class Char (Type):
    def name(self): return "Char"

class Unreal (Type):
    def name(self): return "Unreal"
    def is_unreal(self): return True

class Any (Unreal):
    def name(self): return "Any"

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
        sources = method.get_sources()
        impl = method.get_impl()
        new_sources = [model.Sink(s.get_id(),s.get_slot()) for s in sources]
        def get_type(method,i):
            try:
                return method.get_requirement('Type')[i] 
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
        
        for new,old in zip(new_sources,function.get_sources()):
            new.set_extensions(old.get_extensions().values())
        
        for source,sink in zip(new_sources,sinks):
            source['Type'] = sink['Type']

        return new_sources

    def apply(self,function,sources):
        from .. import model
        #Determine typesj
        types = [(source.get_slot(),source['Type'])
                    for source in sources]

        method_name = function['MethodName']
        from .methodname import has_method_name
        from .sources import has_sources_length
        from .sinks import has_sinks_length
        #Determine method
        method = self.module.get_method_where(
                matchers.all_of(
                    has_types(types),
                    has_method_name(methodName),
                    has_sources_length(len(sources)),
                    has_sinks_length(len(function.get_sinks()))
                    )
                )
        
        if not 'Type' in method.get_ensurances(): 
            method = self.visit(method)
        
        new_sinks = [model.Sink(sink.get_id(),sink.get_slot()) for sink in function.get_sinks()]
        s_types = [method.get_ensurance('Type')[i] for i in range(len(new_sinks))]

        new_function = model.Function(function.get_id())
        
        for new,old in zip(new_sinks,function.get_sinks()):
            new.set_extensions(old.get_extensions().values())
        
        for i,t in enumerate(s_types):
            new_sinks[i]['Type'] = t
            new_sinks[i].add_function(new_function)

        for s in sources:
            s.add_function(new_function)

        new_function.add_sources(sources)
        new_function.add_sinks(new_sinks)
        new_function.set_extensions(function.get_extensions().values())
        
        return ((sink.get_id(),sink) for sink in new_sinks)


    def final(self,method,sinks):
        from .. import model
        new_method = model.Method(method.get_internal_id())
        new_method.add_ensurances(method.get_ensurances().values())
        new_method.add_requirements(method.get_requirements().values())

        new_impl = model.Impl(new_method)
        new_impl.add_sinks(sinks.values())
        new_impl.add_functions(visitors.calculate_reachable_functions(sinks.values()))

        sink_types = dict(
                (new_method.get_ensurance('Sinks')[sink.get_id()],sink['Type']) 
                    for sink in new_method.get_sinks())

        new_method.set_ensurance('Type',sink_types)
        return new_method
