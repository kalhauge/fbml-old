"""
.. module:: pyfbml.dataflow.model

.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

Model
=====

This module contains the dataflow model. The dataflow model contains of two main
classes the :class:`~pyfbml.dataflow.model.Method` and the :class:`~pyfbml.dataflow.model.Impl`


Method
------
.. autoclass:: pyfbml.dataflow.model.Method
    :members:

Implementation
--------------
.. autoclass:: pyfbml.dataflow.model.Impl
    :members:

.. autoclass:: pyfbml.dataflow.model.NoneImpl
    :members:

Internal classes
................

.. autoclass:: pyfbml.dataflow.model.Function
    :members:

.. autoclass:: pyfbml.dataflow.model.Sink
    :members:

.. autoclass:: pyfbml.dataflow.model.Source
    :members:
"""

from .. import exceptions

class ModelObject (object): pass

class ExtendableModelObject(ModelObject):

    """
    The ExtendableModelObject allows the object to be extendable, with extensions.
    """

    def setExtensions(self,extensions):
        self._extensions = dict((ext.getName(),ext) for ext in extensions)
        return self

    def getExtension(self,name):
        return self._extensions[name].getData()

    def getExtensions(self):
        return self._extensions

    def __getitem__(self,name): 
        return self.getExtension(name)

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

    def getId(self):
        """
        :returns: the id of the method
        """
        return self._id
    
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
        """
        return [s for s in self.getRequirement('Sources').values()]

    def getSinks(self):
        """
        """
        impl = self.getImpl()
        return [impl.getSink(s) for s in self.getEnsurance('Sinks')]

    def setImpl(self,impl):
        self._impl = impl
        return self

    def hasImpl(self):
        """
        :returns: ``True`` if the method, has an :class:`~pyfbml.dataflow.model.Impl`
        """
        return not isinstance(self._impl,NoneImpl) 

    def getImpl(self):
        """
        :retruns: the implementation, might be of type :class:`~pyfbml.dataflow.model.NoneImpl`
        """
        return self._impl

    def __repr__(self):
        return '<method id="'+self._id+'">'

    def __str__(self):
        return 'Method "{}" : ({}) -> ({})'.format(
                self._id,
                ", ".join(i for i in self.getSources().values()),
                ", ".join(i for i in self.getSinks()))



class Impl (ModelObject):

    """
    This is the implementation of the method.

    :param method:
        the method to implement.
    
    :param functions: 
        a sequence containing elements of type :class:`~pyfbml.dataflow.model.Function`,
        the default is an empty list.
    
    :param sinks:
        a sequence containing elements of type :class:`~pyfbml.dataflow.model.Sink`,
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
            a sequence of type :class:`~pyfbml.dataflow.model.Function`
        """
        self._functions.extend(functions)
        return self

    def addSinks(self,sinks):
        """
        Adds sinks to the implementation

        :param functions: 
            a sequence of type :class:`~pyfbml.dataflow.model.Sink`
        """
        self._sinks.update((sink.getId(),sink) for sink in sinks)
        return self

    def getSink(self,sid):
        """
        The method to uses to get any sink in the used in the implementation.
        
        :param sid:
            the sid of the :class:`~pyfbml.dataflow.model.Sink` that should be 
            found.
        
        :returns: the :class:`~pyfbml.dataflow.model.Sink`, with id ``sid`` 
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
        :returns: the implemented :class:`~pyfbml.dataflow.model.Method`
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
        return '<source sink={} > '.format(self._sink);

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
