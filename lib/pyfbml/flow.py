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
        from FlowParser import FlowParser
        return FlowParser(filename).createFlow();


class Method (object):

    def __init__(self,ID):
        self._id = ID;
        self._impl = None;

    def __repr__(self):
        return '<method id="'+self._id+'">'

    def addImpl(self, impl):
        self._impl = impl;

class Impl (object):
    def __init__(self,functions,sinks):
        self._functions = functions
        self._sinks = sinks;                

class Function (object):
    def __init__(self,sinks,sources):
        self._sinks = sinks;
        self._sources = sources;
        self.connect();

    def connect(self):
        for i,sink in enumerate(self._sinks):
            sink.addFunction(self,i);
        for i,source in enumerate(self._source):
            source.addFunction(self,i);

class Sink (object):
    def __init__(self,sid):
        self._id = sid;
    
    def addFunction(self,function,slot):
        self._function = function;
        self._slot = slot;

class Source (object):
    def __init__(self,sink):
        self._sink = sink;

    def addFunction(self,function,slot):
        self._function = function;
        self._slot = slot;

