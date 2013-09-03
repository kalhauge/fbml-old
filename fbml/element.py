"""
.. currentmodule:: fbml.element
.. moduleauthor:: Christian Gram Kalhauge

"""
import pprint
from collections import namedtuple, deque

import logging
log = logging.getLogger(__name__)

from fbml.util import Immutable, namedtuple_from_dict

from operator import attrgetter

From = namedtuple('From', ['function', 'slot'])


class Element(Immutable):
    pass


class Sink (Element):

    def __init__ (self, target, data):
        Immutable.__init__(**locals())

    @classmethod
    def new(cls, target, data={}):
        return cls(target, namedtuple_from_dict("SinkData", data))

    @property
    def owner(self):
        return self.target.function
    
    @property
    def slot(self):
        return self.target.slot

    def depth(self, helper):
        if not self in helper:
            helper[self] = self.owner.depth(helper) + 1
        return helper[self]

    def __str__(self):
        return 'Sink : {self.data.id!r} at \n{self.owner!s}'.format(**locals())

    def update_data(self, function, data={}):
        new_data = dict(vars(self.data))
        new_data.update(data)
        return self.new(From(function,self.slot),new_data)


class Internal(Sink): pass

class Source(Sink):

    def __init__(self, slot,  data):
        Immutable.__init__(**locals())
   
    @classmethod
    def new(cls, slot, data={}):
        return cls(
                slot = slot,
                data = namedtuple_from_dict("SourceData", data)
                )

    @property
    def owner(self):
        return None 

    @property
    def slot(self):
        return self.__dict__['slot']

    def depth(self, helper): 
        return 0

    def __str__(self):
        return 'Source : {self.data.id!r} at {self.slot!r}'.format(**locals())

class Constant(Sink):

    def __init__(self, data):
        Immutable.__init__(**locals())
   
    @classmethod
    def new(cls, data={}):
        return cls(
                data = namedtuple_from_dict("ConstantData", data)
                )

    @property
    def owner(self):
        return None 

    def depth(self, helper): 
        return 0

    def __str__(self):
        return 'Constant : {self.data.id!r}'.format(**locals())

class Target(Sink): pass

class Function (Element):

    def __init__(self, sources, data):
        Immutable.__init__(**locals())

    @classmethod
    def new(cls, sources, data={}):
        return cls(
                sources = namedtuple_from_dict("Sources", sources),
                data = namedtuple_from_dict("FunctionData", data)
                )

    def depth(self,helper):
        if not self in helper:
            if not self.sources: depth = 0;
            else: depth = max(sink.depth(helper) 
                            for sink in self.sources) +1
            helper[self] = depth;
        return helper[self]

    def __str__(self):
        return 'Function'

    def update_data(self, sink_data, data={}):
        new_data = dict(vars(self.data).items())
        new_data.update(data)
        new_sinks = {slot: sink_data[sink] for slot, sink in vars(self.sources).items()}
        return Function.new(new_sinks, new_data)

def _get_sinks_of_type(sink_type):
    def get_sinks(self):
        return ( sink for sink in self.sinks if isinstance(sink, sink_type) )
    return get_sinks

class Impl (Immutable):

    def __init__ (self, targets, sinks, functions):
        Immutable.__init__(**locals())

    @classmethod
    def new(cls, target_sinks):
        target_sinks = namedtuple_from_dict('Targets',target_sinks)
        sinks, functions = Impl._calculate_reach(target_sinks)
        return cls(
                targets = target_sinks,
                sinks = sinks,
                functions = functions)

    @staticmethod 
    def _calculate_reach(target_sinks):
        #import pdb; pdb.set_trace()
        sinks = set()
        functions = set()
        calc_sinks = deque(target_sinks)
        while calc_sinks:
            sink = calc_sinks.popleft()
            if sink in sinks: continue 
            sinks.add(sink)
            function = sink.owner
            if function:
                if function in functions: continue
                functions.add(function)
                calc_sinks.extend(function.sources)
        return frozenset(sinks), frozenset(functions)

    def functions_with_targets(self, functions):
        targets = {}
        for sink in self.sinks:
            if sink.owner:
                targets.setdefault(sink.owner,set()).add((sink.target.slot, sink))
        return ((function, targets[function]) for function in functions)

    constant_sinks = property(_get_sinks_of_type(Constant))
    internal_sinks = property(_get_sinks_of_type(Internal))
    source_sinks = property(_get_sinks_of_type(Source))
    target_sinks = property(attrgetter('targets'))

    def update_data(self, sink_data):
        new_sinks = {slot: sink_data[sink] 
                for slot, sink in vars(self.targets).items()}
        return Impl.new(new_sinks)
