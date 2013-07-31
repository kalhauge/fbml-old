"""
.. module:: pyfblm.matchers

Currently just an wrapper and extendtions of the :mod:`hamcrest` module. 

"""

import hamcrest as hc
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.hasmethod import hasmethod

class Matcher (BaseMatcher):

    def _matches(self,item):
        super(Matcher,self)._matches(item)

all_of = hc.all_of

class has_sources(Matcher):
    
    def __init__(self,slots):
        self._slots = list(slots)
        self._matcher = hc.contains_inanyorder(*self._slots)

    def _matches(self, method):
        return self._matcher.matches(method.req.slots.names)

    def describe_to(self,description):
        description.append("sources with slots satisfying ( ")
        self._matcher.describe_to(description)
        description.append(" )")

class has_targets(Matcher):
    
    def __init__(self,slots):
        self._slots = list(slots)
        self._matcher = hc.contains_inanyorder(*self._slots)

    def _matches(self, method):
        return self._matcher.matches(method.ens.slots.names)
       
    def describe_to(self,description):
        description.append("targets with slots satisfying ( ")
        self._matcher.describe_to(description)
        description.append(" )")


