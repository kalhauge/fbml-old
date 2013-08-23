"""
.. currentmodule:: fbml.impl
.. moduleauthor:: Christian Gram Kalhauge

"""

from collections import namedtuple

import logging
log = logging.getLogger(__name__)

from fbml.util import Immutable


Target = namedtuple('Target', ['function', 'slot'])
Source = namedtuple('Source', ['sink', 'slot'])

class Impl (Immutable):

    def __init__ (self, results):
        Immutable.__init__(**locals())
    

class Sink (Immutable):

    def __init__ (self, target, extends):
        Immutable.__init__(**locals())


class Function (Immutable):

    def __init__ (self, sources, extends):
        Immutable.__init__(**locals())
