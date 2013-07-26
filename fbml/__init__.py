"""
.. module:: fbml
    :platform: Unix
    :synopsis: This module controlls the pyfbml interface.

.. moduleauthor: Christian Gram Kalhauge
"""

class MallformedFlowError (Exception) : pass

import logging
log = logging.getLogger('fbml')

def setup():
    from .util import visitors
    global DataFlowVisitor;
    global ControlFlowVisitor
    ControlFlowVisitor = visitors.ControlFlowVisitor
    DataFlowVisitor = visitors.DataFlowVisitor

def get_extensions(names):
    """
    Returns some of the std extensions, form the names given
    in args
    """
    from .extensions import named_extensions 
    from .parsers.xmlformat import XMLExtensionFormats
    return XMLExtensionFormats(named_extensions[a].tuble() for a in names)

def root_from_environment(paths=None):
    import os
    if not paths: paths = []
    try: paths += os.environ['FBMLPATH'].split(':')
    except KeyError: log.warning('FBMLPATH not set')
    return structure.RootPackage(paths)

def get_builder(
        paths=None,
        root_package=None,
        extensions=None,
        parser=None):
    if not root_package: 
        root_package = root_from_environment(paths) 
    if not parser:
        extensions = list(extensions) if extensions else list()
        from .parsers import xmlformat
        parser = xmlformat.XMLParser(
                get_extensions(extensions + ['sources','sinks']))

    from . import core
    return core.Builder(root_package,parser)



def import_module(modulename,extension=None,paths=None):
    """
    This method imports a fmbl module. It uses the environemnt
    path $FBMLPATH to dertermine where to find the module.

    :param modulename: the name of the module, a dot sperated list
    :param paths: extra search paths beound the $FBMLPATH.
    :returns: A :class:`~fbml.model.Module`
    """

    paths.append(os.getcwd())
    
    from . import core 
    from .parsers import xmlformat
    builder = core.Builder(paths,xmlformat.XMLParser(extension))
    return builder.get_module(modulename).get()


def save_module(module,filelike,extensions):
    from .parsers import xmlformat
    return xmlformat.XMLWriter(extensions).write(module,filelike)
    
setup()
