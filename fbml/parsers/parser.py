"""
.. module:: pyfbml.dataflow.parser

"""
from ..util import exceptions

def str_format(obj, indent):
    from io import StringIO
    si = StringIO()
    try:
        values = obj.values()
        si.write(indent + '+ @' + obj.__class__.__name__ + '\n')
        for name, value in values.items():
            si.write(indent + '| + ' + name + ":\n")
            si.write(str_format(value,indent + '| |'))
        si.write(indent + '+-+' + "\n")
        si.write(indent + '+' + "\n")
        return si.getvalue()
    except AttributeError:
        if isinstance(obj,list):
            for x in obj:
                si.write(str_format(x,indent + ' ' ))
            return si.getvalue()
            si.write(indent + '+' + "\n")
        return indent + '   ' + repr(obj) + '\n'

class ParseObject(object):
    
    def __init__(self,**kargs):
        for k,v in kargs.items():
            setattr(self,k,v)
        self.check()

    def check(self):
        attributes = self.requried_attributes()
        for attr in attributes:
            if not hasattr(self,attr):
                raise exceptions.MallformedFlowError(
                    "{} needs the attribute {}".format(self,attr)
                    )

    def values(self):
        vals = dict((name.lstrip('_'),value) for name, value in vars(self).items())
        return vals

    def __repr__(self):
        return self.__class__.__name__ # str_format(self,'')


class Data(ParseObject):
    def requried_attributes(self): return []
class Module(ParseObject):

    def requried_attributes(self): return ['version']

class Method(ParseObject): 

    def requried_attributes(self): return ['id']

class Impl(ParseObject):

    def requried_attributes(self): return ['method_id']

class Function(ParseObject):
   
    def requried_attributes(self): return ['id']

class Condition(ParseObject):
    def requried_attributes(self): return []

class Sink(ParseObject):
    def requried_attributes(self): return ['id']

class RemoteSink(ParseObject):
    def requried_attributes(self): return ['id','slot']

class Slot(ParseObject):
    def requried_attributes(self): return ['id']

class Map(ParseObject):
    def requried_attributes(self): return ['slot', 'sink']

class Extends(ParseObject):
    def requried_attributes(self): return []


