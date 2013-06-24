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
        'bin/compilers/flow2dot',
        'bin/compilers/flow2llvm',
        'bin/optimizers/fbml-type'
        ],
    packages=[
        'pyfbml',
        'pyfbml.dataflow',
        'pyfbml.dataflow.extensions',
        'pyfbml.test',
        ],
)
