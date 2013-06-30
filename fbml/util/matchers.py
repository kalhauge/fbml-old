"""
.. module:: pyfblm.matchers

Currently just an wrapper and extendtions of the :mod:`hamcrest` module. 

"""

import hamcrest.core as hc
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.hasmethod import hasmethod

class Matcher (BaseMatcher): pass

all_of = hc.all_of
class require (Matcher):

    def __init__(self,name,matcher):
        self._name = name
        self._matcher = matcher

    def _matches(self, item):
        if not hasmethod(item,'getRequirement'):
            return False
        return self._matcher.matches(item.getRequirement(self._name))

    def describe_to(self,description):
        description.append("requirement with name {!r} that matches {!s}".format(
                self._name,
                self._matcher)
                )
