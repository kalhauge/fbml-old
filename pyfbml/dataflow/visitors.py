class Visitor (object):

    def __init__(self):
        self._data = dict();

    def visit(self,impl):
        from collections import deque
        from pprint import pprint
        sinks = [impl.getSink(sid) for sid in impl.getMethod().getSinks()]
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
        runorder = sorted(f_set,key=lambda a : a.depth(helper));        

        self.setup(sources);
        for function in runorder:
            f_sinks = [source.getSink() for source in function.getSources()]
            self.set(function,self.merge(f_sinks))

            result = self.apply(function)
            for sink in function.getSinks():
                self.set(sink,result);
        return self.merge(sinks);

    def setup(self,method_sources):
        pass

    def merge(self,sinks):
        pass

    def apply(self,function):
        pass

    def set(self,obj,data):
        self._data[obj]=data;

    def get(self,obj):
        return self._data[obj];


