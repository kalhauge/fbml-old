from collections import namedtuple

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

class Immutable(object):
    def __repr__(self):
        return (self.__class__.__name__ 
        + '(' + ', '.join(str(k) + "=" + repr(v) for k, v 
                    in self.items()) + ')'
                )

    def __setattr__(self,name,value):
        raise TypeError('All attributes is read-only in an immutable object')

    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
        self.__dict__['_hash'] = hash(self)

    def __hash__(self):
        if not hasattr(self,'_hash'):
            return hash(tuple(sorted(self.items()))) 
        else: return self._hash

    def items(self):
        return ((k,v) for k, v in vars(self).items() 
                    if not k.startswith('_'))

    def __eq__(self,other):
        return tuple(sorted(self.items())) == tuple(sorted(other.items()))

def namedtuple_from_dict(name, d):
    return namedtuple(name,list(d))(**d)
