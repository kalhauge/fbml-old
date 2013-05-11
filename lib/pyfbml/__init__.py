"""
Module: pyfbml
Author: Christian Gram Kalhauge

This module controlls the pyfbml interface.
"""

class MallformedFlowError (Exception) : pass





def Setup():
    """ Returns an instance of the LazyVisitor """
    import visitors
    global Visitor;
    Visitor = visitors.Visitor
    

def parseFlow(filename):
    from flow import Flow
    return Flow.parse(filename);


Setup();
