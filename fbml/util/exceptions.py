class FbmlError(Exception) : pass
class MallformedFlowError (FbmlError) : pass

class BadLabelAccess (FbmlError):

    def __init__(self,obj,  name):
        super(BadLabelAccess,self).__init__(
                "Bad access to {name} in {obj}".format(**locals()))


class AmbiguousMethodCall(FbmlError):

    def __init__(self,methods,condition):
        super(AmbiguousMethodCall,self).__init__(
                "Ambiguous call for methods: {} on condition: {}".format(methods,condition))


class NoMethodCall(FbmlError):

    def __init__(self,methods):
        super(NoMethodCall,self).__init__(
                "No methods found for call in {}".format(methods))

