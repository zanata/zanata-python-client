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

from zanatalib.versionservice import VersionService
from zanatalib.error import UnAvaliableResourceException
from zanatalib.error import NoSuchFileException
from zanatalib.error import UnavailableServiceError
from zanatalib.logger import Logger
from zanatacmd import ZanataCommand
from parseconfig import ZanataConfig
from publicanutil import PublicanUtility
from optionsutil import OptionsUtil

from command import makeHandler
from command import strip_docstring
from command import parse_command_line
from command import handle_program
from pushcmd import PoPush
from pushcmd import PublicanPush
from pushcmd import GenericPush
from pullcmd import GenericPull

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
    'noskeletons' : [
        dict(
            type='command',
            long=['--noskeletons'],
        ),
    ],
    'pushtransonly' : [
        dict(
            type='command',
            long=['--push-trans-only'],
        ),
    ],
    'pushtype' : [
        dict(
            type='command',
            long=['--push-type'],
            metavar='PUSHTYPE',
        ),
    ],
    'disablesslcert' : [
        dict(
            type='command',
            long=['--disable-ssl-cert'],
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
    'push':[],
    'pull':[],
    'glossary':['push', 'delete']
    }

usage = """Client for talking to a Zanata Server
Usage: zanata <command> [COMMANDOPTION]...

list of commands:
help                Display this help and exit
list                List all available projects
project info        Show information about a project
version info        Show information about a version
project create      Create a project
version create      Create a version within a project
publican pull       Pull the content of publican file
publican push       Push the content of publican file to Zanata server
po pull       Pull the content of software project file
po push       Push the content of software project file to Zanata server
push          Push the content of software project/docbook project to Zanata server
pull          Pull the content of software project/docbook project from Zanata server
glossary push Push the glossary files to Zanata server

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

    if command_handler_factories.has_key(command):
        if hasattr(help, command):
            print strip_docstring(getattr(help, command))
        else:
            fn = command_handler_factories[command]()
            print strip_docstring((fn.__doc__ or 'No help'))
        sys.exit(0)
    else:
        if command == 'project':
            print ("Command: 'zanata project info'\n"
                    "         'zanata project create'")
        elif command == 'version':
            print ("Command: 'zanata version info'\n"
                    "         'zanata version create'")
        elif command == 'publican':
            print ("Command: 'zanata publican push'\n"
                    "         'zanata publican pull'")
        elif command == 'po':
            print ("Command: 'zanata po push'\n"
                    "         'zanata po pull'")
        else:
            log.error("No such command %r, Try 'zanata --help' for more information." % command.replace('_', ' '))

def read_project_config(command_options):
    project_config = {}
    config = ZanataConfig()
    #Read the project configuration file using --project-config option
    config_file = [os.path.join(os.getcwd(), filename) for filename\
                    in ['zanata.xml', 'flies.xml']]

    if command_options.has_key('project_config'):
        config_file.append(command_options['project_config'][0]['value'])

    for path in config_file:
        if os.path.exists(path):
            log.info("Loading zanata project config from: %s" % path)
            project_config = config.read_project_config(path)
            break

    return project_config

def process_url(project_config, command_options):
    url = ""
    #process the url of server
    if project_config.has_key('project_url'):
        url = project_config['project_url']
    #The value in options will override the value in project-config file
    if command_options.has_key('url'):
        log.info("Overriding url of server with command line option")
        url = command_options['url'][0]['value']

    if not url or url.isspace():
        log.error("Please specify valid server url in zanata.xml or with '--url' option")
        sys.exit(1)
    
    if ' ' in url or '\n' in url:
        log.info("Warning, the url which contains '\\n' or whitespace is not valid, please check zanata.xml")
    url = url.strip()

    if url[-1] == "/":
        url = url[:-1]
    
    return url

def read_user_config(url, command_options):
    print "read user config"
    user_name = ""
    apikey = ""
    config = ZanataConfig()
    #Try to read user-config file
    user_config = [os.path.join(os.path.expanduser("~") + '/.config', filename) for filename in ['zanata.ini', 'flies.ini']]
    if command_options.has_key('user_config'):
        user_config.append(command_options['user_config'][0]['value'])

    for path in user_config:
        if os.path.exists(path):
            log.info("Loading zanata user config from: %s" % path)

            #Read the user-config file
            config.set_userconfig(path)

            try:
                server = config.get_server(url)
                if server:
                    user_name = config.get_config_value("username", "servers", server)
                    apikey = config.get_config_value("key", "servers", server)
            except Exception, e:
                log.info("Processing user-config file:%s" % str(e))
                break
            
            break

    if not (user_name, apikey):
        log.info("Can not find user-config file in home folder, current path or path in 'user-config' option")

    log.info("zanata server: %s" % url)

    #The value in commandline options will overwrite the value in user-config file
    if command_options.has_key('user_name'):
        user_name = command_options['user_name'][0]['value']

    if command_options.has_key('key'):
        apikey = command_options['key'][0]['value']

    return (user_name, apikey)

def get_version(url, command_options,headers=None):
    #Retrieve the version of client
    version_number = ""
    path = os.path.dirname(os.path.realpath(__file__))
    version_file = os.path.join(path, 'VERSION-FILE')

    try:
        version = open(version_file, 'rb')
        client_version = version.read()
        version.close()
        version_number = client_version.rstrip()[len('version: '):]
    except IOError:
        log.error("Please run VERSION-GEN or 'make install' to generate VERSION-FILE")
        version_number = "UNKNOWN"

    #Retrieve the version of the zanata server
    version = VersionService(url,headers)

    if command_options.has_key('disablesslcert'):
        version.disable_ssl_cert_validation()

    try:
        content = version.get_server_version()
        if content:
            server_version = content['versionNo']
            log.info("zanata python client version: %s, zanata server API version: %s" % (version_number, content['versionNo']))
            return server_version
    except UnAvaliableResourceException:
        log.info("zanata python client version: %s" % version_number)
        log.error("Can not retrieve the server version, server may not support the version service")
    except UnavailableServiceError:
        log.error("Service Temporarily Unavailable, stop processing!")
        sys.exit(1)
        
def generate_zanatacmd(url, username, apikey):
    if username and apikey:
        return ZanataCommand(url, username, apikey)
    else:
        log.error("Please specify username and apikey in zanata.ini or with '--username' and '--apikey' options")
        sys.exit(1)

#################################
#
# Command Handler
#
#################################
def help_info(command_options, args):
    if args:
        process_command(args)
    else:
        print usage

def list_project(command_options, args):
    """
    Usage: zanata list [OPTIONS]

    List all available projects

    Options:
        --url address of the Zanata server, eg http://example.com/zanata
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    project_config = read_project_config(command_options)
    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    headers = http_headers(username,apikey,'application/json')
    zanatacmd = ZanataCommand(url,username,apikey,headers)
    if command_options.has_key('disablesslcert'):
        zanatacmd.disable_ssl_cert_validation()
    headers = http_headers(username,apikey,'application/vnd.zanata.Version+json')
    get_version(url, command_options,headers)
    zanatacmd.list_projects()

def http_headers(user_name,user_pass,accept_format):
    headers = {
        'X-Auth-User':user_name,
        'X-Auth-Token':user_pass,
        'Accept': accept_format
    }
    return headers

def project_info(command_options, args):
    """
    Usage: zanata project info [OPTIONS]

    Show infomation about a project

    Options:
        --project-id: project id
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    project_id = ""
    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")
    
    url = process_url(project_config, command_options)
    get_version(url, command_options)

    if command_options.has_key('project_id'):
        project_id = command_options['project_id'][0]['value']
    else:
        if project_config:
            project_id = project_config['project_id']

    if not project_id:
        log.error('Please use zanata project info --project-id=project_id or zanata.xml to specify the project id')
        sys.exit(1)

    zanatacmd = ZanataCommand(url)

    if command_options.has_key('disablesslcert'):
        zanatacmd.disable_ssl_cert_validation()

    zanatacmd.project_info(project_id)

def version_info(command_options, args):
    """
    Usage: zanata version info [OPTIONS]

    Show infomation about a version

    Options:
        --project-id: project id
        --project-version: id of project version
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    project_id = ""
    iteration_id = ""

    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")
    else:
        project_id = project_config['project_id']
        iteration_id = project_config['project_version']

    url = process_url(project_config, command_options)

    get_version(url, command_options)

    if command_options.has_key('project_id'):
        project_id = command_options['project_id'][0]['value']

    if command_options.has_key('project_version'):
        iteration_id = command_options['project_version'][0]['value']

    if not iteration_id or not project_id:
        log.error("Please use zanata version info --project-id=project_id --project-version=project_version to retrieve the version")
        sys.exit(1)

    zanatacmd = ZanataCommand(url)

    if command_options.has_key('disablesslcert'):
        zanatacmd.disable_ssl_cert_validation()

    zanatacmd.version_info(project_id, iteration_id)

def create_project(command_options, args):
    """
    Usage: zanata project create [PROJECT_ID] [OPTIONS]

    Create a project

    Options:
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-name: project name
        --project-desc: project description
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    project_id = ""
    project_name = ""
    project_desc = ""
    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    get_version(url, command_options)

    if args:
        project_id = args[0]
    else:
        log.error("Please provide PROJECT_ID for creating project")
        sys.exit(1)

    if command_options.has_key('project_name'):
        project_name = command_options['project_name'][0]['value']
    else:
        log.error("Please specify project name with '--project-name' option")
        sys.exit(1)

    if command_options.has_key('project_desc'):
        project_desc = command_options['project_desc'][0]['value']

    zanatacmd = generate_zanatacmd(url, username, apikey)

    if command_options.has_key('disablesslcert'):
        zanatacmd.disable_ssl_cert_validation()

    zanatacmd.create_project(project_id, project_name, project_desc)

def create_version(command_options, args):
    """
    Usage: zanata version create [VERSION_ID] [OPTIONS]

    Create a version

    Options:
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-id: id of the project
        --version-name(Deprecated): version name 
        --version-desc(Deprecated): version description
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    project_id = ""
    version_name = ""
    version_desc = ""
    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    server_version = get_version(url, command_options)

    if command_options.has_key('project_id'):
        project_id = command_options['project_id'][0]['value']
    elif project_config.has_key('project_id'):
        project_id = project_config['project_id']
    else:
        log.error("Please specify PROJECT_ID with --project-id option or using zanata.xml")

    log.info("Project id:%s" % project_id)

    if args:
        version_id = args[0]
    else:
        log.error("Please provide ITERATION_ID for creating version")
        sys.exit(1)

    if command_options.has_key('version_name'):
        version_name = command_options['version_name'][0]['value']
        log.warn("This option is deprecated, it should not be used on new zanata server")

    if command_options.has_key('version_desc'):
        version_desc = command_options['version_desc'][0]['value']
        log.warn("This option is deprecated, it should not be used on new zanata server")

    zanatacmd = generate_zanatacmd(url, username, apikey)

    if command_options.has_key('disablesslcert'):
        zanatacmd.disable_ssl_cert_validation()

    zanatacmd.create_version(project_id, version_id, version_name, version_desc)

def po_pull(command_options, args):
    """
    Usage: zanata po pull [OPTIONS] {documents} {lang}

    Retrieve gettext project translation files from server

    Options:
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-id: id of the project (defaults to zanata.xml value)
        --project-version: id of the version (defaults to zanata.xml value)
        --dstdir: output folder (same as --transdir option)
        --dir: output folder for po files (same as --transdir)
        --transdir: output folder for po files
        --lang: language list
        --noskeleton: omit po files when translations not found
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pull(command_options, args, "gettext")

def po_push(command_options, args):
    """
    Usage: zanata po push [OPTIONS] {documents}

    Push software project source and translation files to server

    Options:
        -f: force to remove content on server side
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-id: id of the project (defaults to zanata.xml value)
        --project-version: id of the version (defaults to zanata.xml value)
        --dir: the path of the folder that contains pot files and po files,
               no need to specify --srcdir and --transdir if --dir option specified
        --srcdir: the path of the po folder(e.g. ./po)
        --srcfile: the path of the source file
        --transdir: the path of the folder that contains po files(e.g. ./po)
        --import-po: push local translations to server
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
        --lang: language list
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    command = PoPush()
    command.run(command_options, args)
    
def publican_pull(command_options, args):
    """
    Usage: zanata publican pull [OPTIONS] {documents} {lang}

    Retrieve translated publican content files from server

    Options:
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-id: id of the project (defaults to zanata.xml value)
        --project-version: id of the version (defaults to zanata.xml value)
        --dstdir: output folder (same as --transdir option)
        --dir: output folder (same as --transdir option)
        --transdir: translations will be written to this folder (one sub-folder per locale)
        --lang: language list
        --noskeleton: omit po files when translations not found
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    pull(command_options, args, "podir")

def publican_push(command_options, args):
    """
    Usage: zanata publican push OPTIONS {documents}

    Push publican content to server for translation.

    Argumensts: documents

    Options:
        -f: force to remove content on server side
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-id: id of the project (defaults to zanata.xml value)
        --project-version: id of the version (defaults to zanata.xml value)
        --dir: the path of the folder that contains pot folder and locale folders,
               no need to specify --srcdir and --transdir if --dir option specified
        --srcdir: the path of the pot folder (e.g. ./pot)
        --transdir: the path of the folder that contain locale folders
                    (e.g. ./myproject)
        --import-po: push local translations to server
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
        --lang: language list
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    command = PublicanPush()
    command.run(command_options, args)

def push(command_options, args):
    """
    Usage: zanata push OPTIONS {documents}

    Generic push command to push content to server for translation.

    Argumensts: documents

    Options:
        -f: force to remove content on server side
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-type: project type (gettext or podir)
        --project-id: id of the project (defaults to zanata.xml value)
        --project-version: id of the version (defaults to zanata.xml value)
        --srcdir: the path of the pot folder (e.g. ./pot)
        --srcfile: the path of the pot file(gettext project only)
        --transdir: the path of the folder that contain locale folders
                    (e.g. ./myproject)
        --push-trans: push local translations to server
        --push-trans-only: push translations only
        --push-type: source: push source document only, target: push translations only, same to push-trans-only 
                    both: push source and translations together, same to push-trans
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
        --lang: language list (defaults to zanata.xml locales)
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    command = GenericPush()
    command.run(command_options, args)

def pull(command_options, args, project_type = None):
    """
    Usage: zanata pull [OPTIONS] {documents} {lang}

    Retrieve translated publican content files from server

    Options:
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --project-type: project type (gettext or podir)
        --project-id: id of the project (defaults to zanata.xml value)
        --project-version: id of the version (defaults to zanata.xml value)
        --transdir: translations will be written to this folder
        --lang: language list (defaults to zanata.xml locales)
        --noskeletons: omit po files when translations not found
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    project_config = read_project_config(command_options)
    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    headers = http_headers(username,apikey,'application/vnd.zanata.Version+json')
    command = GenericPull()
    command.run(command_options, args, project_type,headers)

def glossary_push(command_options, args):
    """
    Usage: zanata glossary push [OPTIONS] GLOSSARY_POFILE

    Push glossary file in po/csv format to zanata server

    Options:
        --url: URL of zanata server
        --username: user name (defaults to zanata.ini value)
        --apikey: api key of user (defaults to zanata.ini value)
        --lang(po format): language of glossary file
        --sourcecommentsastarget(po format): treat extracted comments and references as target comments of term
                                  or treat as source reference of entry
        --commentcols(csv format): comments header of csv format glossary file
        --disable-ssl-cert disable ssl certificate validation in 0.7.x python-httplib2
    """
    locale_map = []

    optionsutil = OptionsUtil(command_options)
    url, username, apikey = optionsutil.apply_configfiles()
    get_version(url, command_options)
    log.info("Username: %s" % username)

    zanatacmd = ZanataCommand(url, username, apikey)

    if command_options.has_key('disablesslcert'):
        zanatacmd.disable_ssl_cert_validation()

    if args:
        path = os.path.join(os.getcwd(), args[0])
        if not os.path.isfile(path):
            log.error("Can not find glossary file %s under current path"%args[0])
            sys.exit(1)
    else:
        log.info("Please specify the file name of glossary file")
        sys.exit(1)

    basename, extension = os.path.splitext(path)

    locale_map = optionsutil.get_localemap()

    log.info("pushing glossary document %s to server"%args[0])

    if extension == '.po':
        if command_options.has_key('lang'):
            lang = command_options['lang'][0]['value'].split(',')[0]
        else:
            log.error("Please specify the language with '--lang' option")
            sys.exit(1)

        if lang in locale_map:
            lang = locale_map[lang]

        if command_options.has_key('sourcecomments'):
            sourcecomments = True
        else:
            sourcecomments = False
        zanatacmd.poglossary_push(path, url, username, apikey, lang, sourcecomments)
    elif extension == '.csv':
        if command_options.has_key('comment_cols'):
            comments_header = command_options['comment_cols'][0]['value'].split(',')
        else:
            log.error("Please specify the comments header, otherwise processing will be fault")
            sys.exit(1)
        
        zanatacmd.csvglossary_push(path, url, username, apikey, locale_map, comments_header)

def glossary_delete(command_options, args):
    lang = None
    optionsutil = OptionsUtil(command_options)
    url, username, apikey = optionsutil.apply_configfiles()
    get_version(url, command_options)
    log.info("Username: %s" % username)

    zanatacmd = ZanataCommand(url, username, apikey)

    if command_options.has_key('disablesslcert'):
        zanatacmd.disable_ssl_cert_validation()

    if command_options.has_key('lang'):
        lang = command_options['lang'][0]['value'].split(',')[0]
        log.info("Delete the glossary terms in %s on the server" % lang)
    else:
        log.info("Delete all the glossary terms on the server")

    zanatacmd.delete_glossary(url, username, apikey, lang)

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
    'glossary_delete': makeHandler(glossary_delete)
}

def signal_handler(signal, frame):
    print '\nPressed Ctrl+C! Stop processing!'
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
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        if command:
            print "Try zanata %(command)s --help' for more information." % {
                'command': command,
            }
        else:
            print usage
        sys.exit(2)
