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

method = flow.getMethod(args.method_name);
impl = method.getImpl();

class DotVisitor (pyfbml.Visitor):
    
    def setup(self,method_sources):
        for sink in method_sources:
            self.set(sink,[]);

    def merge(self,sinks):
        result = [];
        for sink in sinks:
            result.extend(self.get(sink));
        from collections import OrderedDict
        return list(OrderedDict.fromkeys(result));

    def apply(self,function):
        in_str = "|".join(["<source_{}>".format(s.getSink().getId()) 
                        for s in function.getSources()]);
        out_str = "|".join(["<sink_{}>".format(s.getId()) 
                        for s in function.getSinks()]);
        function_str= '{}[label="{{{}}}"];'.format(
            function.getId(),
            '{} {} {}'.format(
               '{{{}}} |'.format(in_str) if not in_str is '' else '',
               function.getId(),
               '| {{{}}}'.format(out_str) if not out_str is '' else '',
               )
            )

        connections = ['"{}":sink_{} -> "{}":source_{};'.format(
            sink.getFunction().getId(),
            sink.getId(),
            function.getId(),
            sink.getId()) for sink in 
            (source.getSink() for source in function.getSources())
                if not sink.getFunction() is None];


        return self.get(function) + [function_str] + connections

        
print "digraph {"
print "  node [shape=record,style=rounded,height=0.1];"
from pprint import pprint
print '  ' + '\n  '.join(DotVisitor().visit(impl));
print "}"

