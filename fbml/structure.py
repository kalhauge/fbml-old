"""
.. module:: fbml.structure
.. moduleauthor:: Christian Gram Kalhauge <s093273@student.dtu.dk>

=====
Structure
=====

"""

import os

import logging
log = logging.getLogger('fbml.structure')

from .util import readonly
from .util import exceptions

class Label (object):
    """
    Label is the identification of the package system
    :param name: The name of the object, found in the package.
    :param package: The package that the label is found in
    """

    def __init__(self, name, parrent):
        self._name = str(name)
        self._parrent = parrent

    # Make the name and package, get only variables..
    name = readonly('_name')
    parrent = readonly('_parrent') 

    def __repr__(self):
        return '.'.join(self.to_name_list()) 

    def to_name_list(self):
        return self.parrent.to_name_list() + [self.name]

    def get(self):
        return self.parrent.children[self.name]

    @staticmethod
    def from_string(label_string, root_package, factory):
        """ 
        Creates a string from an label string and the root package

        :param label_string: a string representing the Label. The format
            is a dot seperated list of names. 
        :param root_package: is the root package controling the names
            and position of the following packages
        """
        name_list = label_string.split('.')
        return root_package.find_or_make(name_list,factory).label

            
class Namespace (object):

    def __init__(self,label):
        self._label = label
        self._children = dict() 

    label = readonly('_label')

    @property
    def parrent(self):
        return self.label.parrent

    @property
    def children(self):
        return dict(self._children)

    def find_or_make(self, name_list, factory):
        """
        Finds or make a label from a list using a
        factory
        """
        if not name_list: return self.label
        try:
            subpackage = self.find(name_list[0])
        except KeyError:
            log.debug("Subpackage %s not found, try to create",
                    name_list[0])
            subpackage = self.make(name_list[0],factory)
            
        return subpackage.find_or_make(name_list[1:],factory)

    def find(self, name):
        """
        Returns a local attribute from a name.
        :param name: the name of the attribute
        """
        return self.children[name]

    def find_from_name_list(self, name_list):
        """ Returns the label, by searching through the structure tree
        recursively

        :param name_list: the list of names to find the label in the 
            subtree
        :raises: KeyError if problem occurs with the language
        """
        if not name_list: 
            return self
        else: 
            return self.find(name_list[0]).find_from_name_list(name_list[1:]) 

    def to_name_list(self):
        """ returns the name list of the package """
        return self._label.to_name_list()

    def make(self, name, child_factory):
        """
        This method enables the user to register a child to a package
        :param name: The name that the child should have
        :param child_factory: a function that creates the child using an
           label 
        """
        child_label = Label(name,self)
        if name in self._children:
            raise KeyError(name + " already in children: " + str(child_label.get()))
        self._children[child_label.name] = child_factory(child_label)
        return child_label.get() 

    @property
    def with_names(self):
        return iter(self.children.items())
    
    @property
    def names(self):
        return iter(self.children)

    def __getitem__(self,name):
        return self.find_from_name_list(name.split('.'))

    def __iter__(self):
        return iter(self.children.values())

    def __repr__(self):
        return repr(self.label)

class Package (Namespace):
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

    paths = readonly('_paths')

    def get_paths_from_name(self, name):
        """
        Returns a generator of acceptable paths with the basename of
        name, form the package.
        :param name: the basename of the files and directories wanted
        """
        posible_names = [os.path.join(path,name) for path in self.paths]
        posible_names += [path + '.fl' for path in posible_names] 
        return filter(lambda fname: os.path.exists(fname), posible_names)

    def __repr__(self):
        return repr(self.label)


class RootPackage (Package):
    """
    The root package is the lowest package in the struckture, and
    has no name
    """

    def __init__(self,paths):
        self._children = dict()
        self._paths = paths

    def to_name_list(self):
        return []

    def __repr__(self):
        return 'root'

class Module (Package):
    """
    The module is the top-level container of the structure. The module 
    contains the methods of the program. The model is a package, but 
    should not contain any subpackages.
    """

    def __init__(self, paths, label, imports):
        super(Module,self).__init__(paths=paths,label=label) 
        self._imports = list(imports)

    label   = readonly('_label')
    imports = readonly('_imports')

    @property
    def methods(self):
        return self._children.values()

    def make_method(self, name, factory):
        return self.make(name, factory) 

    def get_methods_where(self,matcher):
        results = [method for method in self.methods if matcher.matches(method)]
        for imp in self.imports:
            results.extend(imp.get_methods_where(matcher))
        return results

    def get_method_where(self,matcher):
        results = self.get_methods_where(matcher)
        if len(results) > 1: 
            raise exceptions.AmbiguousMethodCall(results,matcher)
        elif not results:
            raise exceptions.NoMethodCall(matcher)
            
        return results[0]

    def find_or_make(self, name_list, factory):
        """
        Since a module can not exist in a half build state
        there is no need to make any thing.

        """
        return self.find_from_name_list(name_list);

    def __repr__(self):
        return "<Module : {self.label}>".format(self=self)
