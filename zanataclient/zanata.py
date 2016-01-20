# vim: set et sts=4 sw=4:
#
# Zanata Python Client
#
# Copyright (c) 2011 Jian Ni <jni@redhat.com>
# Copyright (c) 2011 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

import getopt
import sys
import os
import string
import signal
import subprocess
from functools import wraps

from .zanatalib.logger import Logger
from .context import ProjectContext
from .cmdbase import (
    ListProjects, ProjectInfo, VersionInfo, CreateProject,
    CreateVersion, GlossaryPush, GlossaryDelete, Stats
)
from .command import makeHandler
from .command import strip_docstring
from .command import parse_command_line
from .command import handle_program
from .pushcmd import PoPush
from .pushcmd import PublicanPush
from .pushcmd import GenericPush
from .pullcmd import GenericPull
from .initcmd import ZanataInit

log = Logger()

option_sets = {
    'url': [
        dict(
            type='command',
            long=['--url'],
            metavar='URL',
        ),
    ],
    'user_name': [
        dict(
            type='command',
            long=['--username'],
            metavar='USERNAME',
        ),
    ],
    'key': [
        dict(
            type='command',
            long=['--apikey'],
            metavar='APIKEY',
        ),
    ],
    'user_config': [
        dict(
            type='command',
            long=['--user-config'],
            metavar='USER-CONFIG',
        ),
    ],
    'project_config': [
        dict(
            type='command',
            long=['--project-config'],
            metavar='PROJECT-CONFIG',
        ),
    ],
    'project_id': [
        dict(
            type='command',
            long=['--project-id'],
            metavar='PROJECT-ID',
        ),
    ],
    'project_version': [
        dict(
            type='command',
            long=['--project-version'],
            metavar='PROJECT-VERSION',
        ),
    ],
    'dir': [
        dict(
            type='command',
            long=['--dir'],
            metavar='DIR',
        ),
    ],
    'force': [
        dict(
            type='command',
            long=['--force'],
            short=['-f'],
        ),
    ],
    'help': [
        dict(
            type='shared',
            long=['--help'],
            short=['-h'],
        ),
    ],
    'srcdir': [
        dict(
            type='command',
            long=['--srcdir'],
            metavar='SRCDIR',
        ),
    ],
    'srcfile': [
        dict(
            type='command',
            long=['--srcfile'],
            metavar='SRCFILE',
        ),
    ],
    'transdir': [
        dict(
            type='command',
            long=['--transdir'],
            metavar='TRANSDIR',
        ),
    ],
    'dstdir': [
        dict(
            type='command',
            long=['--dstdir'],
            metavar='DSTDIR',
        ),
    ],
    'project_name': [
        dict(
            type='command',
            long=['--project-name'],
            metavar='PROJECTNAME',
        ),
    ],
    'project_desc': [
        dict(
            type='command',
            long=['--project-desc'],
            metavar='PROJECTDESC',
        ),
    ],
    'version_name': [
        dict(
            type='command',
            long=['--version-name'],
            metavar='VERSIONNAME',
        ),
    ],
    'version_desc': [
        dict(
            type='command',
            long=['--version-desc'],
            metavar='VERSIONDESC',
        ),
    ],
    'lang': [
        dict(
            type='command',
            long=['--lang'],
            metavar='LANG',
        ),
    ],
    'email': [
        dict(
            type='command',
            long=['--email'],
            metavar='EMAIL',
        ),
    ],
    'merge': [
        dict(
            type='command',
            long=['--merge'],
            metavar='MERGE',
        ),
    ],
    'pushtrans': [
        dict(
            type='command',
            long=['--push-trans'],
        ),
    ],
    'importpo': [
        dict(
            type='command',
            long=['--import-po']
        ),
    ],
    'copytrans': [
        dict(
            type='command',
            long=['--copytrans'],
        ),
    ],
    'nocopytrans': [
        dict(
            type='command',
            long=['--no-copytrans'],
        ),
    ],
    'project_type': [
        dict(
            type='command',
            long=['--project-type'],
            metavar='PROJECTTYPE',
        ),
    ],
    'client_version': [
        dict(
            type='program',
            long=['--version'],
            short=['-V'],
        ),
    ],
    'comment_cols': [
        dict(
            type='command',
            long=['--commentcols'],
            metavar='COMMENTCOLS',
        ),
    ],
    'sourcecomments': [
        dict(
            type='command',
            long=['--sourcecommentsastarget'],
        ),
    ],
    'noskeletons': [
        dict(
            type='command',
            long=['--noskeletons'],
        ),
    ],
    'pushtransonly': [
        dict(
            type='command',
            long=['--push-trans-only'],
        ),
    ],
    'pushtype': [
        dict(
            type='command',
            long=['--push-type'],
            metavar='PUSHTYPE',
        ),
    ],
    'mindocpercent': [
        dict(
            type='command',
            long=['--min-doc-percent'],
            metavar='MINDOCPERCENT',
        ),
    ],
    'disablesslcert': [
        dict(
            type='command',
            long=['--disable-ssl-cert'],
        ),
    ],
    'detailstats': [
        dict(
            type='command',
            long=['--details'],
        ),
    ],
    'wordstats': [
        dict(
            type='command',
            long=['--word'],
        ),
    ],
    'docid': [
        dict(
            type='command',
            long=['--docid'],
            metavar='DOCID',
        ),
    ]
}

