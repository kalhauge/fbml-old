import unittest
from  unittest.mock import MagicMock 
from functools import partial   

from fbml.structure import *
from fbml.model import *


class SourceTester (unittest.TestCase):
    
    def test_creation (self):
        sink = MagicMock()
        target = MagicMock()
        s = Source(sink,target)

o
"""
class ImplTestCase (unittest.TestCase):

    def test_method_creation (self):
        root = RootPackage([])
        module = root.make_child('test_module', partial(Module,imports=[]))
        method = module.make_child('simple_method', Method)
        label = Label.from_string('test_module.simple_method',root)
        self.assertEqual(label.get(), method)

    def test_impl_creation (self):
        root = RootPackage([])
        module = root.make_child('test_module', partial(Module,imports=[]))
        method = module.make_child('simple_method', Method)
        impl = method.make_impl()
        self.assertEqual(impl,method.impl)

    def test_function_creation(self):
        root = RootPackage([])
        module = root.make_child('test_module', partial(Module,imports=[]))
        method = module.make_child('simple_method', Method)
        impl = method.make_impl()
        function = impl.make_function('fid',Function)
        self.assertEqual(function, impl.functions['fid'])

    def test_extensions(self):
        root = RootPackage([])
        module = root.make_child('test_module', partial(Module,imports=[]))
        method = module.make_child('simple_method', Method)
        impl = method.make_impl()
        function = impl.make_function('fid',Function)

        function.ext.types = 'New Type'
        function.ext.method_name = 'Hello'

        self.assertEqual('New Type',function.ext.types)
        self.assertEqual('Hello',function.ext.method_name)
        self.assertDictEqual(
                {'types':'New Type','method_name' : 'Hello'},
                function.ext.get_all())

"""
