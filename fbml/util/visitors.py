from itertools import chain
from functools import reduce


def calculate_runorder(impl):
    f_set = impl.functions
    return sorted(f_set,key=lambda a : a.depth(dict()));        

def seperate(pred, iterable):
    it = iter(iterable)
    deque = (collections.deque(),collections.deque())
    def gen(truth):
        while True:
            if not deque[truth]:
                newval = next(it)
                deque[truth].append(newval)
            else:
                yield deque[truth].popleft()
    return gen(False), gen(True)


class DataFlowVisitor (object):

    def visit(self, impl):
        # Calculates the runorder and then removes the method
        runorder = calculate_runorder(impl)

        sink_data = dict()
        function_data = dict()

        def handle_sink(sink):
            if sink.owner:
                return self.merge(sink, function_data[sink.owner])
            else:
                return self.setup(sink,impl)

        def calculate_sinks(sinks):
            return ((sink, handle_sink(sink)) for sink in sinks
                    if sink not in sink_data)

        for function in runorder:
            sink_data.update(calculate_sinks(function.sources))
            function_data[function] = self.apply(function, sink_data)
        
        sink_data.update(calculate_sinks(impl.targets))
        return self.final(impl,function_data, sink_data)

    def setup(self, sink, impl):
        pass

    def merge(self,sink, function):
        """
        Recives the old sink and the functions data. Then returns the new data
        associated with sink. 
        """
        pass

    def apply(self,function,sinks):
        """
        Returns the new function data
        """
        pass

    def final(self,impl,functions, sinks):
        """
        Takes a dictionary of sinks names to results and the method, and returns
        the result for visiting the method
        """
        pass


class ControlFlowVisitor (object):

    def __init__(self):
        self._methods = dict()

    def visit(self,impl, data=None):
        runorder = calculate_runorder(impl)
        result = reduce(self.apply, runorder, self.setup(impl, data))
        return self.final(impl,result)
        

    def setup(self, impl, data):
        pass 

    def apply(self, function, data):
        pass

    def final(self, impl, result):
        pass

