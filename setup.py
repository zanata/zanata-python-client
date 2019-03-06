#!/usr/bin/env python
"""
Build script for zanata-python-client
"""
from setuptools import setup, find_packages
import os
import subprocess


def read(fname):
    return (open(os.path.join(os.path.dirname(__file__), fname), 'rb')
            .read().decode('utf-8'))


def get_client_version():
    version_number = ""
    # Use the version in VERSION-FILE
    path = os.path.dirname(os.path.realpath(__file__))
    version_file = os.path.join(path, 'zanataclient', 'VERSION-FILE')
    try:
        version = open(version_file, 'r')
        client_version = version.read()
        version.close()
        version_number = client_version.rstrip().strip('version: ')
    except IOError:
        print("Please run VERSION-GEN or 'make install' to generate VERSION-FILE")
        version_number = "UNKNOWN"
    return version_number

requirements = read('requirements.txt').splitlines() + [
    'setuptools',
]

setup(
    name="zanata-python-client",
    version=get_client_version(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    description="Zanata Python Client.",
    author='Jian Ni, Ding-Yi Chen, Anish Patil, Sundeep Anand',
    author_email='dchen@redhat.com, apatil@redhat.com, suanand@redhat.com',
    license='LGPLv2+',
    platforms=["Linux"],
    scripts=["zanata", "flies"],
    url='https://github.com/zanata/zanata-python-client',

    # entry_points = {
    # 'console_scripts': [
    #   'zanata = zanataclient.zanata:main',
    #  ]
    # },

    package_data={
        '': ['VERSION-FILE']
    },

    data_files=[
        ('share/doc/zanata-python-client',
         ['CHANGELOG', 'COPYING', 'COPYING.LESSER', 'zanata.ini']
         )
    ],

    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License (LGPL)',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
