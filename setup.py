#!/usr/bin/env python
"""
Build script for flies-python-client
"""
from setuptools import setup, find_packages
import os
import subprocess

if not os.path.exists('./VERSION-FILE'):
    p = subprocess.Popen('./VERSION-GEN', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  close_fds=True)
    output = p.stdout.readline()
    number = output[:-1].strip('version: ')
else:
    file = open('./VERSION-FILE', 'rb')
    client_version = file.read()
    file.close()
    number = client_version[:-1].strip('version: ')

subprocess.Popen("""
cat << EOF > MANIFEST.in
include COPYING
include COPYING.LESSER
include zanata.xml
include zanata.ini
include zanata
include VERSION-FILE
include VERSION-GEN
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
