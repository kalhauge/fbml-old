import unittest
from unittest.mock import MagicMock

import fbml 
from fbml.structure import Module , Label
from fbml.model import Method, Condition, Data
from fbml.element import *
from fbml.extensions.type import * 
from fbml.extensions.methodname import *



class AllowedTypesTester (unittest.TestCase):

    def setUp(self):
        builder = fbml.get_builder(extensions=['method_name','type'])
        self.stdlib = builder.label_from_string('stdlib').get()
        self.module = self.stdlib.root().make('main',
                lambda label: Module(None,label,[self.stdlib]))
        self.method_finder = MethodFinder(self.module)
        self.type_finder = SimpleTyping(self.module)

    def test_simple_add (self):
        A, B = (Source.new('A', {
                    'id':'s_a', 
                    'type':IntegerType()}
                    ), 
                Source.new('B', {
                    'id':'s_b', 
                    'type':IntegerType()}
                    ))
        Add = Function.new({'a':A, 'b':B}, {
                    'id':'f_add',
                    'method_name':'add'})
        C = Target.new(From(Add,'c'), {'id':'t_c'})
        impl = Impl.new({'C':C})
    
        impl_with_methods = self.method_finder.visit(impl)
        impl_with_types = self.type_finder.visit(impl_with_methods)

        self.assertEqual(
                impl_with_types.targets.C.data.type,
                IntegerType())

    def test_simple_add_fail (self):
        A, B = (Source.new('A', {
                    'id':'s_a', 
                    'type':IntegerType()}
                    ), 
                Source.new('B', {
                    'id':'s_b', 
                    'type':RealType()}
                    ))
        Add = Function.new({'a':A, 'b':B}, {
                    'id':'f_add',
                    'method_name':'add'})
        C = Target.new(From(Add,'c'), {'id':'t_c'})
        impl = Impl.new({'c':C})
    
        impl_with_methods = self.method_finder.visit(impl)

        with self.assertRaises(CouldNotMatchTypesToMethods):
           self.type_finder.visit(impl_with_methods)


        
class AuxilliaryTester (unittest.TestCase):

    def test_method_callable_with_types(self):
        label = MagicMock()
        method = Method(label)
        method.req.make_slot('a',lambda x: Data())
        method.req.make_slot('b',lambda x: Data())

        method.req.slots['a'].type = IntegerType()
        method.req.slots['b'].type = RealType()
        self.assertTrue(
                method_callable_with_types(method,
                    {'a': IntegerType(),
                     'b': RealType()}
                ))

        self.assertFalse(
                method_callable_with_types(method,
                    {'a': IntegerType(),
                     'b': IntegerType()}
                ))

        self.assertFalse(
                method_callable_with_types(method,
                    {'a': RealType(),
                     'b': IntegerType()}
                ))

        self.assertTrue(
                method_callable_with_types(method,
                    {'a': TypeAsSlot('Any'),
                     'b': RealType()}
                ))