subcmds = {
    'help': [],
    'list': [],
    'status': [],
    'project': ['info', 'create', 'remove'],
    'version': ['info', 'create', 'remove'],
    'publican': ['push', 'pull'],
    'po': ['push', 'pull'],
    'push': [],
    'pull': [],
    'glossary': ['push', 'delete'],
    'stats': [],
    'init': [],
}

usage = """Client for talking to a Zanata Server
Usage: zanata <command> [COMMANDOPTION]...

list of commands:
help                Display this help and exit
init                Initialize Zanata project configuration
list                List all available projects
project info        Show information about a project
version info        Show information about a version
project create      Create a project
version create      Create a version within a project
publican pull       Pull the content of publican file
publican push       Push the content of publican file to Zanata server
po pull             Pull the content of software project file
po push             Push the content of software project file to Zanata server
push                Push the content of software project/docbook project to Zanata server
pull                Pull the content of software project/docbook project from Zanata server
glossary push       Push the glossary files to Zanata server
stats               Displays translation statistics for a Zanata project version

available system options:
--help              Display this help or detail usage of commands
--version           Display python client version

Use 'zanata help' for the full list of commands
Use 'zanata help <command>, zanata <command> --help or zanata <command> -h' for detail usage of commands
"""


def process_command(args):
    command = args[0]
    if len(args) > 1:
        for arg in args[1:]:
            command = command + '_' + arg

    if command in command_handler_factories:
        if hasattr(help, command):
            print(strip_docstring(getattr(help, command)))
        else:
            fn = command_handler_factories[command]()
            print(strip_docstring((fn.__doc__ or 'No help')))
        sys.exit(0)
    else:
        if command == 'project':
            print("Command: 'zanata project info'\n"
                  "         'zanata project create'")
        elif command == 'version':
            print("Command: 'zanata version info'\n"
                  "         'zanata version create'")
        elif command == 'publican':
            print("Command: 'zanata publican push'\n"
                  "         'zanata publican pull'")
        elif command == 'po':
            print("Command: 'zanata po push'\n"
                  "         'zanata po pull'")
        else:
            log.error("No such command %r, Try 'zanata --help' for more information." % command.replace('_', ' '))

#################################
#
# Command Handler
#
#################################


def command(cmd, auth_req, mode=None):
    def command_decorator(func):
        @wraps(func)
        def run_func(command_options, args, project_type=None):
            context_data = ProjectContext(command_options, mode).get_context_data()
            context_data['auth_req'] = auth_req
            if project_type:
                context_data['project_type'] = project_type
                context_data['publican_po'] = True
            command = cmd(args, context_data)
            command.run()
        return run_func
    return command_decorator


def help_info(command_options, args):
    if args:
        process_command(args)
    else:
        print(usage)


