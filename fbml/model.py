"""
.. module:: fbml.model
.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

=====
Model
=====

This submodule contains the data-flow model of fbml.


This version of the file makes the new version PEP8 ready and special fokus
will be put in that the objects inside the implementation is easy to copy.

The :class:`~fbml.model.Method` and :class:`~fbml.model.Impl` is an extendsion
of the structural class (:class:`fbml.structure.Namespace`) 

"""

from functools import partial


from . import structure
from .structure import Namespace

from .util import readonly
from .util import exceptions



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

class Extendable (object): 

    def __init__(self):
        self._extension = ExtensionManager()

    ext = readonly('_extension')

class Method (Namespace):

    """
    The Method is the descriptor of the functions of the program. It describes
    in what method that the function will be run.

    :param label: The label of the method

    """

    def __init__(self, label):
        super(Method,self).__init__(label)
        self._requirements = ExtensionManager()
        self._ensurances = ExtensionManager()

    req = readonly('_requirements')
    ens = readonly('_ensurances')

    @property
    def impl(self):
        return self.find('impl')

    @property 
    def internal_sinks(self):
        return [self.impl.sinks[name] for name in self.ens.sinks]

    @property
    def internal_sources(self):
        return [self.impl.sinks[name] for name in self.req.sources.values()]

    def make_impl(self, factory):
        self.make('impl',factory)
        return self.impl

    def __repr__(self):
        return '<method label={m.label}>'.format(m=self)

class Impl (Namespace):

    def __init__(self, label):
        super(Impl,self).__init__(label)
        self.sinks = dict()
        self.functions = dict()

    make_sink = make_with('sink') 
    make_function = make_with('function')

    @property
    def method(self):
        return self.label.parrent

class Function (Namespace, Extendable):

    def __init__(self, label):
        super(Function, self).__init__(label)
        Extendable.__init__(self)
        self.sinks = list()
        self.sources = list() 

    def make_sink(self, slot, name, factory):
        def sink_factory(label):
            res = self.make('o'+str(slot), partial(factory,label))
            self.sinks.append(res);
            return res
        self.impl.make_sink(name,sink_factory)
    
    def make_source(self, slot, factory):
        res = self.make('i'+str(slot), factory) 
        self.sources.append(res)
        return res

    @property
    def impl(self):
        return self.label.parrent
    
    def __repr__(self):
        return '<function label={f.label}>'.format(f=self)

    def depth(self,helper):
        if not self in helper:
            if not self.sources: depth = 0;
            else: depth = max(src.depth(helper) for src in self.sources) +1
            helper[self] = depth;
        return helper[self]


class Targetable (object):
    
    def __init__(self, target):
        self._target = target

    target = readonly('_target')

    @property
    def slot(self):
        return self.target.name[1:]

    @property
    def function(self):
        return self.target.parrent


class Sink (Targetable, Extendable):

    def __init__(self, label, target):
        Targetable.__init__(self, target)
        Extendable.__init__(self)
        self._label = label 
        self._users = [] 
   
    label = readonly('_label')
    users = readonly('_users')

    def add_user(self, user):
        self._users.append(user)

    def __repr__(self):
        return '<sink {s.label} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.function.depth(helper) + 1
        return helper[self]

class Source (Targetable, Extendable):

    def __init__(self, sink, target):
        Targetable.__init__(self, target)
        Extendable.__init__(self)
        self._sink = sink
        self._sink.add_user(self)

    sink = readonly('_sink')

    def __repr__(self):
        return '<source {s.sink} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.sink.depth(helper) + 1;
        return helper[self]
