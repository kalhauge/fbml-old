from __init__ import MallformedFlowError;
from pprint import pprint


def getSinks(root):
    from flow import Sink
    sinks = dict();
    for sink_root in root.iter('sink'):
        sink_id = sink_root.attrib['id'];
        if sink_id in sinks: raise MallformedFlowError(); 
        sinks[sink_id] = Sink(sink_id);
    return sinks;

def sortSlotList(slot_list):
    l = [None] * len(slot_list);
    for i,s in slot_list:
        s = int(s)
        if s > len(l) or s < 0: 
            raise MallformedFlowError(
                    "Slot id is {} should in the range [0,{}[".format(
                        s,len(l))
                    );
        l[s] = i;
    return l;

    

class FlowParser (object):
    def __init__(self,filename,extensions):
        self._extensions = extensions;
        self._filename = filename;
        self._methods = dict()
        self._impls = dict()
       

    def createFlow(self):
        from flow import Flow
        import xml.etree.ElementTree as ET
        self.addFlowTree(ET.parse(self._filename));
        return Flow(self._methods,self._impls)

    def addFlowTree(self,tree):
        import xml.etree.ElementTree as ET
        root = tree.getroot();
        for extension in root.findall('extension'):
            if not extension.attrib['name'] in self._extensions:
                raise MallformedFlowError(
                        "Should contain the {} extension".format(
                            extension.attrib['name']
                            ))

        for im in root.findall('import'):
            self.addFlowTree(ET.parse(im.text)); 

        for method in root.findall('method'):
            self.addMethodTree(method);

        for impl in root.findall('impl'):
            self.addImplTree(impl);

    def addMethodTree(self,tree):
        from flow import Method
        method_id = tree.attrib['id'];
        
        sources = sortSlotList(
                [(sid.attrib['id'],sid.attrib['slot'])
                    for sid in tree.findall('source')]
                );
       
        sinks = sortSlotList(
                [(sid.attrib['id'],sid.attrib['slot']) 
                    for sid in tree.findall('sink')]
                );
    
        method = Method(method_id,sources,sinks);
        self._methods[method_id] = method;

        for ext in tree.findall('extend'):
            self._extensions[ext.attrib['name']].parseExt(ext,method);
                    
    def addImplTree(self,root):
        from flow import Impl,Sink, Function

        method_id = root.attrib['method_id'];
        if not method_id in self._methods: raise MallformedFlowError();
        else: method = self._methods[method_id];

        sinks = getSinks(root);
        for source_id  in method.getSources():
            sinks[source_id] = Sink(source_id);

        functions = dict()
        for t_function in root.findall('function'):
            f_sinks = self.parseSinks(t_function,sinks);
            f_sources = self.parseSources(t_function,sinks);
            function = Function(t_function.attrib['id'],f_sources,f_sinks);
            functions[function.getId()] = function;
            self.addExtensions(t_function,function);

        method.addImpl(Impl(method,functions,sinks));
        t = {'function' : functions, 'sink' : sinks} 
        for ext in root.findall('extend'):
            obj = t[ext.attrib['type']][ext.attrib['id']];
            if ext.attrib['type'] != obj.getType():
                raise MallformedFlowError(
                    "Type {} different from {}".format(
                        ext.attrib['type'], obj));
            extension = self._extensions[ext.attrib['name']]
            extension.parseExt(ext,obj);
    
    def parseSinks(self,root,sinks):
        f_sink = [];
        for sink in root.findall('sink'):
            s = sinks[sink.attrib['id']];
            self.addExtensions(sink,s);
            f_sink.append((s,sink.attrib['slot']));
        return sortSlotList(f_sink)
        
    def parseSources(self,root,sinks):
        from flow import Source
        f_sources = [];
        for source in root.findall('source'):
            s = Source(sinks[source.attrib['sink_id']]);
            f_sources.append((s,source.attrib['slot']));
        return sortSlotList(f_sources)

    def addExtensions(self,root,obj):
        for ext in root.findall('extend'):
            extension = self._extensions[ext.attrib['name']]
            extension.parseExt(ext,obj);
            

                    


