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
    """ Returns an instance of the LazyVisitor """
    import visitors
    global Visitor;
    Visitor = visitors.Visitor

def getExtensions(*args):
    from .dataflow.extensions import stdexts;
    return dict([(a,stdexts[a]())for a in args]);

def importModule(modulename,paths=None,extension=None):
    """
    This method imports a fmbl module. It uses the environemnt
    path $FBMLPATH to dertermine where to find the module.

    :param modulename: the name of the module, a dot sperated list
    :param paths: extra search paths beound the $FBMLPATH.
    :returns: A :class:`~pyfbml.dataflow.model.module`
    """
    import os
    if paths is None: paths = []
    if extension is None: extension = []
    try: paths += os.environ['FBMLPATH'].split(':')
    except KeyError: log.warning('FBMLPATH not set')
  
    from .dataflow import model
    from .dataflow import parser

    modulepath = modulename.split('.')
    
    parser.getModule(modulepath,paths)

