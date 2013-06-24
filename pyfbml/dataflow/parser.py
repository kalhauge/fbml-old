"""
.. module:: pyfbml.dataflow.parser

"""
class ParseObject(object):
    
    def __init__(self,**kargs):
        for k,v in kargs.items():
            setattr(self,k,v)
        self.check()

    def check(self):
        attributes = self.requriedAttributes()
        for attr in attributes:
            if not hasattr(self,attr):
                raise MallformedFlowError(
                    "{} needs the attribute {}".format(self,attr)
                    )

    def __repr__(self):
        return "<{} attr: {}>".format(self.__class__.__name__,vars(self))


class ExtendableParseObject (ParseObject):

    def setExtends(self,seq):
        self.extends = list(seq)


class Module(ParseObject):

    def requriedAttributes(self): return ['version']

    def setImports(self,seq):
        self.imports = list(seq) 

    def setExtensions(self,seq):
        self.extensions = list(seq)

    def setMethods(self,seq):
        self.methods = list(seq)

    def setImpls(self,seq):
        self.impls = list(seq)

class Method(ParseObject): 

    def requriedAttributes(self): return ['id']

    def setRequirements(self,seq):
        self.requirements = list(seq)

    def setEnsurances(self,seq):
        self.ensurances = list(seq)


class Impl(ParseObject):

    def requriedAttributes(self): return ['method_id']

    def setFunctions(self,seq):
        self.functions = list(seq)


class Function(ExtendableParseObject):
   
    def requriedAttributes(self): return ['id']
    
    def setSinks(self,seq):
        self.sinks = list(seq)

    def setSources(self,seq):
        self.sources = list(seq)


class Sink(ExtendableParseObject):
    def requriedAttributes(self): return ['id','slot']

class Source(ExtendableParseObject): 
    def requriedAttributes(self): return ['sink_id','slot']

class Require(ParseObject):
    def requriedAttributes(self): return ['name']

class Ensure(ParseObject):
    def requriedAttributes(self): return ['name']

class Extend(ParseObject):
    def requriedAttributes(self): return ['name']


