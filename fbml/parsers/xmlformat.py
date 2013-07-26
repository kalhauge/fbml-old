"""
.. module:: fbml.parsers.xmlformat

"""


import xml.etree.ElementTree as ET
import logging

log = logging.getLogger(__name__)

from ..util import exceptions
from .. import model
from .parser import *

import io
import re

class XMLWriter (object):

    def __init__(self, extend_formats):
        self.extend_formats= extend_formats;

    def write(self,module,filelike):
        e = ET.ElementTree()
        root = ET.Element('fbml',{'version':'0.0'})
        self.write_imports_to_tree(module.imports,root) 
        self.write_extensions_to_tree(module.ext.get_all(),root)
        self.write_methods_to_tree(module.methods,root)
        e._setroot(root)
        s = io.StringIO()
        e.write(s,xml_declaration="1.0",encoding="unicode")
        result = s.getvalue()
        result = re.sub('(</[a-z]*>)',r'\1\n',result)
        result = re.sub('(/\s*>)',r'\1\n',result)
        result = re.sub('><',r'>\n<',result)
        try: filelike.write(result);
        except:
            with open(filelike,'w') as f:
                f.write(result)

    def write_methods_to_tree(self,methods,root):
        for method in methods: self.write_method_to_tree(method,root)

    def write_imports_to_tree(self,imports,root):
        for imp in imports: ET.SubElement(root,'import').text = repr(imp.label)

    def write_extensions_to_tree(self,exts,root):
        for ext in exts: 
            ET.SubElement(root,'extension').text = ext 

    def write_method_to_tree(self,method,root):
        tree_method = ET.SubElement(root,'method',{'id':method.label})
       
        self.write_requirements_to_tree(method.req.get_all(),tree_method)
        self.write_ensurances_to_tree(method.ens.get_all(),tree_method)
        try:   
            self.write_impl_to_tree(method.impl,root)
        except AttributeError as e:
            log.debug("No impl found to %s",method)

    def write_impl_to_tree(self,impl,root):
        tree_impl = ET.SubElement(root,'impl',
                {'method_id':impl.get_method().get_internal_id()})
        self.write_functions_to_tree(impl.get_functions(),tree_impl)

    def write_functions_to_tree(self,funcs,root):
        for func in funcs: self.write_function_to_tree(func,root)

    def write_function_to_tree(self,func,root):
        tree_func = ET.SubElement(root,'function',{'id':func.get_id()})
        self.write_extends_to_tree(func.get_extensions(),tree_func)
        self.write_sources_to_tree(func.get_sources(),tree_func)
        self.write_sinks_to_tree(func.get_sinks(),tree_func)

    def write_sources_to_tree(self,sources,root):
        for source in sources: self.write_source_to_tree(source,root)

    def write_source_to_tree(self,source,root):
        elm = ET.SubElement(root,'source')
        elm.set('sink_id',source.sink.sink_id)
        elm.set('slot',str(source.location.slot))
        self.write_extends_to_tree(source.ext.get_all(),elm)

    def write_sinks_to_tree(self,sinks,root):
        for sink in sinks: self.write_sink_to_tree(sink,root)

    def write_sink_to_tree(self,sink,root):
        elm = ET.SubElement(root,'sink')
        elm.set('id',sink.sink_id)
        elm.set('slot',str(sink.location.slot))
        self.write_extends_to_tree(sink.ext.get_all(),elm)

    def write_requirements_to_tree(self,reqs,root):
        for req in reqs.values(): self.extend_formats.write_require_to_tree(req,root)

    def write_ensurances_to_tree(self,ens,root):
        for en in ens.values(): self.extend_formats.write_ensure_to_tree(en,root)

    def write_extends_to_tree(self,exts,root):
        for ext in exts.values(): self.extend_formats.write_to_tree(ext,root)


