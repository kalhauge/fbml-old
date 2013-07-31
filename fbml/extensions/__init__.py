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
        return self.__class__.XML_FORMATS

    def tuble(self):
        return (self.name(),self)

    def __repr__(self):
        return "<Extension '{}' formats = {}>".format(self.NAME,self.XML_FORMATS)


from . import type, methodname,  llvm

extensions = [
        type.TypeExtension(), 
        methodname.MethodNameExtension(),
        llvm.LLVMExtension(),
        ] 

named_extensions = dict(ext.tuble() for ext in extensions)
