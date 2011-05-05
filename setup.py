#!/usr/bin/env python
"""
Build script for zanata-python-client
"""
from setuptools import setup, find_packages
import os
import subprocess

path = os.path.dirname(os.path.realpath(__file__))
version_file = os.path.join(path, 'zanataclient/VERSION-FILE')
version_gen = os.path.join(path, 'VERSION-GEN')

p = subprocess.Popen(version_gen, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  close_fds=True)
output = p.stdout.readline()
number = output[:-1].strip('version: ')

if number=='UNKNOWN' and os.path.exists(version_file):
    file = open(version_file, 'rb')
    client_version = file.read()
    file.close()
    number = client_version[:-1].strip('version: ')

subprocess.Popen("""
cat << EOF > MANIFEST.in
include zanataclient/VERSION-FILE
EOF
""", shell=True)

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
    scripts = ["zanata","flies"],
    
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
