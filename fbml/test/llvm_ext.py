import unittest
from unittest.mock import MagicMock

import fbml
from fbml.structure import Module , Label
from fbml.model import Method, Condition, Data
from fbml.element import *
from fbml.extensions.type import * 
from fbml.extensions.methodname import *
from fbml.extensions.llvm_ext import *
from fbml.extensions.value import *

import llvm
import llvm.core as llvmc


class CompilerTester (unittest.TestCase):

    def setUp(self):
        builder = fbml.get_builder(
                extensions=['method_name','type','llvm','value'])
        self.stdlib = builder.label_from_string('stdlib').get()
        self.module = self.stdlib.root().make('main',
                lambda label: Module(None,label,[self.stdlib]))
        self.method_finder = MethodFinder(self.module)
        self.type_finder = SimpleTyping(self.module)
        self.value_finder = ValueFinder(self.module)
        self.llvm_compiler = BlockCompiler(self.module)

    def test_simple_add(self):
        impl = self.create_simple_add()
        impl_with_methods = self.method_finder.visit(impl)
        impl_with_types = self.type_finder.visit(impl_with_methods)

        llvm_module = llvmc.Module.new('main') 
        llvm_function = llvm_function_from_impl(
                impl_with_types,'simple',llvm_module)

        entry = llvm_function.append_basic_block('entry')

        # Create Initial Values 
        data = BlockData(
                blocks={'entry':entry},
                values={
                    None: {
                        'A': llvm_function.args[0],
                        'B': llvm_function.args[1]
                        }
                    },
                bldr=llvmc.Builder.new(entry)
                )
        exit = self.llvm_compiler.visit(impl_with_types, data)
        exit.bldr.ret(exit.values[impl_with_types]['C'])
        
        print()
        print(llvm_function)

    def test_advanced_add(self):    
        impl = self.create_advanced_add()

        impl_with_methods = self.method_finder.visit(impl)
        impl_with_types = self.type_finder.visit(impl_with_methods)

        llvm_module = llvmc.Module.new('main') 
        llvm_function = llvm_function_from_impl(
                impl_with_types,'advanced',llvm_module)

        entry = llvm_function.append_basic_block('entry')
        
        # Create Initial Values 
        data = BlockData(
                blocks={'entry':entry},
                values={
                    None: {
                        'A': llvm_function.args[0],
                        'B': llvm_function.args[1],
                        'C': llvm_function.args[2],
                        'D': llvm_function.args[3],
                        }
                    },
                bldr=llvmc.Builder.new(entry)
                )

        exit = self.llvm_compiler.visit(impl_with_types, data)
        exit.bldr.ret(exit.values[impl_with_types]['E'])
        
        print()
        print(llvm_function)

    def test_simple_call(self):
        method = self.create_method('multi_add',self.create_advanced_add())
        self.method_finder = MethodFinder(self.module)

        impl = self.optimize(self.create_simple_call())

        llvm_module = llvmc.Module.new('main') 
        llvm_function = llvm_function_from_impl(
                impl,'call',llvm_module)

        entry = llvm_function.append_basic_block('entry')
        
        # Create Initial Values 
        data = BlockData(
                blocks={'entry':entry},
                values={
                    None: {
                        'A': llvm_function.args[0],
                        }
                    },
                bldr=llvmc.Builder.new(entry)
                )

        exit = self.llvm_compiler.visit(impl, data)
        exit.bldr.ret(exit.values[impl]['B'])
        
        print()
        print(llvm_function)

    def test_constant(self):
        impl = self.create_multiply_by("3")
        impl_with_methods = self.method_finder.visit(impl)
        impl_with_types = self.type_finder.visit(impl_with_methods)
        impl = self.value_finder.visit(impl_with_types)

        llvm_module = llvmc.Module.new('main') 
        llvm_function = llvm_function_from_impl(
                impl,'constant',llvm_module)

        entry = llvm_function.append_basic_block('entry')
        
        # Create Initial Values 
        data = BlockData(
                blocks={'entry':entry},
                values={
                    None: {
                        'A': llvm_function.args[0],
                        }
                    },
                bldr=llvmc.Builder.new(entry)
                )

        exit = self.llvm_compiler.visit(impl, data)
        exit.bldr.ret(exit.values[impl]['B'])
        
        print()
        print(llvm_function)

    def test_branch(self):
        true_method = self.create_method('maybe-mult-true',
                self.create_multiply_by("1")) 
        true_method.req.make_slot('test',lambda x: Data())
        true_method.req.slots['test'].match = True 
        true_method.req.slots['test'].type = BooleanType()
        true_method.req.data.method_name = 'maybe_mult'

        false_method = self.create_method('maybe-mult-false',
                self.create_multiply_by("100")) 
        false_method.req.make_slot('test',lambda x: Data())
        false_method.req.data.method_name = 'maybe_mult'
        false_method.req.slots['test'].match = False 
        false_method.req.slots['test'].type = BooleanType()

        self.method_finder = MethodFinder(self.module)

        impl = self.optimize(self.create_branching_call())

        llvm_module = llvmc.Module.new('main') 
        llvm_function = llvm_function_from_impl(
                impl,'mult',llvm_module)

        entry = llvm_function.append_basic_block('entry')
        
        # Create Initial Values 
        data = BlockData(
                blocks={'entry':entry},
                values={
                    None: {
                        'A': llvm_function.args[0],
                        }
                    },
                bldr=llvmc.Builder.new(entry)
                )

        exit = self.llvm_compiler.visit(impl, data)
        exit.bldr.ret(exit.values[impl]['B'])
        
        llvm_function.verify()
        print()
        print(llvm_function)


    def create_method(self, name, impl):
        method = self.module.make_method(name, Method)
        method.impl = self.optimize(impl)
        method.update_conditions()
        method.req.data.method_name = name 
        return method

    def optimize(self, impl):
        impl_with_methods = self.method_finder.visit(impl)
        impl_with_types = self.type_finder.visit(impl_with_methods)
        return self.value_finder.visit(impl_with_types)

    def create_multiply_by(self, string):
        A = Source.new('A', {
            'type' : IntegerType() })
        c1 = Constant.new({
            'type' : IntegerType(),
            'value' : ValueFactory(string)
            })
        f1 = Function.new({'a':A,'b':c1},{
            'method_name' : 'mult'}
            )
        return Impl.new({'B':Target.new(From(f1,'c'))})

    def create_branching_call(self):
        A = Source.new('A', {
            'type' : IntegerType(),
            })
        c1 = Constant.new({
            'type' : IntegerType(),
            'value' : Value(IntegerType(),2)
            })
        gt = Function.new({'a':A, 'b':c1},
                {'method_name':'gt'})

        s1 = Internal.new(From(gt,'c'),
                {})
        
        call = Function.new({'A':A, 'test':s1},
                {'method_name':'maybe_mult'})

        B = Target.new(From(call,'B'))
        return Impl.new({'B':B})

    def create_source(self, name, type_=IntegerType()):
        return Source.new(name, {
            'id' : 's_' + name ,
            'type' : type_
            })

    def create_internal(self, from_):
        return Internal.new(from_, {
            'id' : 'i_' + from_.slot
            })

    def create_simple_add(self):
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
        return Impl.new({'C':C})

    def create_advanced_add(self):
        A, B, C, D = tuple(map(self.create_source,'A B C D'.split()))
        f_1 = Function.new(
                {'a':A, 'b':B}, 
                { 
                    'id':'f_1',
                    'method_name':'add'
                })
        f_2 = Function.new(
                {'a':C, 'b':D}, 
                { 
                    'id':'f_2',
                    'method_name':'add'
                })
        s1, s2 = map(self.create_internal,[From(f_1,'c'),From(f_2,'c')])
        f_3 = Function.new(
                {'a':s1, 'b':s2}, 
                { 
                    'id':'f_3',
                    'method_name':'add'
                })
        E = Target.new(From(f_3,'c'), {'id':'t_E'})
        return Impl.new({'E':E})

    def create_simple_call(self):
        A = self.create_source('A')
        f_1 = Function.new(
                {'A':A, 'B':A, 'C':A, 'D':A},
                {
                    'id':'f_1',
                    'method_name':'multi_add'
                })
        B = Target.new(From(f_1,'E'), {'id': 't_B'})
        return Impl.new({'B':B})







