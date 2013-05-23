"""
.. module:: pyfbml
    :platform: Unix
    :synopsis: This module controlls the pyfbml interface.


.. moduleauthor: Christian Gram Kalhauge
"""

class MallformedFlowError (Exception) : pass

def Setup():
    """ Returns an instance of the LazyVisitor """
    import visitors
    global Visitor;
    Visitor = visitors.Visitor

def getExtensions(*args):
    from extensions import stdexts;
    return dict([(a,stdexts[a]())for a in args]);

def parseFlow(filename,extensions):
    from flowparser import FlowParser
    return FlowParser(filename,extensions).createFlow();


Setup();
