#!/usr/bin/env python3.3

from distutils.core import setup


setup(
    name="PyFBML",
    version="0.0x",
    description='Python implementaion of the Flow Based Modeling Language (FBML)',
    author='Christian Gram Kalhauge',
    author_email='christian@kalhauge.dk',
    long_description=open('README.rst').read(),
    scripts=[
        'bin/compilers/fbml2dot',
        'bin/compilers/fbml2fbml',
        'bin/compilers/fbml2llvm',
        'bin/optimizers/fbml-type'
        ],
    packages=[
        'fbml',
        'fbml.util',
        'fbml.parsers',
        'fbml.extensions',
        'fbml.test',
        ],
)