class XMLParser (object):

    def __init__(self,extend_formats):
        self.extend_formats= extend_formats

    def parse(self,filelike):
        return self.parse_module(ET.parse(filelike).getroot())

    def parse_module(self,tree_module):
        module = Module(**tree_module.attrib)
        module.imports = (self._parse_all(tree_module,'import'))
        module.extensions = (self._parse_all(tree_module,'extension'))
        module.methods = (self._parse_all(tree_module,'method'))
        module.impls = (self._parse_all(tree_module,'impl'))
        return module

    def parse_method(self,tree_method):
        method = Method(**tree_method.attrib)
        method.set_requirements(self._parse_all(tree_method,'require'))
        method.set_ensurances(self._parse_all(tree_method,'ensure')) 
        return method

    def parse_impl(self,tree_impl):
        impl = Impl(**tree_impl.attrib)
        impl.set_functions(self._parse_all(tree_impl,'function'))
        return impl

    def parse_function(self,tree_func):
        func = Function(**tree_func.attrib)
        func.extends = (self._parse_all(tree_func,'extend'))
        func.set_sinks(self._parse_all(tree_func,'sink'))
        func.set_sources(self._parse_all(tree_func,'source'))
        return func

    def parse_require(self,tree_require):
        require = Require(**tree_require.attrib);
        self.extend_formats.parse_require(require,tree_require)
        return require

    def parse_ensure(self,tree_ensure): 
        ensure = Ensure(**tree_ensure.attrib)
        self.extend_formats.parse_ensure(ensure,tree_ensure)
        return ensure

    def parse_sink(self,tree_sink):
        sink = Sink(**tree_sink.attrib)
        sink.slot = int(sink.slot) 
        sink.extends = (self._parse_all(tree_sink,'extend'))
        return sink

    def parse_source(self,tree_source):
        source = Source(**tree_source.attrib)
        source.slot = int(source.slot)
        source.extends = (self._parse_all(tree_source,'extend'))
        return source
        
    def parse_extend(self,tree_extend):
        extend = Extend(**tree_extend.attrib)
        self.extend_formats.parse(extend,tree_extend)
        return extend

    def parse_import(self,tree_import):
        return tree_import.text

    def parse_extension(self,tree_ext):
        return tree_ext.text

    def _parse_all(self,tree,name):
        function = getattr(self,"parse_" + name)
        return (function(elm) for elm in tree.findall(name))


class XMLExtensionFormats (object):

    def __init__(self,extend_formats={}):
        self.extend_formats= dict(extend_formats)

    def add_extension_format(self,eformat):
        self.add_extension_format({eformat.get_name():eformat})

    def add_extension_formats(self,formats):
        self.extend_formats.update(formats)

    def get_extend_format(self,name):
        try: return self.extend_formats[name].XML_FORMAT
        except KeyError:
            log.warning(
                    'Found name %s, no known extension parser', 
                    name)
            form = XMLExtensionFormat()
            form.name = name
            return form 

    def parse(self,extend,tree_extend): 
        extend.data = self.get_extend_format(extend.name).parse(tree_extend)

    def parse_require(self,require,tree_require):
        require.data = self.get_extend_format(require.name).parse_require(tree_require)

    def parse_ensure(self,ensure,tree_ensure):
        ensure.data = self.get_extend_format(ensure.name).parse_ensure(tree_ensure)

    def write_to_tree(self,extend,root):
        tree = ET.SubElement(root,'extend',{'name':extend.get_name()})
        self.get_extend_format(extend.get_name())\
                .write_to_tree(extend.get_data(),tree);
    
    def write_require_to_tree(self,extend,root):
        tree = ET.SubElement(root,'require',{'name':extend.get_name()})
        self.get_extend_format(extend.get_name())\
                .write_require_to_tree(extend.get_data(),tree);
    
    def write_ensure_to_tree(self,extend,root):
        tree = ET.SubElement(root,'ensure',{'name':extend.get_name()})
        self.get_extend_format(extend.get_name())\
                .write_ensure_to_tree(extend.get_data(),tree);

class XMLExtensionFormat (object):
    
    def parse(self,tree):
        return tree 

    parse_require = parse
    parse_ensure = parse

    def write_to_tree(self,data,tree):
        tree.text = str(data)

    write_ensure_to_tree = write_to_tree
    write_require_to_tree = write_to_tree

