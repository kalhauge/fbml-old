"""
Module: pyfbml
Author: Christian Gram Kalhauge

This module controlls the pyfbml interface.
"""

class MallformedFlowError (Exception) : pass

def parseFlow(filename):
    from flow import Flow
    return Flow.parse(filename); 
