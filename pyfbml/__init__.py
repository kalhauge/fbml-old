"""
.. module:: pyfbml
    :platform: Unix
    :synopsis: This module controlls the pyfbml interface.

.. moduleauthor: Christian Gram Kalhauge
"""

class MallformedFlowError (Exception) : pass

import logging
log = logging.getLogger('pyfbml')

def Setup():
    from .dataflow import visitors
    global DataFlowVisitor;
    global ControlFlowVisitor
    ControlFlowVisitor = visitors.ControlFlowVisitor
    DataFlowVisitor = visitors.DataFlowVisitor

def getExtensions(*args):
    """
    Returns some of the std extensions, form the names given
    in args
    """
    from .dataflow.extensions import formatters 
    from .dataflow.xmlformat import XMLExtensionFormats
    args = list(args)
    args.extend(['Sources','Sinks'])
    return XMLExtensionFormats((a,formatters[a]()) for a in args)

def importModule(modulename,extension=None,paths=None):
    """
    This method imports a fmbl module. It uses the environemnt
    path $FBMLPATH to dertermine where to find the module.

    :param modulename: the name of the module, a dot sperated list
    :param paths: extra search paths beound the $FBMLPATH.
    :returns: A :class:`~pyfbml.dataflow.module.Module`
    """
    import os
    if paths is None: paths = []
    if extension is None: extension = {} 
    try: paths += os.environ['FBMLPATH'].split(':')
    except KeyError: log.warning('FBMLPATH not set')

    paths.append(os.getcwd())
    
    from .dataflow import module 
    from .dataflow import xmlformat
    env = module.BuildEnvironment(paths,xmlformat.XMLParser(extension))
    return module.build(modulename,env)


def saveModule(module,filelike,extensions):
    from .dataflow import xmlformat
    return xmlformat.XMLWriter(extensions).write(module,filelike)
    
Setup()
