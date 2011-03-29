#!/usr/bin/env python
"""
Build script for flies-python-client
"""
from setuptools import setup, find_packages
import os

file = open('./VERSION-FILE', 'rb')
version = file.read()
file.close()
number = version[:-1].strip('version: ')

setup (name = "zanata-python-client",
    version = number,
    packages = find_packages(),
    install_requires=[
        'polib' ,
        'httplib2'
    ],
    description = "Zanata Python Client.",
    author = 'Jian Ni',
    author_email = 'jni@redhat.com',
    license = 'LGPLv2+',
    platforms=["Linux"],
    scripts = ["zanata"],
    
    #entry_points = {
	#'console_scripts': [
	#	'zanata = zanataclient.zanata:main',
	#]
    #},

    classifiers=['License :: OSI Approved ::  GNU Lesser General Public License (LGPL)',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 ],
)
