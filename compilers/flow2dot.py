"""
Compiler : flow2dot 

This is the simple flow to dot compiler wich takes a .fl file
and produces dot code. 
"""

# Lets start out by importing pyflow 
import sys
sys.path.append('/Users/christian/Develop/Projects/2013/FlowLang');
import pyflow 
import argparse

def fail(msg):
    import sys;
    print "Failed: " + str(msg);
    sys.exit(-1);

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('filename',help='the file to compile');

args = parser.parse_args();

try: flow = pyflow.parse(args.filename);
except pyflow.FlowParseError as error:
    fail(error.getMessage());

try: main = flow.getMethodFromId('main').getLattice();
except pyflow.FlowError as e: fail(e)
else:
    pass;
