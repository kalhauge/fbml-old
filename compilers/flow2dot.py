"""
Compiler : flow2dot 

This is the simple flow to dot compiler wich takes a .fl file
and produces dot code. 
"""

# Lets start out by importing pyflow 
import sys
sys.path.append('/Users/christian/Develop/Projects/2013/fbml/lib');

import pyfbml 
import argparse

def fail(msg):
    import sys;
    print "Failed: " + str(msg);
    sys.exit(-1);

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('filename',help='the file to compile');
parser.add_argument('method_name',help='the method to print');

args = parser.parse_args();

flow = pyfbml.parseFlow(args.filename);

print(flow.getMethod(args.method_name));
