"""
.. module:: fbml.model

.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

Model
=====

This module contains the dataflow model. The dataflow model contains of three main
classes the :class:`~fbml.model.Method`, the :class:`~fbml.model.Impl`, and the
:class:`~fbml.model.Module` class.


Method
------
.. autoclass:: fbml.model.Method
    :members:

Implementation
--------------
.. autoclass:: fbml.model.Impl
    :members:

.. autoclass:: fbml.model.NoneImpl
    :members:

Internal classes
................

.. autoclass:: fbml.model.Function
    :members:

.. autoclass:: fbml.model.Sink
    :members:

.. autoclass:: fbml.model.Source
    :members:

Module
------

.. autoclass:: fbml.model.Module
    :members:

Package
.......

.. autoclass:: fbml.model.Package
    :members:

.. autoclass:: fbml.model.RootPackage
    :members:

"""

from .util import exceptions

def tuble (obj):
    return (obj.getId(),obj)

class Module (object):

    def __init__(self,name,package):
        self._extensions = set() 
        self._methods = dict()
        self._name = name
        self._package = package 

    def setMethods(self,methods):
        for method in methods:
            self.setMethod(method)
        return self

    def setImports(self,imports):
        self._imports = list(imports)
        return self

    def getImports(self):
        return self._imports

    def getMethod(self,ID):
        return self._methods[ID];

    def setMethod(self,method):
        self._methods[method.getInternalId()] = method
        method.setModule(self)
        return self

    def getMethodsWhere(self,matcher):
        results = [method for method in self.getMethods() if matcher.matches(method)]
        for imp in self.getImports():
            results.extend(imp.getMethodsWhere(matcher))
        return results

    def getMethodWhere(self,matcher):
        results = self.getMethodsWhere(matcher)
        if len(results) > 1: 
            raise exceptions.AmbiguousMethodCall(results,matcher)
        elif len(results) == 0:
            raise exceptions.NoMethodCall(matcher)
        return results[0]
    
    def getMethods(self):
        return self._methods.values()

    def getExtensions(self):
        return self._extensions

    def setExtensions(self,ext):
        self._extensions = set(ext)

    def getId(self,name):
        return self.getName() + "." + name

    def getName(self):
        return self._package.getId(self._name)

    def __str__(self):
        return self.getName()

    def __repr__(self):
        return "<Module at {}>".format(self.getName())


class Package (object):
    
    def __init__(self,name,package):
        self._modules = {} 
        self._subpackages = {}
        self._name = name
        self._package = package

    def getName(self):
        return self._package.getId(self._name)

    def getId(self,name):
        return self.getName() + "." + name

    def getPackage(self,name):
        if not name in self._subpackages:
            self._subpackages[name] = Package(name,self)
        return self._subpackages[name]

    def getModule(self,name):
        if not name in self._modules:
            self._modules[name] = Module(name,self)
        return self._modules[name]

    def __str__(self):
        return self.getName()

class RootPackage (Package):

    def __init__ (self):
        self._modules = {}
        self._subpackages = {}
    
    def getName(self):
        return "(root)" 

    def getId(self,name):
        return name




class ModelObject (object): pass
class ExtendableModelObject(ModelObject):

    """
    The ExtendableModelObject allows the object to be extendable, with extensions.
    """
    def __init__(self):
        self._extensions = dict()

    def setExtensions(self,extensions):
        self._extensions = dict((ext.getName(),ext) for ext in extensions)
        return self

    def setExtension(self,name,item):
        self._extensions[name] = Extend(name,item)
        return self

    def getExtension(self,name):
        return self._extensions[name].getData()

    def getExtensions(self):
        return self._extensions

    def __getitem__(self,name): 
        return self.getExtension(name)

    def __setitem__(self,name,item):
        return self.setExtension(name,item)

        
class Method (ModelObject):

    """
    The Method is the main id holder of the model, it controls the details
    about the requirements and ensurances of the execution of the function.

    :param ID: the ID of the method
    :param requirements: the requirements of the method.
    :param ensurances: the ensurences of the method.
    """
    def __init__(self,ID,requirements={},ensurances={}):
        self._id = ID;
        self._requirements = dict(requirements)
        self._ensurances = dict(ensurances)
        self._impl = NoneImpl() 

    def setModule(self,module):
        self._module = module
        return self

    def getModule(self):
        return self._module

    def getInternalId(self):
        return self._id

    def getId(self):
        """
        :returns: the id of the method
        """
        return self.getModule().getId(self.getInternalId())
    
    def getRequirements(self):
        """
        :returns: the requirements of the method
        """
        return self._requirements

    def getRequirement(self,name):
        """
        :returns: the requirement corresponding to the name
        """
        return self.getRequirements()[name].getData()

    def getEnsurances(self):
        """
        :returns: the ensurances of the method
        """
        return self._ensurances

    def getEnsurance(self,name):
        """
        :returns: the ensurance corresponding to the name
        """
        return self.getEnsurances()[name].getData()

    def setEnsurance(self,name,data):
        self.getEnsurances()[name] = Ensure(name,data)
        return self

    def addEnsurances(self,ensurances):
        """
        :param ensurances: a sequence of ensurances
        """
        self.getEnsurances().update((ens.getName(),ens) for ens in ensurances)
        return self

    def addRequirements(self,requirements):
        """
        :param requirements: a sequence of requirements
        """
        self.getRequirements().update((req.getName(),req) for req in requirements)
        return self

    def getSources(self):
        """
        Returns a list of orderet names of the sources.
        """
        impl = self.getImpl()
        sources = self.getRequirement('Sources')
        ret_list = [None] * len(sources)
        for i,s in sources.items():
            ret_list[i] = impl.getSink(s)
        return ret_list

    def getSinks(self):
        """
        Returns a list of orderet :class:`~fbml.model.Sink`s 
        """
        impl = self.getImpl()
        sinks = self.getEnsurance('Sinks')
        ret_list = [None] * len(sinks)
        for s,i in sinks.items():
            ret_list[i] = impl.getSink(s) 
        return ret_list

    def setImpl(self,impl):
        self._impl = impl
        return self

    def hasImpl(self):
        """
        :returns: ``True`` if the method, has an :class:`~fbml.model.Impl`
        """
        return not isinstance(self._impl,NoneImpl) 

    def getImpl(self):
        """
        :retruns: the implementation, might be of type :class:`~fbml.model.NoneImpl`
        """
        return self._impl

    def __repr__(self):
        return '<method id="'+self.getId()+'">'

    def __str__(self):
        return 'Method "{}" : ({}) -> ({})'.format(
                self.getId(),
                ", ".join(i for i in self.getRequirement('Sources').values()),
                ", ".join(i for i in self.getEnsurance('Sinks')))



