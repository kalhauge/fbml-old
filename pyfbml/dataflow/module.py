"""
.. module: pyflow.dataflow.module
    :platform: Unix
    :synopsis: The dataflow.module module. This is used for all assosiations.
.. moduleauthor: Christian Gram Kalhauge

"""

class Id (object):
    def __init__(self,module,name):
        self._module = module;
        self._name = name;

    def __repr__(self):
        return "'{}'".format((module.getIname));

class Module (object):
    def __init__(self,name,parent=None):
        self._extensions = [] 
        self._methods = []
        self._name = name
        self._parrent = parrent

    def getMethod(self,ID):
        return self._methods[ID];

    def getExtension(self,name):
        return self._extensions[name];

    def getId(self,name):
        return self.getModuleName() + "." + name

    def getModuleName(self):
        if not self._parrent is None:
            return self._name
        else: 
            return self._parrent + "." + self._name
