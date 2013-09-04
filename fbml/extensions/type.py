import collections

from ..structure import Label
from . import Extension
from ..util import matchers
from ..util import exceptions
from ..util import visitors
from ..parsers import xmlformat 

import xml.etree.ElementTree as ET


class TypeDoesNotExist(exceptions.MallformedFlowError):
    """ TypeDoesNotExist is thrown if a type does not exist"""

class CouldNotMatchTypesToMethods(exceptions.FbmlError):
    """ CouldNotTypeImpl is thrown if it is imposible to find
        a method to match a type """
    def __init__(self, types, methods):
        super(CouldNotMatchTypesToMethods,self).__init__(
                "Could not match {types} to {methods}".format(
                    **locals())
                )
                
class AmbiguousTypeForSinkAtFunction(exceptions.FbmlError):

    def __init__(self, sink, function): 
        super(AmbiguousTypeForSinkAtFunction,self).__init__(
                "Ambiguous type for {sink} at {function}".format(
                    **locals())
                )



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

class BooleanType (Type):
    name = 'Boolean'

    def parse_str(self, string):
        return bool(string)

class CharType (Type):
    name = 'Char'

    def parse_str(self, string):
        return string[0]

class RealType (Type):
    name = 'Real'

    def parse_str(self, string):
        return float(string)


Type._buildin_types = {type_.name : type_() for type_ in [BooleanType, IntegerType,CharType,RealType]}

TypeAsSlot = collections.namedtuple('TypeAsSlot', ['slot'])

def generate_find_types(module):

    def find_types(method):

        return 
    return find_types


def can_method_be_called_with(method, types):
    for slot, t in types.items():
        method_type = method.req.type[slot]
        if isinstance(method_type, TypeAsSlot):
            if method_type.slot == slot:
                continue
            elif types[method_type.slot] != t:
                return False
        elif t != method_type:
            return False
    else:
        return True
    
def type_of_target(slot, methods):
    return set(method.ens.slots[slot].type for method in methods)


def method_callable_with_types(method, types):
    for slot, data in method.req.slots.with_names:
        if isinstance(types[slot], TypeAsSlot):
            continue
        if data.type != types[slot]:
            return False
    else:
        return True


class SimpleTyping (visitors.DataFlowVisitor):
    """
    Single parse
    """

    def __init__(self, module):
        self.module = module

    def setup(self, sink, impl):
        return sink

    def merge(self, sink, function):
        methods = [Label.find(method,self.module) 
                for method in function.data.methods]
        try:
            type_, = type_of_target(sink.slot, methods)
        except ValueError:
            raise AmbiguousTypeForSinkAtFunction(sink,function)
        return sink.update_data(function, {'type':type_})

    def apply(self, function, sinks):
        types = {slot: sinks[sink].data.type
                    for slot, sink in vars(function.sources).items()}

        def valid_method_lable(method_label):
            method = Label.find(method_label,self.module)
            return method_callable_with_types(method,types)
        
        methods = list(filter(valid_method_lable,function.data.methods))
        if not methods:
            raise CouldNotMatchTypesToMethods(types,set(function.data.methods))
        return function.update_data(sinks,
                        {'methods': frozenset(map(str,methods))} )

    def final(self, impl, functions, sinks):
        return impl.update_data(sinks)

class AllowedTypes (visitors.DataFlowVisitor):
    """
    The opjective of this visitor is to find the allowed types
    of the arguments

    function data is a tuple of Types and restrictions 
    
    sink data is a tuple :
        (Type, Restrictions)
    """
    
    def __init__(self, module):
        self.module = module

    def setup(self, sink, impl):
        restrictions = dict(map(lambda x: (x.slot,set()),impl.source_sinks))
        try: return sink.data.type, restrictions
        except AttributeError:
            return TypeAsSlot(sink.slot), restrictions 
    
    def merge(self, sink, functions):
        methods, restrictions = functions[sink.owner]
        return type_of_target(sink.slot, methods), restrictions

    def apply(self, function, sinks):
        
        types = dict((slot, sinks[sink][0]) 
                    for slot, sink in vars(function.sources).items())
        methods = []
        for method_label in function.data.methods:
            method = Label.find(method_label,self.module)
            if not method_callable_with_types(method,types):
                continue
            methods.append(method)
     
        restrictions = dict()
        for sink in function.sources:
            for source_slot, restiction in sinks[sink][1].items():
                restrictions.setdefault(source_slot,set()).union(restiction)
        
        return methods, restrictions

    def final(self,impl, functions, sinks):
        return {slot: sinks[sink] for slot, sink in vars(impl.targets).items()}



class TypeExtension(Extension):
    NAME = "type"
    XML_FORMATS = [
            TypeFormat(), 
            #TypesFormat()
            ] 


