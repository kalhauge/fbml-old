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
        #self.write_extensions_to_tree(module.ext.get_all(),root)
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
        for method in methods: 
            self.write_method_to_tree(method,root)

    def write_imports_to_tree(self,imports,root):
        for imp in imports:
            ET.SubElement(root,'import').text = repr(imp.label)

    def write_extensions_to_tree(self,exts,root):
        for ext in exts: 
            ET.SubElement(root,'extension').text = ext 

    def write_method_to_tree(self,method,root):
        tree_method = ET.SubElement(root,'method',{'id':method.label.name})
       
        self.write_requirements_to_tree(method.req.get_all(),tree_method)
        self.write_ensurances_to_tree(method.ens.get_all(),tree_method)
        try:   
            self.write_impl_to_tree(method.impl,root)
        except AttributeError as e:
            raise e
            log.debug("No impl found to %s",method)

    def write_impl_to_tree(self,impl,root):
        tree_impl = ET.SubElement(root,'impl',
                {'method_id':impl.method.label.name})
        self.write_functions_to_tree(impl.functions.values(),tree_impl)

    def write_functions_to_tree(self,funcs,root):
        for func in funcs: self.write_function_to_tree(func,root)

    def write_function_to_tree(self,func,root):
        tree_func = ET.SubElement(root,'function',{'id':func.label.name})
        self.write_extends_to_tree(func.ext.get_all(), tree_func)
        self.write_sources_to_tree(func.sources, tree_func)
        self.write_sinks_to_tree(func.sinks, tree_func)

    def write_sources_to_tree(self,sources,root):
        for source in sources: self.write_source_to_tree(source,root)

    def write_source_to_tree(self,source,root):
        elm = ET.SubElement(root,'source')
        elm.set('sink_id',source.sink.label.name)
        elm.set('slot',str(source.slot))
        self.write_extends_to_tree(source.ext.get_all(),elm)

    def write_sinks_to_tree(self,sinks,root):
        for sink in sinks: self.write_sink_to_tree(sink,root)

    def write_sink_to_tree(self,sink,root):
        elm = ET.SubElement(root,'sink')
        elm.set('id',sink.label.name)
        elm.set('slot',str(sink.slot))
        self.write_extends_to_tree(sink.ext.get_all(),elm)

    def write_requirements_to_tree(self,reqs,root):
        for name, req in reqs.items(): 
            self.extend_formats.write('require', name, req, root)

    def write_ensurances_to_tree(self,ens,root):
        for name, ens in ens.items(): 
            self.extend_formats.write('ensure', name, ens, root)

    def write_extends_to_tree(self,exts,root):
        for name, ext in exts.items():
            self.extend_formats.write('extend', name, ext, root)

def module_format(parser, tree):
    module = Module(**tree.attrib)
    module.imports = parser.parse_objects(tree, 'import')
    module.methods = parser.parse_objects(tree, 'method')
    module.impls   = parser.parse_objects(tree, 'impl')
    return module

def import_format(parser, tree):
    return tree.text

def method_format(parser, tree):
    method = Method(**tree.attrib)
    parser.parse_subobject(method, tree.find('require'))
    parser.parse_subobject(method, tree.find('ensure'))
    return method

def impl_format(parser, tree):
    impl = Impl(**tree.attrib)
    impl.functions = parser.parse_objects( tree, 'function')
    return impl

def function_format(parser, tree):
    function = Function(**tree.attrib)
    function.extends = parser.parse_object_from_name(tree,'extend')
    function.sources = parser.parse_object_from_name(tree,'sources')
    function.sinks = parser.parse_object_from_name(tree,'targets')
    return function

def slot_dict_format(parser, tree):
    objects = (parser.parse_object(subtree) for subtree in tree.findall('slot'))
    return dict((obj.id, obj.sink) for obj in objects)

def extend_format(parser, tree):
    extends = Extends()
    parser.parse_subobjects(extends,tree)
    return extends

def sink_format(parser, tree):
    sink = Sink(**tree.attrib)
    sink.extends = Extends(**{});
    parser.parse_subobjects(sink.extends,tree)
    return sink

def slot_format(parser, tree):
    slot = Slot(**tree.attrib)
    try:
        slot.sink = parser.parse_object_from_name(tree,'sink')
    except exceptions.MallformedFlowError:
        slot.sink = None
    return slot

def std_format(parser, tree):
    log.debug("Parsing unknown %s",tree)
    return tree

class XMLParser (object):
    _std_formats = {
            'fbml'     : module_format,
            'import'   : import_format,
            'method'   : method_format,
            'impl'     : impl_format,
            'function' : function_format,
            'targets'  : slot_dict_format,
            'sources'  : slot_dict_format,
            'require'  : extend_format,
            'ensure'   : extend_format,
            'extend'   : extend_format,
            'sink'     : sink_format,
            'slot'     : slot_format,
            }

    def __init__(self,extend_formats):
        self.formats = XMLParser._std_formats
        self.formats.update((e.NAME, e.XML_FORMAT.parse) for e in extend_formats)

    def parse(self,filelike):
        return self.parse_object(ET.parse(filelike).getroot())

    def parse_objects(self, tree, name):
        def parse(subtree):
            return self.parse_object(subtree, name)
        return [parse(subtree) for subtree in tree.findall(name)]

    def parse_subobject(self, parrent, tree):
        setattr(parrent,tree.tag,self.parse_object(tree))

    def parse_subobjects(self, parrent, tree):
        for subtree in tree:
            self.parse_subobject(parrent, subtree)


    def parse_object_from_name(self, tree, name):
        subtree = tree.find(name)
        try:
            return self.parse_object(subtree,name)
        except exceptions.MallformedFlowError:
            raise exceptions.MallformedFlowError('In tree {}'.format(tree))
        
    def parse_object(self, tree, name=None):
        if tree is None:
            raise exceptions.MallformedFlowError('Missed to parse an object: {} {}'.format(tree, name))
        return self.formats.get(tree.tag,std_format)(self,tree)

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

    def parse(self, tag, extend, tree):
        extformat = self.get_extend_format(extend.name)
        extend.data = extformat.parse(tag, tree)

    def write(self, tag, name, data, root):
        tree = ET.SubElement(root, tag, {'name':name})
        self.get_extend_format(name).write(tag, data, tree);

class XMLExtensionFormat (object):
    
    def parse(self, tag, tree):
        return tree 

    def write(self, tag, data, tree):
        tree.append(data)

