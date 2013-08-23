"""
.. currentmodule:: fbml.impl
.. moduleauthor:: Christian Gram Kalhauge

"""

from collections import namedtuple

import logging
log = logging.getLogger(__name__)

from fbml.util import Immutable, namedtuple_from_dict

Target = namedtuple('Target', ['function', 'slot'])
Source = namedtuple('Source', ['sink', 'slot'])

class Impl (Immutable):

    def __init__ (self, method, target_sinks):
        Immutable.__init__(
                self = self,
                method_id = method.name,
                target_sinks = tuple(target_sinks))

class Sink (Immutable):

    def __init__ (self, target, extends):
        Immutable.__init__(
                self = self,
                target = target,
                ext = namedtuple_from_dict("Extensions", extends) 
                )

    @property
    def owner(self):
        return self.target.function

    def depth(self, helper):
        if not self in helper:
            helper[self] = self.owner.depth(helper) + 1
        return helper[self]

class Source(Sink):

    def __init__(self, impl, extends):
        Immutable.__init__(
                self = self,
                impl = impl,
                ext = namedtuple_from_dict("Extensions", extends) 
                )

    @property
    def owner(self):
        return self.impl

    def depth(self, helper): 
        return 0

class Function (Immutable):

    def __init__ (self, sources, extends):
        Immutable.__init__(
                self = self,
                sources = tuple(sources),
                ext = namedtuple_from_dict("Extensions", extends)
                )

    def depth(self,helper):
        if not self in helper:
            if not self.sources: depth = 0;
            else: depth = max(sink.depth(helper) 
                            for sink in self.sources.values()) +1
            helper[self] = depth;
        return helper[self]