@command(ListProjects, False)
def list_project(command_options, args):
    """
    Usage: zanata list [OPTIONS]

    List all available projects

    Options:
        --url address of the Zanata server, eg http://example.com/zanata
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(ProjectInfo, False)
def project_info(command_options, args):
    """
    Usage: zanata project info [OPTIONS]

    Show infomation about a project

    Options:
        --project-id: project id
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(VersionInfo, False)
def version_info(command_options, args):
    """
    Usage: zanata version info [OPTIONS]

    Show infomation about a version

    Options:
        --project-id: project id
        --project-version: id of project version
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(CreateProject, True)
def create_project(command_options, args):
    """
    Usage: zanata project create [PROJECT_ID] [OPTIONS]

    Create a project

    Options:
        --username      : user name (defaults to zanata.ini value)
        --apikey        : api key of user (defaults to zanata.ini value)
        --project-name  : project name
        --project-desc  : project description
        --project-type  : project type (gettext, podir)
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(CreateVersion, True)
def create_version(command_options, args):
    """
    Usage: zanata version create [VERSION_ID] [OPTIONS]

    Create a version

    Options:
        --username      : user name (defaults to zanata.ini value)
        --apikey        : api key of user (defaults to zanata.ini value)
        --project-id    : id of the project
        --version-name  : version name (Deprecated)
        --version-desc  : version description (Deprecated)
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


def po_pull(command_options, args):
    """
    Usage: zanata po pull [OPTIONS] {documents} {lang}

    Retrieve gettext project translation files from server

    Options:
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --dstdir            : output folder (same as --transdir option)
        --dir               : output folder for po files (same as --transdir)
        --transdir          : output folder for po files
        --lang              : language list
        --noskeleton        : omit po files when translations not found
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pull(command_options, args, "gettext")


@command(PoPush, True)
def po_push(command_options, args):
    """
    Usage: zanata po push [OPTIONS] {documents}

    Push software project source and translation files to server

    Options:
        -f                  : force to remove content on server side
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --dir               : the path of the folder that contains pot files and po files,
                                no need to specify --srcdir and --transdir if --dir option specified
        --srcdir            : the path of the po folder(e.g. ./po)
        --srcfile           : the path of the source file
        --transdir          : the path of the folder that contains po files(e.g. ./po)
        --import-po         : push local translations to server
        --merge             : override merge algorithm: auto (default) or import
        --copytrans         : ask server to copy translations from other versions
        --no-copytrans      : no effect (kept for backward compatibility). Incompatible
                                with --copytrans option.
        --lang              : language list
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


def publican_pull(command_options, args):
    """
    Usage: zanata publican pull [OPTIONS] {documents} {lang}

    Retrieve translated publican content files from server

    Options:
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --dstdir            : output folder (same as --transdir option)
        --dir               : output folder (same as --transdir option)
        --transdir          : translations will be written to this folder (one sub-folder per locale)
        --lang              : language list
        --noskeleton        : omit po files when translations not found
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pull(command_options, args, "podir")


