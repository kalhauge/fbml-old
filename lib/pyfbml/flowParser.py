
from __init__ import MallformedFlowError;

def sortSlotList(slot_list):
    l = [None] * len(slot_list);
    for i,s in slot_list:
        if s > len(l) or s < 0: raise MallformedFlowError();
        l[s] = i;
    return l;

class FlowParser (object):
    def __init__(self,filename):
        import xml.etree.ElementTree as ET
        self._filename = filename;
        self._methods = dict()
        self._impls = dict()
        self.addFlowTree(ET.parse(filename));

    def createFlow(self):
        from flow import Flow
        return Flow(self._methods,self._impls)

    def addFlowTree(self,tree):
        import xml.etree.ElementTree as ET
        root = tree.getroot();
        
        for im in root.findall('import'):
            self.addFlowTree(ET.parse(im.text));
        
        for method in root.findall('method'):
            self.addMethodTree(method);

        for impl in root.findall('impl'):
            self.addImplTree(impl);

    def addMethodTree(self,tree):
        from flow import Method
        self._methods[tree.attrib['id']] = Method(tree.attrib['id']);
        pass

    def addImplTree(self,root):
        from flow import Impl, Sink, Source, Function

        method_id = root.attrib['method_id'];
        if not method_id in self._methods: raise MallformedFlowError();
        else: method = self._methods[method_id];

        sinks = [];
        for sink_root in root.iter('sink'):
            sink_id = sink_root.attrib['id'];
            if sink_id in sinks: raise MallformedFlowError(); 
            sinks[sink_id] = Sink(sink_id);

        functions = []
        for function in root.forall('function'):
            sinks = sortSlotList(
                        [(sinks[sid.attrib['id']],sid.attrib['slot']) 
                            for sid in function.forall('sinks')]
                        );
            function_sinks.extend(sinks);
            sources = sortSlotList(
                        [(Source(sinks[sid.attrib['id']]),sid.attrib['slot'])
                            for sid in function.forall('sinks')]
                        );

            function = Function(function.attrib('id'),sinks,sources);
            functions.append(function);
        
        method.addImpl(Impl(functions,function_sinks));


            
        
