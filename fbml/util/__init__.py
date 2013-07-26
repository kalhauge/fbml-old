


def readonly(name):
    return property(lambda self: getattr(self,name))

