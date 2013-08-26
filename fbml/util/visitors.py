
def calculate_runorder(impl):
    f_set = impl.functions
    return sorted(f_set,key=lambda a : a.depth(dict()));        


class DataFlowVisitor (object):

    def __init__(self):
        self._methods = dict()

    def visit(self,method):
        if method in self._methods:
            return self._methods[method]
        impl = method.impl

        # Calculates the runorder and then removes the method
        runorder = calculate_runorder(impl)

        sink_data = dict()
        function_data = dict()

        for function in runorder:
            sink_data.update((sink, self.merge(sink, function_data))
                for sink in function.targets)
            function_data[function] = self.apply(function, sink_data)
        ret_method = self.final(method,function_data, sink_data)
        self._methods[method] = ret_method
        return ret_method

    def merge(self,sink, functions):
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

    def final(self,method,functions, sinks):
        """
        Takes a dictionary of sinks names to results and the method, and returns
        the result for visiting the method
        """
        pass


class ControlFlowVisitor (object):

    def __init__(self):
        self._methods = dict()

    def visit(self,method):
        if method in self._methods:
            return self._methods[method] 
        runorder = calculate_runorder(method.impl)
        result = self.setup(method)
        for function in runorder:
            result = self.apply(function,result)

        ret_method = self.final(method,result)
        self._methods[method] = ret_method
        return ret_method

    def setup(self, method):
        pass 

    def apply(self, function,result):
        pass

    def final(self, result):
        pass

