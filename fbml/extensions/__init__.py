"""

.. module :: fbml.extensions


"""


class Extension (object):
    """
    The Extension is the basic class to extend, when making an new
    extension.

    Should Implement the NAME and XML_FORMAT variable as least.
    """

    def getName(self):
        return self.__class__.NAME
    def getXMLFormatter(self):
        return self.__class__.XML_FORMAT

    def getDictTuble(self):
        return (self.getName(),self)



from . import type, methodname, sources, sinks, llvm


extensions = {
        "Type"       : type.TypeExtension,
        "MethodName" : methodname.MethodNameExtension,
        "Sources"    : sources.SourcesExtension,
        "Sinks"      : sinks.SinksExtension,
        "LLVM"       : llvm.LLVMExtension,
        }
