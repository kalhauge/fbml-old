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
        return type_ == method.req.slots[slot].type
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
    
    _buildin_types = dict()

    @staticmethod
    def new(name):
        if not name in Type._buildin_types:
            raise TypeDoesNotExist(name + " does not exist")
        return Type._buildin_types[name] 

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "<type {}>".format(self.name)

    def parse_str(self, string):
        raise NotImplemented()

    def write_str(self, value):
        raise str(value) 

class IntegerType (Type):
    name = 'Integer'

    def parse_str(self, string):
        return int(string)

class CharType (Type):
    name = 'Char'

    def parse_str(self, string):
        return string[0]

class RealType (Type):
    name = 'Real'

    def parse_str(self, string):
        return float(string)


Type._buildin_types = {type_.name : type_() for type_ in [IntegerType,CharType,RealType]}

class TypeSetter (visitors.DataFlowVisitor):

    def __init__(self,module):
        super(TypeSetter,self).__init__()
        self.module = module

    def setup(self,method):
        return ([(sink, sink.type) for sink in method.impl.source_sinks] +
                [(sink, sink.type) for sink in method.impl.constant_sinks])

    def apply(self,function,sink_types):

        types = [(slot, sink_types[sink]) 
                for slot, sink in function.sources.with_names]

        method_name = function.data.method_name
        
        from .methodname import has_method_name
        from ..util.matchers import has_targets, has_sources

        #Determine method
        method = self.module.get_method_where(
                matchers.all_of(
                    has_types(types),
                    has_method_name(method_name),
                    has_sources(function.sources.names),
                    has_targets(function.targets.names)
                    )
                )

        for slot, sink in function.targets.with_names:
            try:
                sink.data.type = method.ens.slots[slot].type
            except AttributeError:
                self.visit(method)
                sink.data.type = method.ens.slots[slot].type
            yield sink, sink.data.type

    def final(self,method,sink_types):
        for slot, sink in method.impl.target_sinks.with_names:
            method.ens.slots[slot].type = sink.data.type
        
        return method

class TypeExtension(Extension):
    NAME = "type"
    XML_FORMATS = [
            TypeFormat(), 
            #TypesFormat()
            ] 


