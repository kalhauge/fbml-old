"""

.. module :: fbml.extensions


"""


class Extension (object):
    """
    The Extension is the basic class to extend, when making an new
    extension.

    Should Implement the NAME and XML_FORMAT variable as least.
    """

    def name(self):
        return self.__class__.NAME

    def xml_formatter(self):
        return self.__class__.XML_FORMAT

    def tuble(self):
        return (self.name(),self)



from . import type, methodname, sources, sinks, llvm


extensions = [
        type.TypeExtension(), 
        methodname.MethodNameExtension(),
        sources.SourcesExtension(),
        sinks.SinksExtension(),
        llvm.LLVMExtension(),
        ] 

named_extensions = dict(ext.tuble() for ext in extensions)
