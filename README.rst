.. image:: https://travis-ci.org/zanata/zanata-python-client.svg?branch=master
    :target: https://travis-ci.org/zanata/zanata-python-client
    :alt: Travis CI

Introduction
============

Zanata Python client is a client that communicates with a Zanata server
[http://zanata.org/] to push text for translation (from publican documents or
gettext-based software), and pull translated text back for inclusion in
software or documentation builds.

It also provides support for creating projects/versions in Zanata and
retrieving information about projects.

Install
=======

You can install the zanata-python-client with::

    $ yum install zanata-python-client

To install from source::

    $ make install

Compiling
=========

Required package for compilation::

    yum install python-polib

Required package for unit tests::

    yum install python-minimock python-mock

To run pylint against the source code::

    $ make lint

To run unit tests::

    $ make test

Configuration
=============

After you install the zanata-python-client, you need to create a configuration
file in $HOME/.config/zanata.ini that contains user-specific configuration. For
infomation on how to create a configuration file, go to:
http://zanata.org/help/cli-configuration/

For each project, you need to write a project-specific configuration file named
zanata.xml. An example can be found here:
https://github.com/zanata/zanata-server/blob/master/zanata.xml

You can also override the URL of the server with the command line option
``--url``.  Use ``--username`` for user name and ``--apikey`` for api key of
user.

Command List
============

Name: ``/usr/bin/zanata``

If you type ``zanata`` in the shell, it will give you basic information for
working with a Zanata server. You can use ``zanata --help`` to get more help.

Basic Usage: ``zanata COMMAND [ARGS] [COMMAND_OPTIONS]``

Listing/Querying for Projects::

    $ zanata list --url

Creating a project::

    $ zanata project create {project_id} --project-name={project_name} --project-desc={project_description}

Create a Project Version::

    $ zanata version create {version_id} --project-id={project_id} --version-name={version_name} --version-desc={version_description}

Query for information of a project::

    $ zanata project info --project-id={project_id}

Query for information of a project iteration::

    $ zanata version info --project-id={project_id} --project-version={version_id}

Publishing Templates (source text) to Zanata.

If you want to push only one template file to zanata server, you can use
command below::

    $ zanata publican push --project-id={project_id} --project-version={iteration_id} [documentName..]

If documentName is omitted, the ``publican push`` command will push all the
template files under the template folder to the Zanata server. You can specify
the path of template folder by command line option ``--srcdir``. If you don't
provide such info, the command will try to locate template folder in current
path::

    $ zanata publican push --project-id={project_id} --project-version={iteration_id} --srcdir={template_folder}

    $ zanata publican push --project-id={project_id} --project-version={iteration_id}

Or if you run command below in a folder containing a template folder with
zanata.xml in it, it will load all the info from configuration file::

    $ zanata publican push

You can use the ``import-po`` option and the related translation (po files)
will be pushed to zanata server at the same time.

You need to specify the parent folder that contains all the translations by the
``transDir`` option. By default it will read the language info from the project
configuration file (zanata.xml), or you can specify the language that you want
to push to the zanata server by ``lang`` option::

    $ zanata publican push --import-po --trandir={path of parent folder contains locale folders} --lang=lang1,lang2,..

When pushing source files, the server can try to fill in equivalent
translations for those files, from this project or other projects (depending
on the project options on the server). In previous versions, this was enabled
by default. You can set the `--copytrans` option to enable this function::

    $ zanata publican push --copytrans

Retrieving translated Documents from zanata.

If you want to retrieve only one file from zanata server, you can use::

    $ zanata publican pull --project-id={project_id} --project-version={iteration_id} [documentName..]

Without indicating the documentName, this command will pull all the documents
of a project version on zanata server to a local output folder. It reads the
language info from project configuration file (zanata.xml), or you can specify
the language that you want to pull from the zanata server by the ``--lang``
option::

    $ zanata publican pull --project-id={project_id} --project-version={iteration_id} --lang=lang1,lang2,.. --dstdir={output_folder}

    $ zanata publican pull --project-id={project_id} --project-version={iteration_id} --lang=lang1,lang2,..

You can also simply run this in a folder containing zanata.xml and it will load
all the info from configuration file::

    $ zanata publican pull

Push and pull software project with Zanata

If you want to only push a software project file to the zanata server::

    $ zanata po push --project-id={project_id} --project-version={iteration_id} [documentName..]

Without giving the documentName, ``po push`` will push all source files of the
project under the po folder to zanata server. You can specify the path of the
po folder with ``--srcdir={po_folder_name}``, if you don't provide such info,
the command will try to locate the po folder in the current path::

    $ zanata po push --project-id={project_id} --project-version={iteration_id} --srcdir={po_folder}

    $ zanata po push --project-id={project_id} --project-version={iteration_id}

Or you can simply run this in a folder containing a po folder with zanata.xml
and it will load all the info from configuration file::

    $ zanata po push

You can use the ``--import-po`` option and related translations will be pushed
to the zanata server at the same time. You can specify the parent folder that
contains all the translations with
``--transdir={path_of_parent_folder_contains_translation_files}``, or the
client will use the path of po folder as the 'transdir'.  By default, command
will read the language info from project configuration file (zanata.xml), or
you can specify the language that you want to push to the zanata server by
'lang' option::

    $ zanata po push --import-po --trandir={path of parent folder contains translation files, such as zh-CN.po} --lang=lang1,lang2,..

When pushing source files, the server can try to fill in equivalent
translations for those files, from this project or other projects (depending
on the project options on the server). In previous versions, this was enabled
by default. You can set the `--copytrans` option to enable this function::

    $ zanata po push --copytrans

Retrieving Software project translation from zanata

If you want to retrieve the software translation from the zanata server, you
can use the command below::

    $ zanata po pull --project-id={project_id} --project-version={iteration_id} [softwareName..]

Without indicating the software name, this command will pull all the
translations of a project version on the zanata server to a local output
folder. It reads the language info from project configuration file
(zanata.xml), or you can specify the language that you want to pull from the
zanata server by the ``--lang`` option::

    $ zanata po pull --project-id={project_id} --project-version={iteration_id} --lang=lang1,lang2,.. --dstdir={output_folder}

    $ zanata po pull --project-id={project_id} --project-version={iteration_id} --lang=lang1,lang2,..

you can also simply run this in a folder containing a zanata.xml file and it
will load all the info from the configuration file::

    $ zanata po pull

If you want to retrieve the statistics for a project version, you can use the command below::

    $ zanata stats --project-id={project_id} --project-version={iteration_id}
