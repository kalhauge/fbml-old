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

# class TypesFormat(object):
#     name = "types"
# 
#     def parse(self, parser, tree):
#         return frozenset(parser.parse_objects(tree,'type'))
# 
#     def write(self, writer, value, root):
#         elm = ET.SubElement(root, 'types')
#         for val in value:
#             writer.write_object(value,root)

def check(function):
    def inner(*args):
        print(args)
        ret = function(*args)
        print(ret)
        return ret
    return inner

def could_be(type_,method,slot):
    try:
        return type_ == method.req.sources[slot].extends.type
    except KeyError:
        return False

class has_types (matchers.Matcher):

    def __init__(self,source_types):
        self.types = list(source_types)

    def _matches(self,method):
        return all(could_be(t,method,i) for i,t in self.types)

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
            raise TypeDoesNotExist(name + " does not exist")
        return Type(name) 

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "<type {}>".format(self.name)

class TypeSetter (visitors.DataFlowVisitor):

    def __init__(self,module):
        super(TypeSetter,self).__init__()
        self.module = module

    def setup(self,method):
        return ((sink, sink.ext.type) for sink in method.sources)

    def apply(self,function,sink_types):
        types = [(sink.slot, type_) for sink, type_ in sink_types.items() 
                if sink in function.sources]

        types = [ (slot, sink_types[sink]) for sink, slot in function.source_slots.items()]

        method_name = function.ext.method_name
        
        from .methodname import has_method_name
        from ..util.matchers import has_targets, has_sources

        #Determine method
        method = self.module.get_method_where(
                matchers.all_of(
                    has_types(types),
                    has_method_name(method_name),
                    has_sources(slot for slot in function.source_slots.values()),
                    has_targets(slot for slot in function.slot_targets)
                    )
                )

        for slot, sink in function.slot_targets.items():
            sink.ext.type = method.ens.targets[slot].extends.type
            yield sink, sink.ext.type

    def final(self,method,sink_types):
        for sink, slot_id in method.targets.items():
            method.ens.targets[slot_id].extends.type = sink.ext.type
        
        return method

class TypeExtension(Extension):
    NAME = "type"
    XML_FORMATS = [
            TypeFormat(), 
            #TypesFormat()
            ] 


