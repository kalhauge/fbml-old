"""
Module: Flow
"""


class Flow (object):
    def __init__(self,methods,impls):
        self._methods = methods

    def getMethod(self,ID):
        return self._methods[ID];

    @staticmethod
    def parse(filename):
        from flowparser import FlowParser
        return FlowParser(filename).createFlow();


class Method (object):
    def __init__(self,ID,sources,sinks):
        self._id = ID;
        self._sinks = sinks;
        self._sources = sources;
        self._impl = None;

    def __repr__(self):
        return '<method id="'+self._id+'">'

    def __str__(self):
        return 'Method "{}" : ({}) -> ({})'.format(
                self._id,
                ", ".join(self._sources),
                ", ".join(self._sinks))

    def getSources(self):
        return self._sources

    def addImpl(self, impl):
        self._impl = impl;

    def getImpl(self):
        return self._impl;

class Impl (object):
    def __init__(self,method,functions,sinks):
        self._method = method;
        self._functions = functions
        self._sinks = sinks;                

    def __repr__(self):
        return '<impl method={!r} functions={} sinks={}>'.format(
                self._method,
                len(self._functions),
                len(self._sinks))

class Function (object):
    def __init__(self,sid,sources,sinks):
        self._id = sid;
        self._sinks = sinks;
        self._sources = sources;
        self.connect();

    def connect(self):
        for i,sink in enumerate(self._sinks):
            sink.addFunction(self,i);
        for i,source in enumerate(self._sources):
            source.addFunction(self,i);

class Sink (object):
    def __init__(self,sid):
        self._id = sid;
        self._function = None
        self._slot = None
    
    def addFunction(self,function,slot):
        self._function = function;
        self._slot = slot;

    def __repr__(self):
        return '<sink id="'+self._id+'">'
class Source (object):
    def __init__(self,sink):
        self._sink = sink;

    def addFunction(self,function,slot):
        self._function = function;
        self._slot = slot;

    def __repr__(self):
        return '<source sink="'+self._sink+'">'
