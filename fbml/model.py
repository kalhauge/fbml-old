"""
.. currentmodule:: fbml.model
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

Subnamespaces
-------------

.. attribute:: impl

.. attribute:: res

.. attribute:: ens

"""

from functools import partial


from . import structure
from .structure import Namespace

from .util import readonly
from .util import exceptions

class Extendable(object):

    def __getattr__(self, name):
        if hasattr(self.data,name):
            return getattr(self.data,name)
        else:
            raise AttributeError('Could not find {!r} in object {!s}, or data'
                    .format(name, self))

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

    def __init__(self, label, impl = None):
        super(Method,self).__init__(label)
        self._impl = impl
        self.req = self.make('req',Condition)
        self.ens = self.make('ens',Condition)

    def __repr__(self):
        return '<method {m.label}>'.format(m=self)

    def get_impl(self): return self._impl 

    def set_impl(self, impl):
        self._impl = impl

    def update_conditions(self):
        self.req.reset_slots()
        self.ens.reset_slots()

        for sink in self.impl.source_sinks:
            self.req.make_slot(sink.slot,lambda x: sink.data)

        for slot, sink in vars(self.impl.targets).items():
            self.ens.make_slot(slot,lambda x: sink.data)

    impl = property(get_impl,set_impl)

class Condition(Namespace, Extendable):
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

    def reset_slots(self):
        self.slots = self.make('slots',Namespace,True)

class Data(object):
    """ The extendable data object """

    def find_from_name_list(self, name_list):
        if not name_list:return self
        else:
            raise exceptions.BadLabelAccess('Bad access to {}'.format(name_list))

