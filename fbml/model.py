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

Method
======

.. autoclass:: fbml.model.Method
    :members:


Impl
====

.. autoclass:: fbml.model.Impl
    :members:

Function 
========

.. autoclass:: fbml.model.Function
    :members:

Sink
====

.. autoclass:: fbml.model.Sink
    :members:



"""

from functools import partial


from . import structure
from .structure import Namespace

from .util import readonly
from .util import exceptions

class Method (Namespace):
    
    """
    The Method is the descriptor of the functions of the program. It describes
    in what method that the function will be run.

    The Method can contain an implementaion. 

    :param label: The label of the method
    :param requirments: The requirments for the method. These describes 
        the required features to run the program
    :param ensurances: The ensurances for the mehtod. These describes the
        effect of running the method.
    """

    def __init__(self, label):
        super(Method,self).__init__(label)

    def make_condition(self, name, factory):
        res = self.make(name,factory)
        setattr(self,name,res)
        return res 

    def make_impl(self, factory):
        self.impl = self.make('impl',factory)
        return self.impl

    def __repr__(self):
        return '<method {m.label}>'.format(m=self)


class Condition(Namespace):

    """
    Condition is the testable aspeckt of the Method

    Contains a subnamespace called 'slots', wich allows the user
    to acces the slot information from the slot ids.

    Slots is just data.
    """

    def __init__(self, label):
        super(Condition,self).__init__(label)
        self.slots = self.make('slots',Namespace)
        self.data = Data()

    def make_slot(self,slot_id, factory):
        return self.slots.make(slot_id,factory)


class Impl (Namespace):
    
    """
    Impl is the implementations of the Mehtod. It contains four major
    subnamespaces; 'sinks', 'functions', 'target_sinks', and 'source_sinks'. 
    Theses can be used to access the sinks and functions using their ids.

    The subnamespace 'sinks' Allows the user to acces the sinks by id, or
    all of them. The same thing for the 'functions'. The 'target_sinks' and the 
    'source_sinks' alows the user to acces sinks by the slot id of the method.
    
    'source_sinks' and 'target_sinks' sinks all refer to the methods slot data.

    :param label: a label to identiy it in the scope
    """

    def __init__(self, label):
        super(Impl,self).__init__(label)
        self.sinks = self.make('sinks',Namespace)
        self.functions = self.make('functions',Namespace)
        self.target_sinks = self.make('target_sinks',Namespace)
        self.source_sinks = self.make('source_sinks',Namespace)

    def make_sink(self, name, factory):
        return self.sinks.make(name, factory)

    def make_function(self, name, factory):
        return self.functions.make(name, factory)

    def make_target_sink(self, name, slot, factory):
        return self.target_sinks.make(slot,
                lambda label: self.make_sink(name,partial(factory,label)))

    def make_source_sink(self, name, slot, factory):
        return self.source_sinks.make(slot, 
                lambda label: self.make_sink(name,partial(factory,label)))

    @property
    def method(self):
        return self.parrent

    def depth(self, helper): 
        return 0

    def __repr__(self):
        return "<impl '{s.parrent.label.name}'>".format(s=self)


class Function (Namespace):
    
    """
    A Function is the method call of fbml. It is posible to
    use this to define which sinks the Methods should be run with.

    The subnamesapces 'sources' and 'targets' enables the user to
    access the sinks using the slot names of the method.
    """

    def __init__(self, label):
        super(Function, self).__init__(label)
        self.data = Data()
        self.sources = self.make('sources',Namespace)
        self.targets = self.make('targets', Namespace)

    def make_target(self, slot, sink):
        def make_sink(label):
            sink.target = label
            return sink
        return self.targets.make(slot,make_sink)
    
    def make_source(self, slot, sink):
        return self.sources.make(slot, lambda x : sink) 

    @property
    def impl(self):
        return self.parrent.parrent

    def __repr__(self):
        return '<function label={f.label.name}>'.format(f=self)

    def depth(self,helper):
        if not self in helper:
            if not self.sources: depth = 0;
            else: depth = max(sink.depth(helper) for sink in self.sources) +1
            helper[self] = depth;
        return helper[self]


class Sink (Namespace):
    
    """
    The sink contains the esential data for execution of the program and
    is the combiner of functions

    .. attribute:: impl
        
        the implementaions in where the sink resides
    
    .. attribute:: owner 

        Sould be used when wanting to access the owner of the sink, this can be
        a :class:`~fbml.model.Function` or the :class:`~fbml.model.Impl`

    """

    def __init__(self, label):
        super(Sink,self).__init__(label)
        self.data = Data()
  
    @property
    def owner(self):
        return self.target.parrent.parrent

    @property
    def impl(self):
        return self.parrent.parrent

    def __repr__(self):
        return '<sink {s.label.name}>'.format(s=self)

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.owner.depth(helper) + 1
        return helper[self]


class Data(object):
    """ The extendable data object """

    def find_from_name_list(self, name_list):
        if not name_list:
            return self
        else:
            raise Exception('Badd access to {}'.format(name_list))
