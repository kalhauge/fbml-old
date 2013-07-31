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
    source_map = ((sink, sink.user_slot(value)) for sink in value.sources)
    writer.write_object('source_map',source_map, func)
    target_map = ((sink, sink.slot) for sink in value.targets)
    writer.write_object('target_map',target_map, func)

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
        for sink_pair in value:
            writer.write_object('map',sink_pair,maps)
    return writer

def write_map(writer, value, root):
    (sink, slot) = value
    map_ = ET.SubElement(root,'map')
    map_.set('sink', sink.label.name)
    map_.set('slot', slot)

def write_remote_sink(writer, value, root):
    r_sink = ET.SubElement(root,'remote_sink')
    r_sink.set('id',value.label.name)
    if value.is_method_source():
        r_sink.set('source',value.slot)
    if value.is_method_target():
        r_sink.set('target',value.method_target)

def write_std(writer, value, root):
    log.debug('Writer encountered an unknow value {}'.format(value))
    root.append(value)

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
        log.debug('Writing with extensions : %s', extend_formats)
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
        self.formats.get(name,write_std)(self, value, root)

    def write_objects(self, name, values, root):
        for value in values:
            self.write_object(name, value, root)

def parse_module(parser, tree):
    module = Module(**tree.attrib)
    module.imports = parser.parse_objects(tree, 'import')
    module.methods = parser.parse_objects(tree, 'method')
    module.impls   = parser.parse_objects(tree, 'impl')
    return module

def parse_impl(parser, tree):
    impl = Impl(**tree.attrib)
    impl.functions = parser.parse_objects( tree, 'function')
    impl.sinks = parser.parse_objects( tree, 'sink')
    impl.remote_sinks = parser.parse_objects( tree, 'remote_sink')
    return impl

def parse_ext_object(cls,required):
    def parse_obj(parser,tree):
        obj = cls(**tree.attrib)
        for name in required:
            setattr(obj,name,parser.parse_object_from_name(tree, name))
        obj.data = Data()
        parser.parse_rest(tree,obj.data,required)
        return obj
    return parse_obj

def parse_object(cls, subtags):
    def parse_obj(parser,tree):
        obj = cls(**tree.attrib)
        for name in subtags:
            setattr(obj,name,parser.parse_object_from_name(tree, name))
        return obj
    return parse_obj


def parse_list(subtag):
    def parse(parser, tree):
       return list(parser.parse_objects(tree,subtag))
    return parse

def parse_text(parser, tree):
    return tree.text

def parse_std(parser, tree):
    log.debug("Parsing unknown %s",tree)
    return tree

class XMLParser (object):
    _std_formats = {
            'fbml'         : parse_module,
            'impl'         : parse_impl,
            'method'       : parse_object(Method,['require', 'ensure']),
            'function'     : parse_ext_object(Function,['sources','targets']),
            'require'      : parse_ext_object(Condition,['slots']),
            'ensure'       : parse_ext_object(Condition,['slots']),
            'sink'         : parse_ext_object(Sink,[]),
            'slot'         : parse_ext_object(Slot,[]),
            'remote_sink'  : parse_object(RemoteSink,[]),
            'map'          : parse_object(Map,[]),
            'targets'      : parse_list('map'),
            'sources'      : parse_list('map'),
            'slots'        : parse_list('slot'),
            'import'       : parse_text,
            }

    def __init__(self,extend_formats):
        self.formats = XMLParser._std_formats
        log.debug('Parsing with extendsions: %s', extend_formats)
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

    def parse_rest(self, tree, parrent, do_not_load):
        for subtree in tree:
            if not subtree.tag in do_not_load:
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
        return self.formats.get(tree.tag,parse_std)(self,tree)


