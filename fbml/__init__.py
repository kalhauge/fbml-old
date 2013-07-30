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
    Returns some of the std extensions, from the names given
    in args
    """
    from .extensions import named_extensions 
    return [named_extensions[a] for a in names]

def root_from_environment(paths=None):
    import os
    from fbml import structure
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
                get_extensions(extensions))

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
    extends = get_extensions(extensions)
    return xmlformat.XMLWriter(extends).write(module,filelike)
    
setup()
