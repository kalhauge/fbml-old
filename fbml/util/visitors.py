
def calculate_reachable_functions(sinks):
    from collections import deque 
    sources = []
    q = deque(sinks);
    f_set = set()
    while q:
        sink = q.popleft();
        if not sink.function in f_set:
            # Sink depend on a function not allready in set
            f_set.add(sink.function);
            q.extend(source.sink for source in sink.function.sources);
        else: sources.append(sink);

    return f_set

def calculate_runorder(impl):
    f_set = calculate_reachable_functions(impl.method.internal_sinks)
    helper = dict()
    return sorted(f_set,key=lambda a : a.depth(helper));        


class DataFlowVisitor (object):

    def __init__(self):
        self._methods = dict()

    def visit(self,method):
        if method in self._methods:
            return self._methods[method]
        impl = method.impl
        runorder = calculate_runorder(impl)
        
        results = self.setup(method);
        for function in runorder:
            sinks_results = (results[s.sink] for s in function.sources)
            source_results = self.merge(function,sinks_results)
            results.update(self.apply(function,source_results))
        ret_method = self.final(method,results)
        self._methods[method] = ret_method
        return ret_method

    def setup(self,method):
        """
        Recieves a method and for each source, returns a dict/list of start
        information Sink -> Info
        """
        pass
    
    def merge(self,function,sinks):
        """
        Recieves the results from sinks to a function and returns the resulting
        values for the sources for the new function
        """
        pass

    def apply(self,function,sources):
        """
        For each function take the sources and retrun the sinks
        the sources are slot oriented. The output sinks should orderd in 
        a dict.
        """
        pass

    def final(self,method,sinks):
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
            return method
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

