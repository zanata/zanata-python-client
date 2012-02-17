#!/usr/bin/env python
"""
Build script for zanata-python-client
"""
from setuptools import setup, find_packages
import os
import subprocess


def get_client_version():
    number = ""
    path = os.path.dirname(os.path.realpath(__file__))
    version_file = os.path.join(path, 'zanataclient/VERSION-FILE')
    version_gen = os.path.join(path, 'VERSION-GEN')

    p = subprocess.Popen(version_gen, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  close_fds=True)
    output = p.stdout.readline()
    number = output.rstrip()[len('version: '):]
    
    subprocess.Popen("""
    cat << EOF > MANIFEST.in
    include zanataclient/VERSION-FILE
    EOF
    """, shell=True)

    if number=='UKNOWN':
        try:
            file = open(version_file, 'rb')
            client_version = file.read()
            file.close()
            number = client_version[:-1][len('version: '):]
        except IOError:
            file = open(version_file, 'w')
            file.write("version: UKNOWN")
            file.close

    return number

setup (name = "zanata-python-client",
    version = get_client_version(),
    packages = find_packages(),
    include_package_data = True,
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
    package_data = {
        '': ['VERSION-FILE']
    },

    classifiers=['License :: OSI Approved ::  GNU Lesser General Public License (LGPL)',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 ],
)