class Impl (ModelObject):

    """
    This is the implementation of the method.

    :param method:
        the method to implement.
    
    :param functions: 
        a sequence containing elements of type :class:`~fbml.model.Function`,
        the default is an empty list.
    
    :param sinks:
        a sequence containing elements of type :class:`~fbml.model.Sink`,
        the default is an empty list.

    """

    def __init__(self,method,functions=[],sinks={}):
        self._method = method.setImpl(self)
        self._functions = list(functions)
        self._sinks = dict(sinks)


    def addFunctions(self,functions):
        """
        Adds functions to the implementation

        :param functions: 
            a sequence of type :class:`~fbml.model.Function`
        """
        self._functions.extend(functions)
        return self

    def addSinks(self,sinks):
        """
        Adds sinks to the implementation

        :param functions: 
            a sequence of type :class:`~fbml.model.Sink`
        """
        self._sinks.update((sink.getId(),sink) for sink in sinks)
        return self

    def getSink(self,sid):
        """
        The method to uses to get any sink in the used in the implementation.
        
        :param sid:
            the sid of the :class:`~fbml.model.Sink` that should be 
            found.
        
        :returns: the :class:`~fbml.model.Sink`, with id ``sid`` 
        """ 
        return self._sinks[sid]

    def getFunctions(self):
        """
        :returns: the functions used in the implementation.
        """
        return self._functions

    def getSinks(self):
        """
        :returns: the sinks used in the implementations.
        """
        return self._sinks

    def getMethod(self):
        """
        :returns: the implemented :class:`~fbml.model.Method`
        """
        return self._method

    def __repr__(self):
        return '<impl method={!r} functions={} sinks={}>'.format(
                self._method,
                len(self._functions),
                len(self._sinks))


class NoneImpl (Impl):
    """
    A None implementations, indicating no implementation. 
    """
    def __init__(self) : pass

class Function (ExtendableModelObject):
    """
    The function is the function call of fbml. Its primary function is to 
    provide data to help determine which method to be used on the sources,
    of the function to generate the data supoced to go to the sinks.

    :param sid:
        the id of the function, which is used to identify the function later
        and when associating extentions to it.

    """
    def __init__(self,sid,sources=[],sinks=[]):
        super(Function,self).__init__()
        self._id = sid;
        self._sinks = list(sinks)
        self._sources = list(sources)

    def connect(self):
        for sink in self._sinks:
            sink.addFunction(self);
        for source in self._sources:
            source.addFunction(self);

    def addSinks(self,sinks):
        self._sinks.extend(sinks)

    def addSources(self,sources):
        self._sources.extend(sources)

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


class Sink (ExtendableModelObject):
    def __init__(self,sid,slot):
        super(Sink,self).__init__()
        self._id = sid;
        self._slot = slot
        self._function = None
        self._users = [];
    
    def addFunction(self,function):
        self._function = function;

    def getFunction(self):
        return self._function;

    def __repr__(self):
        return '<sink id="'+self._id+'">'

    def getId(self):
        return self._id

    def getSlot(self):
        return self._slot

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

class Source (ExtendableModelObject):
    def __init__(self,sink,slot):
        super(Source,self).__init__()
        self._sink = sink;
        self._slot = slot;
        sink.addUser(self);

    def addFunction(self,function):
        self._function = function;

    def getSink(self):
        return self._sink;

    def getSlot(self):
        return self._slot
    
    def getFunction(self):
        return self._function

    def __repr__(self):
        return '<source sink={} extend={}> '.format(self._sink,self.getExtensions());

    def depth(self,helper):
        if not self in helper:
            helper[self] = self.getSink().depth(helper) + 1;
        return helper[self]



class Extend (ModelObject):

    def __init__(self,name,data):
        self._name = name
        self._data = data

    def getName(self):
        return self._name

    def getData(self):
        return self._data

class Ensure (Extend) : pass
class Require (Extend) : pass 
