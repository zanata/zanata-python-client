#!/usr/bin/env python
"""
Build script for flies-python-client
"""
from setuptools import setup

setup (name = "flies-python-client",
    version = '0.0.1',
    packages = ['flieslib'],
    py_modules = ['flies'], 
    description = "Flies Python Client.",
    author = 'Jian Ni',
    author_email = 'jni@redhat.com',
    license = 'LGPLv2+',
    platforms=["Linux"],

    classifiers=['License :: OSI Approved ::  GNU Lesser General Public License (LGPL)',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 ],
)
