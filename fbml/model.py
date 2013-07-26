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
    dictname = namespace + 's'
    def make_type(self, name, factory):
        result = self.make(str(name),factory)
        getattr(self, dictname)[name] = result 
        return result
    return make_type

class ExtensionManager (object):

    def __init__ (self):
        self.__dict__['_extensions'] = dict()

    def __setattr__(self, name, extend):
        self.__dict__['_extensions'][name] = extend

    def __getattr__(self, name):
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

    impl  = property(lambda self: self.find('impl'))
    req   = readonly('_requirements')
    ens   = readonly('_ensurances')

    def internal_sinks(self):
        return [self.impl.sinks[name] for name in self.ens.sinks]

    def make_impl(self, factory):
        self.make('impl',factory)
        return self.impl

class Impl (Labelable, ModelObject):

    def __init__(self, label):
        super(Impl,self).__init__(label)
        self.sinks = dict()
        self.functions = dict()

    make_sink = make_with('sink') 
    make_function = make_with('function')

    method = property(lambda self: self.label.parrent) 

class Function (Labelable, ExtendableModelObject):

    def __init__(self, label):
        super(Function, self).__init__(label)
        ExtendableModelObject.__init__(self)
        self.sinks = dict()
        self.sources = dict() 

    def make_sink(self, slot, name, factory):
        def sink_factory(label):
            res = self.make('sink_'+str(slot), partial(factory,label))
            self.sinks[name] = res;
            return res
        self.impl.make_sink(name,sink_factory)
    
    make_source = make_with('source')

    impl = property(lambda self: self.label.parrent)

    def depth(self,helper):
        if not self in helper:
            if not self.sources: depth = 0;
            else: depth = max(src.depth(helper) for src in self.sources.values()) +1
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

    function = property(lambda self: self.target.parrent)

    def __repr__(self):
        return '<sink {s.label} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.function.depth(helper) + 1
        return helper[self]

class Source (ExtendableModelObject):

    def __init__(self, sink, target):
        super(Source, self).__init__()
        ExtendableModelObject.__init__(self)
        self._sink     = sink
        self._target = target 

    sink = readonly('_sink')
    target = readonly('_target')

    function = property(lambda self: self.target.parrent)

    def __repr__(self):
        return '<source {s.sink} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.sink.depth(helper) + 1;
        return helper[self]
