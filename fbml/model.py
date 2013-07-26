"""
.. module:: fbml.model
.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

=====
Model
=====

This submodule contains the data-flow model of fbml.


This version of the file makes the new version PEP8 ready and special fokus
will be put in that the objects inside the implementation is easy to copy.

"""

from functools import partial


from . import structure
from .structure import Labelable
from .util import readonly



def make_with(namespace):
    def make_type(self, name, factory):
        return self.make(namespace + str(name),factory)
    return make_type


class ExtensionManager (object):

    def __init__ (self):
        self.__dict__['_extensions'] = dict()

    def __setattr__(self, name, extend):
        self.__dict__['_extensions'][name] = extend

    def __getattr__(self, name):
        print(self.__class__.__name__, self.__dict__['_extensions'])
        return self.__dict__['_extensions'][name]

    def get_all(self):
        return self.__dict__['_extensions']

    def set(self, name, data):
        setattr(self, name, data)

class ModelObject (object) : pass


class ExtendableModelObject (ModelObject): 

    def __init__(self):
        self._extension = ExtensionManager()

    ext = readonly('_extension')

class Method (Labelable, ModelObject):

    """
    The Method is the descriptor of the functions of the program. It describes
    in what method that the function will be run.

    """

    def __init__(self, label):
        super(Method,self).__init__(label)
        self._requirements = ExtensionManager()
        self._ensurances = ExtensionManager()

    impl  = property(lambda self: self.children['impl'])
    req   = readonly('_requirements')
    ens   = readonly('_ensurances')

    make_impl = lambda s,f :make_with('impl')(s,'',f)

class Impl (Labelable, ModelObject):

    def __init__(self, label):
        super(Impl,self).__init__(label)

    make_sink = make_with('sink_') 
    make_function = make_with('function_')

    def get_sink(self,name):
        return self.children['sink_' + name]

class Function (Labelable, ExtendableModelObject):

    def __init__(self, label):
        super(Function, self).__init__(label)
        ExtendableModelObject.__init__(self)

    def make_sink(self, slot, name, factory):
        def sink_factory(label):
            return self.make(slot, partial(factory,label))
        self.impl.make_sink(name,sink_factory)
    
    make_source = make_with('source')

    impl = property(lambda self: self.label.parrent)

    def depth(self,helper):
        if not self in helper:
            if len(self.sources) == 0: depth = 0;
            else: depth = max(src.depth(helper) for src in self.sources) +1
            helper[self] = depth;
        return helper[self]

    def __repr__(self):
        return '<function label={f.label}>'.format(f=self)

class Sink (ExtendableModelObject):

    def __init__(self, label, target):
        super(Sink, self).__init__()
        ExtendableModelObject.__init__(self)
        self._label = label 
        self._target = target
        self._users = [] 
   
    label = readonly('_label')
    target = readonly('_target')
    users = readonly('_users')

    def __repr__(self):
        return '<sink {s.label} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            if self.function is None: depth = 0;
            else: depth = self.function.depth(helper) + 1;
            helper[self] = depth;
        return helper[self]

class Source (ExtendableModelObject):

    def __init__(self, sink, target):
        super(Source, self).__init__()
        ExtendableModelObject.__init__(self)
        self._sink     = sink
        self._target = target 

    sink = readonly('_sink')
    target = readonly('_target')
    def __repr__(self):
        return '<source {s.sink} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.sink.depth(helper) + 1;
        return helper[self]
