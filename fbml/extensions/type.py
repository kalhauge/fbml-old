from . import Extension
from ..util import matchers
from ..util import exceptions
from ..util import visitors
from ..parsers import xmlformat 

import xml.etree.ElementTree as ET


def get_source_types(function):
    return [s['type'] for s in function.get_sources()]

class TypeFormat (xmlformat.XMLExtensionFormat):
    def __init__(self): 
        self.name = 'type'

    def parse_method(self,tree):
        m = ((x.attrib['slot'],Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parse_extend(self,tree):
        m = ((x.attrib['slot'],Type.new(x.text)) for x in tree.findall('type'))
        return dict(m)

    def parse(self,tag,tree):
        return self.parse_functions[tag](self,tree)

    parse_functions = {
            'extend' : parse_extend,
            'require' : parse_method,
            'ensure' : parse_method
            }

    def write(self, tag, req, tree):
        self.write_functions[tag](self,req,tree) 

    def write_method(self,req,tree):
        for slot,type_ in req.items():
            ET.SubElement(tree,'type',{'slot':str(slot)}).text = type_.name()

    def write_extend(self,ext,tree):
        ET.SubElement(tree,'type').text = ext.name()

    write_functions = {
            'extend': write_extend,
            'require': write_method,
            'ensure': write_method
            }

def could_be(t,method,i):
    try:
        return isinstance(t,Any) or t.name() == method.req.type[i].name() 
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
        return "<type {}>".format(self.name())

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
    NAME = "type"
    XML_FORMAT = TypeFormat()


class TypeSetter (visitors.DataFlowVisitor):

    def __init__(self,module):
        super(TypeSetter,self).__init__()
        self.module = module

    def setup(self,method):

        slot_sinks = dict((slot, method.impl.sinks[source_name])
                for slot, source_name in method.req.sources.items())

        for slot, sink in slot_sinks.items():
            try:
                if sink.ext.type != method.req.type[slot]:
                    raise Exception("In consistent state on source {} and method {}"
                            .format(source.ext.type, method.req.type[slot]))
            except KeyError:
                sink.ext.type = method.req.type[slot]
        return dict((sink, sink.ext.type) for sink in slot_sinks.values())

    def merge(self,function,sinks):
        sources = dict()
        for source in function.sources:
            source.ext.type = source.sink.ext.type
            sources[source] = source.ext.type
        return sources

    def apply(self,function,sources):
        from .. import model
        if not function.sources: return {function.sinks[0]:function.sinks[0].ext.type}
        #Determine typesj
        types = [(source.slot, source.ext.type)
                    for source in sources]

        method_name = function.ext.method_name
        from .methodname import has_method_name
        from .sources import has_sources_length
        from .sinks import has_sinks_length
        #Determine method
        method = self.module.get_method_where(
                matchers.all_of(
                    has_types(types),
                    has_method_name(method_name),
                    has_sources_length(len(sources)),
                    has_sinks_length(len(function.sinks))
                    )
                )
        try: method_types = method.ens.type
        except KeyError: 
            self.visit(method)
            method_types = method.ens.type
       
        for sink in function.sinks:
            sink.ext.type = method_types[sink.slot]

        return dict((sink, sink.ext.type) for sink in function.sinks)


    def final(self,method,sink_types):
        method.ens.type = dict( 
                (sink.slot, sink_types[sink]) 
                for sink in method.internal_sinks)

        return method
