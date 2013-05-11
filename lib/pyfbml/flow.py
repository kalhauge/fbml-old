"""
Module: Flow
"""
from __init__ import MallformedFlowError;

class Flow (object):
    def __init__(self,methods,extensions):
        self._methods = methods
        self._extensions = extensions

    def getMethod(self,ID):
        return self._methods[ID];

    def getExtension(self,name):
        return self._extensions[name];
    
    @staticmethod
    def parse(filename):
        from flowparser import FlowParser
        return FlowParser(filename).createFlow();

class Extension (object):
    def __init__(self):
        self._data = dict()
    
    def setName(self,name):
        self._name = name

    def getName(self):
        return self._name

    def parseExt(self,ext,obj):
        if ext.attrib['type'] != obj.getType():
            raise MallformedFlowError(
                    "Type {} different from {}".format(
                        ext.attrib['type'], obj));
        self.parseExtension(ext,obj);

    def set(self,obj,data):
        self._data[obj] = data;

    def get(self,obj):
        try: return self._data[obj]
        except KeyError as e:
            raise MallformedFlowError("No extendsion data for " + str(obj))

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

    def getSinks(self):
        return self._sinks

    def addImpl(self, impl):
        self._impl = impl;

    def getImpl(self):
        return self._impl;

    def getType(self): return "method"

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


    def getSink(self,sid):
        return self._sinks[sid]

    def getFunctions(self):
        return self._functions

    def getMethod(self):
        return self._method

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

    def getSources(self):
        return self._sources;

    def getSinks(self):
        return self._sinks;

    def getId(self):
        return self._id;

    def __repr__(self):
        return '<function id="{}" >'.format(self._id);

    def depth(self,helper):
        if not self in helper:
            if len(self.getSources()) == 0: depth = 0;
            else: depth = max(src.depth(helper) for src in self.getSources()) +1
            helper[self] = depth;
        return helper[self]

    def getType(self): return "function"

class Sink (object):
    def __init__(self,sid):
        self._id = sid;
        self._function = None
        self._slot = None
        self._users = [];
    
    def addFunction(self,function,slot):
        self._function = function;
        self._slot = slot;

    def getFunction(self):
        return self._function;

    def __repr__(self):
        return '<sink id="'+self._id+'">'

    def getId(self):
        return self._id

    def addUser(self,source):
        self._users.append(source);

    def getUsers(self):
        return self._users;

    def depth(self,helper):
        if not self in helper:
            if self.getFunction() is None: depth = 0;
            else: depth = self.getFunction().depth(helper) + 1;
            helper[self] = depth;
        return helper[self]

    def getType(self): return "sink"

class Source (object):
    def __init__(self,sink):
        self._sink = sink;
        sink.addUser(self);

    def addFunction(self,function,slot):
        self._function = function;
        self._slot = slot;

    def getSink(self):
        return self._sink;

    def getFunction(self):
        return self._function

    def __repr__(self):
        return '<source sink={} > '.format(self._sink);

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.getSink().depth(helper) + 1;
        return helper[self]

