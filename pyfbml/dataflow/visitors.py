

def calculateRunorder(impl):
    from collections import deque
    sinks = impl.getMethod().getSinks()
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

    
    helper = dict()
    return sorted(f_set,key=lambda a : a.depth(helper));        


class DataFlowVisitor (object):

    def __init__(self):
        self._data = dict();

    def visit(self,impl):
        runorder = calculateRunorder(impl)
        self.setup(impl.getMethod());
        for function in runorder:
            f_sinks = [source.getSink() for source in function.getSources()]
            self.set(function,self.merge(f_sinks))

            result = self.apply(function)
            for sink in function.getSinks():
                self.set(sink,result);
        return self.merge(sinks);

    def setup(self,method):
        pass

    def merge(self,sinks):
        pass

    def apply(self,function):
        pass

    def set(self,obj,data):
        self._data[obj]=data;

    def get(self,obj):
        return self._data[obj];

class ControlFlowVisitor (object):

    def __init__(self):
        self._data = dict()

    def visit(self,impl):
        runorder = calculateRunorder(impl)
        result = self.setup(impl.getMethod())
        for function in runorder:
            result = self.apply(function,result)

        return self.final(result)

    def setup(self, method):
        pass 

    def apply(self, function,result):
        pass

    def final(self, result):
        pass

    def set(self,obj,data):
        self._data[obj]=data;

    def get(self,obj):
        return self._data[obj];
