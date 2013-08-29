
import unittest

from fbml.parsers.parser import *
from fbml.parsers.xmlformat import *


#class XMLTestCase (unittest.TestCase):
#
#    no_extend = """<?xml version='1.0' encoding='UTF-8'?>
#        <fbml version="0.0">
#            <import>stdlib</import>
#            <method id="m1">
#            </method>
#            <impl method_id="m1">
#                <function id="f_add">
#                    <source sink_id="a" slot="0"/>
#                    <source sink_id="b" slot="1"/>
#                    <sink id="c" slot="0"/>
#                </function>
#            </impl>
#        </fbml>
#        """
#
#    with_extend = """<?xml version='1.0' encoding='UTF-8'?>
#        <fbml version="0.0">
#            <import>stdlib</import>
#            <extension>Type</extension>
#            <extension>Value</extension>
#            <extension>MethodName</extension>
#            <extension>Constant</extension>
#            <method id="m1">
#                <require name="MethodName">Main</require>
#                <require name="Sources">
#                    <source id="a" slot="0" />
#                    <source id="b" slot="1" />
#                </require>
#                <require name="Type">
#                    <type slot="0">Integer</type>
#                    <type slot="1">Integer</type>
#                </require>
#                <ensure name="Type">
#                    <type slot="0">Integer</type>
#                </ensure>
#                <ensure name="Sinks">
#                    <sink id="c" slot="0" />
#                </ensure>
#            </method>
#            <impl method_id="m1">
#                <function id="f_add">
#                    <extend name="MethodName">Add</extend>
#                    <source sink_id="a" slot="0">
#                        <extend name="Type">
#                            <type>Integer</type>
#                        </extend>
#                    </source>
#                    <source sink_id="b" slot="1">
#                        <extend name="Type">
#                            <type>Integer</type>
#                        </extend>
#                    </source>
#                    <sink id="c" slot="0">
#                        <extend name="Type">
#                            <type>Integer</type>
#                        </extend>
#                    </sink>
#                </function>
#            </impl>
#        </fbml>
#        """
#    
#    def test_parse_data(self):
#        from io import StringIO
#        parser = XMLParser(XMLExtensionFormats())
#        model_tree = parser.parse(StringIO(XMLTestCase.no_extend))
#
#
#    def test_parse_extend(self):
#        from fbml.extensions import extensions
#        from io import StringIO
#        parser = XMLParser(XMLExtensionFormats(extensions))
#        model_tree = parser.parse(StringIO(XMLTestCase.no_extend))
