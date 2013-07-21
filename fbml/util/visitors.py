
def calculateReachableFunctions(sinks):
    from collections import deque 
    sources = []
    q = deque(sinks);
    f_set = set()        
    while q:
        sink = q.popleft();
        function = sink.getFunction();
        if not function is None:
            if not function in f_set:
                # Sink depend on a function not allready in set
                f_set.add(function);
                q.extend(source.getSink() 
                        for source in function.getSources());
        else: sources.append(sink);

    return f_set

def calculateRunorder(impl):
    sinks = impl.getMethod().getSinks()
    f_set = calculateReachableFunctions(sinks)
    helper = dict()
    return sorted(f_set,key=lambda a : a.depth(helper));        


class DataFlowVisitor (object):

    def __init__(self):
        self._methods = dict()

    def visit(self,method):
        if method in self._methods:
            return self._methods[method]
        impl = method.getImpl()
        runorder = calculateRunorder(impl)
        initial_sink_results = self.setup(method);
        results = dict((s.getId(),initial_sink_results[s.getSlot()])
                        for s in method.getSources())
        for function in runorder:
            sinks_results = (results[s.getSink().getId()] 
                                for s in function.getSources())
            source_results = self.merge(function,sinks_results)
            results.update(self.apply(function,source_results))
        ret_method = self.final(method,results)
        self._methods[method] = ret_method
        return ret_method

    def setup(self,method):
        """
        Recieves a method and for each source, returns a dict/list of start
        information
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
        For each function take the sources and retun the sinks
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
        impl = method.getImpl()
        runorder = calculateRunorder(impl)
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