@command(PublicanPush, True)
def publican_push(command_options, args):
    """
    Usage: zanata publican push OPTIONS {documents}

    Push publican content to server for translation.

    Arguments: documents

    Options:
        -f                  : force to remove content on server side
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --dir               : the path of the folder that contains pot folder and locale folders,
                                no need to specify --srcdir and --transdir if --dir option specified
        --srcdir            : the path of the pot folder (e.g. ./pot)
        --transdir          : the path of the folder that contain locale folders
                                (e.g. ./myproject)
        --import-po         : push local translations to server
        --merge             : override merge algorithm: auto (default) or import
        --copytrans         : ask server to copy translations from other versions
        --no-copytrans      : no effect (kept for backward compatibility). Incompatible
                                with --copytrans option.
        --lang              : language list
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(GenericPush, True)
def push(command_options, args):
    """
    Usage: zanata push OPTIONS {documents}

    Generic push command to push content to server for translation.

    Arguments: documents

    Options:
        -f                  : force to remove content on server side
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-type      : project type (gettext or podir)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --srcdir            : the path of the pot folder (e.g. ./pot)
        --srcfile           : the path of the pot file(gettext project only)
        --transdir          : the path of the folder that contain locale folders
                                (e.g. ./myproject)
        --push-trans        : push local translations to server
        --push-trans-only   : push translations only
        --push-type         : source: push source document only, target: push translations only, same as push-trans-only
                                both: push source and translations together, same as push-trans
        --merge             : override merge algorithm: auto (default) or import
        --no-copytrans      : prevent server from copying translations from other versions
        --lang              : language list (defaults to zanata.xml locales)
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(GenericPull, False)
def pull(command_options, args, project_type=None):
    """
    Usage: zanata pull [OPTIONS] {documents} {lang}

    Retrieve translated publican content files from server

    Options:
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-type      : project type (gettext or podir)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --transdir          : translations will be written to this folder
        --lang              : language list (defaults to zanata.xml locales)
        --min-doc-percent   : Only pull translation documents that have at least this percentage of messages translated.
                                Accepts an integer from 0 to 100.
        --noskeletons       : omit po files when translations not found
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(GlossaryPush, True)
def glossary_push(command_options, args):
    """
    Usage: zanata glossary push [OPTIONS] GLOSSARY_POFILE

    Push glossary file in po/csv format to zanata server

    Options:
        --url               : URL of zanata server
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --lang(po format)   : language of glossary file
        --sourcecommentsastarget(po format): treat extracted comments and references as target comments of term
                                  or treat as source reference of entry
        --commentcols(csv format): comments header of csv format glossary file
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(GlossaryDelete, True)
def glossary_delete(command_options, args):
    """
    Usage: zanata glossary delete [OPTIONS]

    Delete glossary file at zanata server

    Options:
        --url               : URL of zanata server
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --lang(po format)   : language of glossary file
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(Stats, False)
def stats(command_options, args):
    """
    Usage: zanata stats [OPTIONS]

    Displays translation statistics for a Zanata project version

    Options:
        --url               : URL of zanata server
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --details           : Include statistics for lower levels (i.e., for documents in a project version)
        --docid             : Document Id to fetch statistics for
        --lang              : Language list (comma separated)
        --word              : Include word level statistics. By default only message level statistics are shown
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


@command(ZanataInit, False, 'init')
def init(command_options, args):
    """
    Usage: zanata init [OPTIONS]

    Initialize Zanata project configuration

    Options:
        --url               : URL of zanata server
        --username          : user name (defaults to zanata.ini value)
        --apikey            : api key of user (defaults to zanata.ini value)
        --project-id        : id of the project (defaults to zanata.xml value)
        --project-version   : id of the version (defaults to zanata.xml value)
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pass


command_handler_factories = {
    'help': makeHandler(help_info),
    'list': makeHandler(list_project),
    'project_info': makeHandler(project_info),
    'project_create': makeHandler(create_project),
    'version_info': makeHandler(version_info),
    'version_create': makeHandler(create_version),
    'po_pull': makeHandler(po_pull),
    'po_push': makeHandler(po_push),
    'publican_pull': makeHandler(publican_pull),
    'publican_push': makeHandler(publican_push),
    'push': makeHandler(push),
    'pull': makeHandler(pull),
    'glossary_push': makeHandler(glossary_push),
    'glossary_delete': makeHandler(glossary_delete),
    'stats': makeHandler(stats),
    'init': makeHandler(init),
}


def signal_handler(signal, frame):
    print('\nPressed Ctrl+C! Stop processing!')
    sys.exit(0)


def run():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        command = None
        prog_opts, command_opts, command, args = parse_command_line(
            option_sets,
            subcmds,
        )
        handle_program(
            command_handler_factories,
            option_sets,
            prog_opts,
            command_opts,
            command,
            args,
            program_name=os.path.split(sys.argv[0])[1],
        )
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))
        if command:
            print("Try zanata %(command)s --help' for more information." % {
                'command': command,
            })
        else:
            print(usage)
        sys.exit(2)
