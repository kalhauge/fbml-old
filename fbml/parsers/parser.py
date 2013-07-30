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
        return str_format(self,'')

def public_list(name):
    def setter(self, seq):
        setattr(self,name,list(seq))
        return self
    return property(lambda self: getattr(self,name),setter)


class Module(ParseObject):

    def requried_attributes(self): return ['version']

    imports    = public_list('_imports')
    extensions = public_list('_extensions') 
    methods    = public_list('_methods')
    impls      = public_list('_impls')

class Method(ParseObject): 

    def requried_attributes(self): return ['id']

    def set_requirements(self,seq):
        self.requirements = list(seq)

    def set_ensurances(self,seq):
        self.ensurances = list(seq)


class Impl(ParseObject):

    def requried_attributes(self): return ['method_id']

    def set_functions(self,seq):
        self.functions = list(seq)


class Function(ParseObject):
   
    def requried_attributes(self): return ['id']
    
    def set_sinks(self,seq):
        self.sinks = list(seq)

    def set_sources(self,seq):
        self.sources = list(seq)


class Sink(ParseObject):
    def requried_attributes(self): return ['id']

class RemoteSink(ParseObject):
    def requried_attributes(self): return ['id']

class Slot(ParseObject):
    def requried_attributes(self): return ['id']

class Map(ParseObject):
    def requried_attributes(self): return ['slot', 'sink']

class Extends(ParseObject):
    def requried_attributes(self): return []


