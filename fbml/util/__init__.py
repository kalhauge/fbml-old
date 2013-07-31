
def readonly(name):
    return property(lambda self: getattr(self,name))

import logging
def log_it(log_func):
    def factory(function):
        def log_function(*args, **kwds):
            log_func("%s called with %s , %s",function.__name__,args,kwds)
            ret = function(*args, **kwds)
            log_func("%s returned %s",function.__name__,ret)
            return ret
        return log_function
    return factory
