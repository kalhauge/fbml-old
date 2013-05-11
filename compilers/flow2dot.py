"""
Compiler : flow2dot 

This is the simple flow to dot compiler wich takes a .fl file
and produces dot code.

Need extensions:
    MethodName
"""

# Lets start out by importing pyflow 
import sys
sys.path.append('/Users/christian/Develop/Projects/2013/fbml/lib');

import pyfbml
from pyfbml.extensions import MethodNameExtension
import argparse

def fail(msg):
    import sys;
    print "Failed: " + str(msg);
    sys.exit(-1);

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('filename',help='the file to compile');
parser.add_argument('method_name',help='the method to print');

args = parser.parse_args();

ext = pyfbml.getExtensions('MethodName');                

flow = pyfbml.parseFlow(args.filename,ext);

method = flow.getMethod(args.method_name);
impl = method.getImpl();

class DotVisitor (pyfbml.Visitor):
    
    def setup(self,method_sources):
        for sink in method_sources:
            self.set(sink,['IN_{} [label="{}"];'.format(
                sink.getId(), 
                sink.getId())]
                )

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
        function_str= '{} [label="{{{}}}"];'.format(
            function.getId(),
            '{} {} {}'.format(
               '{{{}}} |'.format(in_str) if not in_str is '' else '',
               ext['MethodName'].get(function),
               '| {{{}}}'.format(out_str) if not out_str is '' else '',
               )
            )
        
        connections = []
        for source in function.getSources():
            sink = source.getSink();
            if not sink.getFunction() is None:
                con = '"{}":sink_{} -> "{}":source_{};'.format(
                        sink.getFunction().getId(),
                        sink.getId(),
                        function.getId(),
                        sink.getId())
            else:
                con = '"IN_{}" -> "{}":source_{};'.format(
                        sink.getId(),
                        function.getId(),
                        sink.getId())

            connections.append(con);

        return self.get(function) + [function_str] + connections

        
print "digraph {"
print "  node [shape=record,style=rounded,height=0.1];"
from pprint import pprint
print '  ' + '\n  '.join(DotVisitor().visit(impl));

for sid in method.getSinks():
    sink = impl.getSink(sid)
    print '  OUT_{} [label = "{}"];'.format(
            sink.getId(),
            sink.getId())
    print '  "{}":sink_{} -> "OUT_{}";'.format(
            sink.getFunction().getId(),
            sink.getId(),
            sink.getId());
print "}"

