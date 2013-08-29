import unittest
from unittest.mock import MagicMock

import fbml 
from fbml.structure import Module , Label
from fbml.model import Method, Condition, Data
from fbml.element import *
from fbml.extensions.type import * 
from fbml.extensions.methodname import *



class CompilerTester (unittest.TestCase):

    def setUp(self):
        builder = fbml.get_builder(extensions=['method_name','type'])
        self.stdlib = builder.label_from_string('stdlib').get()
        self.module = self.stdlib.root().make('main',
                lambda label: Module(None,label,[self.stdlib]))
        self.method_finder = MethodFinder(self.module)
        self.type_finder = SimpleTyping(self.module)

