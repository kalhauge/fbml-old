

class FlowError(Exception) : pass
class MallformedFlowError (FlowError) : pass

class AmbiguousMethodCall(FlowError):

    def __init__(self,methods,condition):
        super(AmbiguousMethodCall,self).__init__(
                "Ambiguous call for methods: {} on condition: {}".format(methods,condition))

class NoMethodCall(FlowError):

    def __init__(self,condition):
        super(NoMethodCall,self).__init__(
                "No methods found for call on condition: {}".format(condition))


