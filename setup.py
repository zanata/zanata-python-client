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
    number = ""
    path = os.path.dirname(os.path.realpath(__file__))
    version_file = os.path.join(path, 'zanataclient/VERSION-FILE')
    version_gen = os.path.join(path, 'VERSION-GEN')

    p = subprocess.Popen(version_gen, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    output = p.stdout.readline()
    number = output.rstrip()[len('version: '):]

    subprocess.Popen("""
    cat << EOF > MANIFEST.in
    include zanataclient/VERSION-FILE
    include CHANGELOG
    include COPYING
    include COPYING.LESSER
    include zanata.ini
EOF
    """, shell=True)

    if number == 'UNKNOWN':
        try:
            file = open(version_file, 'rb')
            client_version = file.read()
            file.close()
            number = client_version[:-1][len('version: '):]
        except IOError:
            file = open(version_file, 'w')
            file.write("version: UNKNOWN")
            file.close

    return number

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
    author='Jian Ni, Ding-Yi Chen, Anish Patil',
    author_email='jni@redhat.com, dchen@redhat.com, apatil@redhat.com',
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
