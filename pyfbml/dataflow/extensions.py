from flow import Extension


class MethodNameExtension (Extension):
    def __init__(self):
        Extension.__init__(self);
        self.setName("MethodName");

    def parseExtension(self,tree,obj):
        self.set(obj,tree.text)


stdexts = {
    'MethodName' : MethodNameExtension,
    }
