
def calculate_reachable_functions(sinks):
    from collections import deque 
    sources = []
    q = deque(sinks);
    f_set = set()
    while q:
        sink = q.popleft();
        if not sink.owner in f_set:
            # Sink depend on a function not allready in set
            f_set.add(sink.owner);
            q.extend(sink for sink in sink.owner.sources);
        else: sources.append(sink);

    return f_set

def calculate_runorder(impl):
    f_set = calculate_reachable_functions(impl.method.targets)
    helper = dict()
    return sorted(f_set,key=lambda a : a.depth(helper));        


class DataFlowVisitor (object):

    def __init__(self):
        self._methods = dict()

    def visit(self,method):
        if method in self._methods:
            return self._methods[method]
        impl = method.impl

        # Calculates the runorder and then removes the method
        runorder = calculate_runorder(impl)[1:]
        
        results = dict(self.setup(method))
        for function in runorder:
            results.update(self.apply(function,results))
        ret_method = self.final(method,results)
        self._methods[method] = ret_method
        return ret_method

    def setup(self,method):
        """
        Recieves a method and for each source, returns a dict/list of start
        information Sink -> Info
        """
        pass

    def apply(self,function,sinks):
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
        runorder = calculate_runorder(method.impl)[1:]
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

