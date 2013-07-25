"""
.. module:: fbml.model
.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

=====
Structure
=====

"""

import os

class Label (object):
    """
    Label is the identification of the package system
    :param name: The name of the object, found in the package.
    :param package: The package that the label is found in
    """

    def __init__(self, name, parrent):
        self._name = name
        self._parrent = parrent

    # Make the name and package, get only variables..
    name = property(lambda self: self._name)
    parrent = property(lambda self: self._parrent)

    def __repr__(self):
        return '.'.join(self.get_name_list()) 

    def get_name_list(self):
        return self.parrent.get_name_list() + [self.name]

    def get(self):
        return self.parrent.children[self.name]

    @staticmethod
    def from_string(label_string, root_package):
        """ 
        Creates a string from an label string and the root package

        :param label_string: a string representing the Label. The format
            is a dot seperated list of names. 
        :param root_package: is the root package controling the names
            and position of the following packages
        """
        name_list = label_string.split('.')
        return root_package.get_label_from_name_list(name_list)

class Labelable (object):

    def __init__(self,label):
        self._label = label
        self._children = dict() 

    label = readonly('_label')
    children = property(lambda self: dict(self._children))

    def get_label_from_name(self, name):
        """
        Returns the label, given a name, if the name is know as one of 
        the children. Else is rasies a KeyError
        :param name: The name of the label to retrieve
        :raises: KeyError if name does not exist in children
        """
        if not name in self.children: 
            raise KeyError(repr(self) + ': No ' + name + ' in children')
        return Label(name, self)

    def get(self, name):
        return self.children[name]

    def get_label_from_name_list(self, name_list):
        """ Returns the label, by searching through the structure tree
        recursively

        :param name_list: the list of names to find the label in the 
            subtree
        :raises: KeyError if problem occurs with the language
        """
        if not name_list: return self.label
        subpackage = self.children[name_list[0]]
        return subpackage.get_label_from_name_list(name_list[1:])

    def get_name_list(self):
        """ returns the name list of the package """
        return self._label.get_name_list()

    def make(self, name, child_factory):
        """
        This method enables the user to register a child to a package
        :param name: The name that the child should have
        :param child_factory: a function that creates the child using an
           label 
        """
        child_label = Label(name,self)
        if name in self._children:
            raise KeyError(name + " already in children")
        self._children[child_label.name] = child_factory(child_label)
        return self._children[child_label.name]

class Package (Labelable):
    """
    Package is the core of the package system. A package unless if
    it is the root package is does always have a parrent.

    The Package is the link between the filesytem and the compiler,
    the package can reside in multible folders at the same time. But 
    the Module will choose the first of these filenames

    :param parrent: the parrent of the package
    """
    
    def __init__(self, label, paths):
        super(Package,self).__init__(label)
        self._paths = paths 

    #Read only
    paths = property(lambda self: self._paths)


    def get_paths_from_name(self, name):
        """
        Returns a generator of acceptable paths with the basename of
        name, form the package.
        :param name: the basename of the files and directories wanted
        """
        posible_names = (os.path.join(path,name) for path in self.paths)
        return filter(posible_names,lambda fname: os.path.exists(fname))

    def make(self,name_list,factory): 
        """
        Returns a new package the data which is created, from the
        new data. The functions raises a KeyError if the model already
        exists.
       
        :param name_list: The list of names, that the label should be
            created from
        :param factory: A function that given a list of valid paths 
            returns a function able to create a package or module
            using a label.
        """
        if name_list == []: return self.label
        paths = self.get_paths_from_name(name_list[0])
        child = self.make(name,factory(list(paths)))

        return child.make(name_list[1:],factory)
         

    def __repr__(self):
        return repr(self.package_label)


class RootPackage (Package):
    """
    The root package is the lowest package in the struckture, and
    has no name
    """

    def __init__(self,paths):
        self._children = dict()
        self._paths = paths

    def get_name_list(self):
        return []

    def __repr__(self):
        return 'root'

class Module (Labelable):
    """
    The module is the top-level container of the structure. The module 
    contains the methods of the program. The model is a package, but 
    should not contain any subpackages.
    """

    def __init__(self, label, imports):
        super(Module,self).__init__(label) 
        self._imports = list(imports)

    label = property(lambda self: self._label)
    imports   = property(lambda self: self._imports)

    make_method = Module.make

