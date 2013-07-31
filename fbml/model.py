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

    def get_all(self):
        return vars(self)

    def set(self, name, data):
        setattr(self, name, data)

    def __repr__(self):
        return repr(self.get_all())

class Extendable (object): 

    def __init__(self):
        self._extension = ExtensionManager()

    ext = readonly('_extension')

class Method (Namespace):

    """
    The Method is the descriptor of the functions of the program. It describes
    in what method that the function will be run.

    The Method can contain an implementaions. 

    :param label: The label of the method
    :param requirments: The requirments for the method. These describes 
        the required features to run the program
    :param ensurances: The ensurances for the mehtod. These describes the
        effect of running the method.
    """

    def __init__(self, label, requirements, ensurances):
        super(Method,self).__init__(label)
        self._requirements = requirements
        self._ensurances = ensurances 
        self.sources = list()
        self.targets = list()

    req = readonly('_requirements')
    ens = readonly('_ensurances')

    @property
    def impl(self):
        return self.find('impl')

    def make_target(self, slot, sink):
        res = self.make(slot, sink.add_user)
        for name, data in vars(self.ens.targets[slot].extends).items():
            sink.ext.set(name,data)
        self.targets.append(res)
        return res
    
    def make_source(self, slot, sink):
        res = self.make(slot,sink.set_target) 
        for name, data in vars(self.req.sources[slot].extends).items():
            sink.ext.set(name,data)
        self.sources.append(res)
        return res

    def make_impl(self, factory):
        self.make('impl',factory)
        return self.impl

    def __repr__(self):
        return '<method {m.label}>'.format(m=self)

    def depth(self,helper):
        return 0  

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
        self.source_labels = list() 
        self.target_labels = list()

    def make_target(self, slot, sink):
        def set_target(label):
            sink.set_target(label)
            self.target_labels.append(label)
        res = self.make(slot, set_target)
        return res
    
    def make_source(self, slot, sink):
        def add_user(label):
            sink.add_user(label)
            self.source_labels.append(label)
        res = self.make(slot, add_user) 
        return res

    @property
    def impl(self):
        return self.label.parrent

    def __repr__(self):
        return '<function label={f.label}>'.format(f=self)

    def depth(self,helper):
        if not self in helper:
            if not self.sources: depth = 0;
            else: depth = max(sink.depth(helper) for sink in self.sources) +1
            helper[self] = depth;
        return helper[self]


class Sink (Extendable):

    def __init__(self, label):
        Extendable.__init__(self)
        self._label = label 
        self._users = dict() 
   
    label = readonly('_label')
    users = readonly('_users')
    target = readonly('_target')

    @property
    def slot(self):
        return self.target.name

    def user_slot(self, user):
        return self._users[user].name

    @property
    def owner(self):
        return self.target.parrent

    def is_remote_sink(self):
        return self.is_method_source() or self.is_method_target()

    def is_method_target(self):
        return any(isinstance(user,Method) for user in self.users)

    @property
    def method_target(self):
        return [self.user_slot(user)
                for user in self.users if isinstance(user,Method)][0]

    def is_method_source(self):
        return isinstance(self.owner, Method)

    @property
    def impl(self):
        return self.label.parrent

    def set_target(self, target):
        self._target = target
        return self

    def add_user(self, target):
        self._users[target.parrent] = target
        return self

    def __str__(self):
        return '<sink {s.label.name} at {s.target.name}>'.format(s=self)

    def __repr__(self):
        return '<sink {s.label} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.owner.depth(helper) + 1
        return helper[self]

