from . import Extension
from ..util import matchers
from ..util import exceptions
from ..util import visitors
from ..parsers import xmlformat 

import xml.etree.ElementTree as ET


class TypeDoesNotExist(exceptions.MallformedFlowError):
    """ TypeDoesNotExist is thrown if a type does not exist"""

class TypeFormat(object):
    name = "type"

    def parse(self, parser, tree):
        return Type.new(tree.text)

    def write(self, writer, value, root):
        ET.SubElement(root,'type').text = value.name

class TypesFormat(object):
    name = "types"

    def parse(self, parser, tree):
        return parser.parse_objects(tree,'type')

    def write(self, writer, value, root):
        elm = ET.SubElement(root, 'types')
        for val in value:
            writer.write_object(value,root)

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
    _buildin_types = {
            'Any',
            'Integer',
            'Real',
            'Char'
            }

    def __init__(self, name):
        self.name = name

    @staticmethod
    def new(name):
        if not name in Type._buildin_types:
            raise 
        
        return Type(name) 


    def is_unreal(self):
        return False

    def __repr__(self):
        return "<type {}>".format(self.name())




class TypeExtension(Extension):
    NAME = "type"
    XML_FORMATS = [TypeFormat(), TypesFormat()] 


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
