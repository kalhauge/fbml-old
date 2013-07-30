"""
.. module:: fbml.parsers.xmlformat

"""

import io
import re

from itertools import chain, compress
from operator import not_
import xml.etree.ElementTree as ET

import logging
log = logging.getLogger(__name__)

from ..util import exceptions
from .. import model
from .parser import *


def write_method(writer, value, root):
    method = ET.SubElement(root, 'method')
    method.set('id',value.label.name) 
    writer.write_object('require', value.req, method)
    writer.write_object('ensure', value.ens, method)
    writer.write_object('impl', value.impl, root)

def write_impl(writer, value, root):
    impl = ET.SubElement(root, 'impl')
    impl.set('method_id',value.method.label.name)

    is_remote = [sink.is_remote_sink() for sink in value.sinks.values()]
    remote_sinks = compress(value.sinks.values(),is_remote)
    local_sinks  = compress(value.sinks.values(),map(not_,is_remote))

    writer.write_objects('function',value.functions.values(), impl)
    writer.write_objects('sink',local_sinks, impl)
    writer.write_objects('remote_sink',remote_sinks, impl)

def write_function(writer, value, root):
    func = ET.SubElement(root, 'function')
    func.set('id', value.label.name)
    writer.write_object('extend',value.ext, func)
    writer.write_object('source_map',value.sources, func)
    writer.write_object('target_map',value.targets, func)

def write_sources(writer, value, root):
    srcs = ET.SubElement(root, 'sources')
    writer.write_objects('slot',value.values(), srcs)

def write_targets(writer, value, root):
    trgs = ET.SubElement(root, 'targets')
    writer.write_objects('slot',value.values(), trgs)

def write_slot(writer, value, root):
    slot = ET.SubElement(root, 'slot')
    slot.set('id',value.id)
    for name, value in vars(value.extends).items():
            writer.write_object(name, value, slot)

def write_sink(writer, value, root):
    sink = ET.SubElement(root, 'sink')
    sink.set('id', value.label.name)
    for name, value in vars(value.ext).items():
            writer.write_object(name, value, sink)

def write_import(writer, value, root):
    ET.SubElement(root,'import').text = repr(value.label)

def write_extend(name):
    def writer(writer, value, root):
        extend = ET.SubElement(root, name)
        for n, v in vars(value).items():
            writer.write_object(n,v,extend)
    return writer

def write_maps(name):
    def writer(writer, value, root):
        maps = ET.SubElement(root, name)
        for sink in value:
            writer.write_object('map',sink,maps)
    return writer

def write_map(writer, value, root):
    map_ = ET.SubElement(root,'map')
    map_.set('sink', value.label.name)
    map_.set('slot', value.slot)

def write_remote_sink(writer, value, root):
    r_sink = ET.SubElement(root,'remote_sink')
    r_sink.set('sink',value.label.name)
    if value.is_method_source():
        r_sink.set('source',value.slot)
    if value.is_method_target():
        r_sink.set('target',value.method_target)
class XMLWriter (object):

    _std_formats = {
            'import'       : write_import,
            'method'       : write_method,
            'impl'         : write_impl,
            'function'     : write_function,
            'sources'      : write_sources,
            'targets'      : write_targets,
            'require'      : write_extend('require'),
            'ensure'       : write_extend('ensure'),
            'extend'       : write_extend('extend'),
            'slot'         : write_slot,
            'sink'         : write_sink,
            'remote_sink'  : write_remote_sink,
            'source_map'   : write_maps('source_map'),
            'target_map'   : write_maps('target_map'),
            'map'          : write_map,
            }

    def __init__(self, extend_formats):
        self.formats = self._std_formats
        self.formats.update(
                (x.name, x.write) 
                for x in chain.from_iterable(
                    e.XML_FORMATS for e in extend_formats))

    def write(self,module,filelike):
        e = ET.ElementTree()
        root = ET.Element('fbml',{'version':'0.0'})
        self.write_objects('import', module.imports, root) 
        self.write_objects('method', module.methods, root)
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

    def write_object(self, name, value, root):
        self.formats[name](self, value, root)

    def write_objects(self, name, values, root):
        for value in values:
            self.write_object(name, value, root)

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
    impl.sinks = parser.parse_objects( tree, 'sink')
    impl.remote_sinks = parser.parse_objects( tree, 'remote_sink')
    return impl

def function_format(parser, tree):
    function = Function(**tree.attrib)
    function.extends = parser.parse_object_from_name(tree,'extend')
    function.sources = parser.parse_object_from_name(tree,'source_map')
    function.targets = parser.parse_object_from_name(tree,'target_map')
    return function

def slot_dict_format(parser, tree):
    objects = (parser.parse_object(subtree) for subtree in tree.findall('slot'))
    return dict((obj.id, obj) for obj in objects)

def map_dict_format(parser, tree):
    objects = (parser.parse_object(subtree) for subtree in tree.findall('map'))
    return dict((obj.slot, obj.sink) for obj in objects)

def map_format(parser, tree):
    return Map(**tree.attrib)

def extend_format(parser, tree):
    extends = Extends()
    parser.parse_subobjects(extends,tree)
    return extends

def sink_format(parser, tree):
    sink = Sink(**tree.attrib)
    sink.extends = Extends();
    parser.parse_subobjects(sink.extends,tree)
    return sink

def slot_format(parser, tree):
    slot = Slot(**tree.attrib)
    slot.extends = Extends()
    parser.parse_subobjects(slot.extends,tree)
    return slot

def remote_sink_format(parser, tree):
    sink = RemoteSink(**tree.attrib)
    return sink

def std_format(parser, tree):
    log.debug("Parsing unknown %s",tree)
    return tree

class XMLParser (object):
    _std_formats = {
            'fbml'         : module_format,
            'import'       : import_format,
            'method'       : method_format,
            'impl'         : impl_format,
            'function'     : function_format,
            'targets'      : slot_dict_format,
            'sources'      : slot_dict_format,
            'source_map'   : map_dict_format,
            'target_map'   : map_dict_format,
            'map'          : map_format,
            'require'      : extend_format,
            'ensure'       : extend_format,
            'extend'       : extend_format,
            'sink'         : sink_format,
            'slot'         : slot_format,
            'remote_sink'  : remote_sink_format,
            }

    def __init__(self,extend_formats):
        self.formats = XMLParser._std_formats
        self.formats.update(
                (x.name, x.parse) 
                for x in chain.from_iterable(
                    e.XML_FORMATS for e in extend_formats))

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
            raise exceptions.MallformedFlowError(
                    'Missed to parse an object: {} {}'.format(tree, name))
        return self.formats.get(tree.tag,std_format)(self,tree)


