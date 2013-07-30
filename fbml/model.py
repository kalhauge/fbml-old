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

    :param label: The label of the method

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
        res = self.make('target_'+str(slot), sink.add_user)
        for name, data in vars(self.ens.targets[slot].extends).items():
            sink.ext.set(name,data)
        self.targets.append(res);
        return res
    
    def make_source(self, slot, sink):
        res = self.make('source_'+str(slot),sink.set_target) 
        for name, data in vars(self.req.sources[slot].extends).items():
            sink.ext.set(name,data)
        self.sources.append(res)
        return res

    def make_impl(self, factory):
        self.make('impl',factory)
        return self.impl

    def __repr__(self):
        return '<method label={m.label}>'.format(m=self)

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
        self.sources = list() 
        self.targets = list()

    def make_target(self, slot, sink):
        res = self.make('o_'+str(slot), sink.set_target)
        self.targets.append(res);
        return res
    
    def make_source(self, slot, sink):
        res = self.make('i_'+str(slot),sink.add_user) 
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
            else: depth = max(sink.depth(helper) for sink in self.sources) +1
            helper[self] = depth;
        return helper[self]


class Sink (Extendable):

    def __init__(self, label):
        Extendable.__init__(self)
        self._label = label 
        self._users = [] 
   
    label = readonly('_label')
    users = readonly('_users')
    target = readonly('_target')

    @property
    def slot(self):
        return self.target.name.split('_',1)[1]

    @property
    def owner(self):
        return self.target.parrent

    def is_remote_sink(self):
        return self.is_method_source() or self.is_method_target()

    def is_method_target(self):
        return any(isinstance(user.parrent,Method) for user in self.users)

    @property
    def method_target(self):
        return [user.name.split('_',1)[1] for user in self.users if isinstance(user.parrent,Method)][0]

    def is_method_source(self):
        return isinstance(self.owner, Method)

    @property
    def impl(self):
        return self.label.parrent

    def set_target(self, target):
        self._target = target
        return self

    def add_user(self, target):
        self._users.append(target)
        return self

    def __repr__(self):
        return '<sink {s.label} at {s.target}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.owner.depth(helper) + 1
        return helper[self]

