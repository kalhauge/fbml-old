import unittest
from unittest.mock import MagicMock

from fbml.element import *

class ElementTester(unittest.TestCase): 
    pass

class SinkTester (unittest.TestCase):

    def test_new(self):
        function = MagicMock()
        sink = Sink.new(From(function,'slot'))

        self.assertEqual(sink.owner,function)
        self.assertEqual(sink.slot,'slot')
        self.assertIsNotNone(sink.data)

    def test_data(self):
        function = MagicMock()
        sink = Sink.new(From(function,'slot'),{'value': 1})

        self.assertEqual(sink.data.value, 1)

    def test_depth(self):
        function = MagicMock()
        function.depth.return_value = 1 
        sink = Sink.new(From(function,'slot'),{'value': 1})
        helper = {}

        self.assertEqual(sink.depth(helper),2)
        function.depth.assert_called_with(helper)

    def test_update_data_only_functions(self):
        function = MagicMock()
        sink = Sink.new(From(function,'slot'),{'value': 1})

        new_function = MagicMock()
        new_sink = sink.update_data(new_function)

        self.assertEqual(new_sink.data, sink.data)
        self.assertEqual(new_sink.slot, sink.slot)
        self.assertEqual(new_sink.owner, new_function)
        self.assertEqual(sink.owner, function)

    def test_update_data_only_data(self):
        function = MagicMock()
        sink = Sink.new(From(function,'slot'),{'value': 1})

        new_sink = sink.update_data(function, {'value': 2})

        self.assertNotEqual(new_sink.data, sink.data)
        self.assertEqual(new_sink.data.value, 2)
        self.assertEqual(new_sink.slot, sink.slot)


class FunctionTester (unittest.TestCase):

    def test_update_data_only_sinks(self):
        sink = MagicMock()
        function = Function.new({'sink':sink}) 

        other_sink = MagicMock()
        new_function = function.update_data({sink:other_sink})

        self.assertNotEqual(new_function.sources.sink,function.sources.sink)
        self.assertEqual(new_function.data, function.data)

    def test_update_data_only_data(self):
        pass

class ImplTester (unittest.TestCase):

    def test_build_simple(self):
        a, b = Source.new('A'), Source.new('B')
        add =  Function.new({'a':a, 'b':b})
        c = Target.new(From(add,'c'))
        impl = Impl.new({'C':c})

        self.assertEqual(set(impl.sinks),set((a,b,c)))
        self.assertEqual(set(impl.functions),set((add,)))
        self.assertEqual(set(impl.source_sinks),set((a,b)))
        self.assertEqual(set(impl.target_sinks),set((c,)))






