#vim:set et sts=4 sw=4: 
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
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

import getopt
import sys
import os
import string
import signal
import subprocess

from zanatalib.versionservice import VersionService
from zanatalib.client import ZanataResource
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
    'glossary':['push']
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

def get_version(url):
    #Retrieve the version of client
    version_number = ""
    path = os.path.dirname(os.path.realpath(__file__))
    version_file = os.path.join(path, 'VERSION-FILE')

    try:
        version = open(version_file, 'rb')
        client_version = version.read()
        version.close()
        version_number = client_version.rstrip().strip('version: ')
    except IOError:
        log.error("Please run VERSION-GEN or 'make install' to generate VERSION-FILE")
        version_number = "UNKNOWN"

    #Retrieve the version of the zanata server
    version = VersionService(url)

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
        
def process_merge(command_options):
    merge = ""

    if command_options.has_key('merge'):
        merge = command_options['merge'][0]['value']
        if merge != 'auto' and merge != 'import':
            log.info("merge option %s is not acceptable, change to default value 'auto'" % merge)
            merge = 'auto'
    else:
        merge = 'auto'

    log.info("merge option set to value %s" % merge)

    return merge

def generate_zanataresource(url, username, apikey):
    if username and apikey:
        return ZanataResource(url, username, apikey)
    else:
        log.error("Please specify username and apikey in zanata.ini or with '--username' and '--apikey' options")
        sys.exit(1)

def get_lang_list(command_options, project_config):
    lang_list = []
    if command_options.has_key('lang'):
        lang_list = command_options['lang'][0]['value'].split(',')
    elif project_config.has_key('locale_map'):
        lang_list = project_config['locale_map'].keys()
    else:
        log.error("Please specify the language with '--lang' option or in zanata.xml")
        sys.exit(1)

    return lang_list

#################################
#
# Process source, trans and output folder
#
#################################
def find_po(folder):
    if not os.path.isdir(folder):
        log.error("Can not find source folder, please specify the source folder with '--srcdir' or 'dir' option")
        sys.exit(1)

    file_list = os.listdir(folder)  
    for item in file_list:
        full_path = os.path.join(folder, item)
        if full_path.endswith(".pot"):
            return True

    return False

def check_pofile(tmlfolder, project_type):
    folder = ""
    
    if project_type == "podir":
        folder_type = "pot"
    elif project_type == "gettext":
        folder_type = "po"

    if not os.path.isdir(tmlfolder):
        log.error("Can not find source folder, please specify the source folder with '--srcdir' or 'dir' option")
        sys.exit(1)
    
    sub_folder = os.path.join(tmlfolder, folder_type)

    if find_po(tmlfolder):
        return tmlfolder
    elif find_po(sub_folder):
        return sub_folder         
    else:
        log.error("The source folder is empty, please specify the valid source folder with '--srcdir' or 'dir' option")
        sys.exit(1)    

def process_srcdir(command_options, project_type, project_config, default_folder):
    tmlfolder = ""

    if command_options.has_key('srcdir'):
        tmlfolder = command_options['srcdir'][0]['value']
    elif default_folder:
        tmlfolder = os.path.abspath(default_folder)
    else:
        tmlfolder = os.path.abspath(os.getcwd())
     
    tmlfolder = check_pofile(tmlfolder, project_type)

    return tmlfolder

def process_srcfile(command_options):
    tmlfolder = ""
    file_path = ""

    if command_options.has_key('srcfile'):
        path = command_options['srcfile'][0]['value']
        file_path = os.path.abspath(path)
        import_file = file_path.split('/')[-1]
        tmlfolder = file_path[0:file_path.rfind('/')]

    return tmlfolder, file_path

def process_transdir(command_options, project_config, src_folder):
    trans_folder = ""

    if command_options.has_key('transdir'):
        trans_folder = command_options['transdir'][0]['value']
    elif src_folder:
        trans_folder = src_folder
    else:
        trans_folder = os.getcwd()

    return trans_folder

def create_outpath(command_options, output_folder):
    if command_options.has_key('transdir'):
        output = command_options['transdir'][0]['value']
    elif output_folder:
        output = output_folder
    else:
        output = os.getcwd()

    if not os.path.isdir(output):
        os.mkdir(output)

    return output

def search_file(path, filename):
    for root, dirs, names in os.walk(path):
        if filename in names:
            return os.path.join(root, filename)

    raise NoSuchFileException('Error 404', 'File %s not found' % filename)

def convert_serverversion(server_version):
    version = str(server_version.split('-')[0])
    main_ver = version[:3]
    version_number = string.atof(main_ver)
    return version_number

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
        --url address of the Zanata/Flies server, eg http://example.com/zanata
    """
    project_config = read_project_config(command_options)
    url = process_url(project_config, command_options)
    get_version(url)

    zanata = ZanataResource(url)
    zanatacmd = ZanataCommand()
    zanatacmd.list_projects(zanata)

def project_info(command_options, args):
    """
    Usage: zanata project info [OPTIONS]

    Show infomation about a project

    Options:
        --project-id: project id
    """
    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")
    url = process_url(project_config, command_options)
    get_version(url)

    if command_options.has_key('project_id'):
        project_id = command_options['project_id'][0]['value']
    else:
        project_id = project_config['project_id']

    if not project_id:
        log.error('Please use zanata project info --project-id=project_id or zanata.xml to specify the project id')
        sys.exit(1)

    zanata = ZanataResource(url)
    zanatacmd = ZanataCommand()
    zanatacmd.project_info(zanata, project_id)

def version_info(command_options, args):
    """
    Usage: zanata version info [OPTIONS]

    Show infomation about a version

    Options:
        --project-id: project id
        --project-version: id of project version
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

    get_version(url)

    if command_options.has_key('project_id'):
        project_id = command_options['project_id'][0]['value']

    if command_options.has_key('project_version'):
        iteration_id = command_options['project_version'][0]['value']

    if not iteration_id or not project_id:
        log.error("Please use zanata version info --project-id=project_id --project-version=project_version to retrieve the version")
        sys.exit(1)

    zanata = ZanataResource(url)

    zanatacmd = ZanataCommand()
    zanatacmd.version_info(zanata, project_id, iteration_id)

def create_project(command_options, args):
    """
    Usage: zanata project create [PROJECT_ID] [OPTIONS]

    Create a project

    Options:
        --username: user name
        --apikey: api key of user
        --project-name: project name
        --project-desc: project description
    """
    project_id = ""
    project_name = ""
    project_desc = ""
    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    get_version(url)

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

    zanata = generate_zanataresource(url, username, apikey)
    zanatacmd = ZanataCommand()
    zanatacmd.create_project(zanata, project_id, project_name, project_desc)

def create_version(command_options, args):
    """
    Usage: zanata version create [VERSION_ID] [OPTIONS]

    Create a version

    Options:
        --username: user name
        --apikey: api key of user
        --project-id: id of the project
        --version-name: version name
        --version-desc: version description
    """
    project_id = ""
    version_name = ""
    version_desc = ""
    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    server_version = get_version(url)

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
        log.error("Please provide ITERATION_ID for creating iteration")
        sys.exit(1)

    if command_options.has_key('version_name'):
        version_name = command_options['version_name'][0]['value']

    if command_options.has_key('version_desc'):
        version_desc = command_options['version_desc'][0]['value']

    if server_version:
        version_number = convert_serverversion(server_version)

        if version_number <= 1.2 and not version_name:
            version_name = args[0]
    else:
        if not version_name:
            version_name = args[0]

    zanata = generate_zanataresource(url, username, apikey)
    zanatacmd = ZanataCommand()
    zanatacmd.create_version(zanata, project_id, version_id, version_name, version_desc)

def po_pull(command_options, args):
    """
    Usage: zanata po pull [OPTIONS] {documents} {lang}

    Retrieve gettext project translation files from server

    Options:
        --username: user name
        --apikey: api key of user
        --project-id: id of the project
        --project-version: id of the version
        --dstdir: output folder (same as --transdir option)
        --dir: output folder for po files (same as --transdir)
        --transdir: output folder for po files
        --lang: language list'
        --noskeleton: omit po files when translations not found
    """
    pull(command_options, args, "gettext")

def po_push(command_options, args):
    """
    Usage: zanata po push [OPTIONS] {documents}

    Push software project source and translation files to server

    Options:
        -f: force to remove content on server side
        --username: user name
        --apikey: api key of user
        --project-id: id of the project
        --project-version: id of the version
        --dir: the path of the folder that contains pot files and po files,
               no need to specify --srcdir and --transdir if --dir option specified
        --srcdir: the path of the po folder(e.g. ./po)
        --srcfile: the path of the source file
        --transdir: the path of the folder that contains po files(e.g. ./po)
        --import-po: push local translations to server
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
        --lang: language list
    """
    copytrans = True
    importpo = False
    force = False
    dir_option = False
    command_type = ''
    default_folder = None
    tmlfolder = ""
    filelist = []

    import_param = {'transdir': '', 'merge': 'auto', 'lang_list': {}, 'locale_map': {}, 'project_type': 'gettext'}

    zanatacmd = ZanataCommand()

    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    get_version(url)

    zanata = generate_zanataresource(url, username, apikey)

    project_id, iteration_id = zanatacmd.check_project(zanata, command_options, project_config)
    log.info("Username: %s" % username)
    log.info("Source language: en-US")

    if command_options.has_key('nocopytrans'):
        copytrans = False

    log.info("Copy previous translations:%s" % copytrans)

    if command_options.has_key('srcfile'):
        tmlfolder, import_file = process_srcfile(command_options)
        filelist.append(import_file)

    #Keep dir option for publican/po push
    if command_options.has_key('dir'):
        default_folder = command_options['dir'][0]['value']
    
    tmlfolder = process_srcdir(command_options, "gettext", project_config, default_folder)
            
    if not os.path.isdir(tmlfolder):
        log.error("Can not find source folder, please specify the source folder with '--srcdir' or 'dir' option")
        sys.exit(1)
    
    log.info("PO directory (originals):%s" % tmlfolder)

    if command_options.has_key('importpo'):
        importpo = True

    if command_options.has_key('pushtrans'):
        log.info("please use --import-po for old publican push command")
        importpo = True

    if importpo:
        log.info("Importing translation")
        import_param['transdir'] = process_transdir(command_options, project_config, tmlfolder)
        log.info("Reading locale folders from %s" % import_param['transdir'])
        import_param['merge'] = process_merge(command_options)
        import_param['lang_list'] = get_lang_list(command_options, project_config)
        if project_config.has_key('locale_map'):
            import_param['locale_map'] = project_config['locale_map']
        else:
            import_param['locale_map'] = None
        importpo = True
    else:
        log.info("Importing source documents only")

    if args:
        try:
            full_path = search_file(tmlfolder, args[0])
            filelist.append(full_path)
        except NoSuchFileException, e:
            log.error(e.msg)
            sys.exit(1)
    else:
        if not command_options.has_key('srcfile'):
            #get all the pot files from the template folder
            publicanutil = PublicanUtility()
            filelist = publicanutil.get_file_list(tmlfolder, ".pot")

            if not filelist:
                log.error("The template folder is empty")
                sys.exit(1)

        if command_options.has_key('force'):
            force = True
        zanatacmd.del_server_content(zanata, tmlfolder, project_id, iteration_id, filelist, force, "gettext")

    if importpo:
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans, import_param)
    else:
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans)
    
def publican_pull(command_options, args):
    """
    Usage: zanata publican pull [OPTIONS] {documents} {lang}

    Retrieve translated publican content files from server

    Options:
        --username: user name
        --apikey: api key of user
        --project-id: id of the project
        --project-version: id of the version
        --dstdir: output folder (same as --transdir option)
        --dir: output folder (same as --transdir option)
        --transdir: translations will be written to this folder (one sub-folder per locale)
        --lang: language list
        --noskeleton: omit po files when translations not found
    """
    pull(command_options, args, "podir")

def publican_push(command_options, args):
    """
    Usage: zanata publican push OPTIONS {documents}

    Push publican content to server for translation.

    Argumensts: documents

    Options:
        -f: force to remove content on server side
        --username: user name
        --apikey: api key of user
        --project-id: id of the project
        --project-version: id of the version
        --dir: the path of the folder that contains pot folder and locale folders,
               no need to specify --srcdir and --transdir if --dir option specified
        --srcdir: the path of the pot folder (e.g. ./pot)
        --transdir: the path of the folder that contain locale folders
                    (e.g. ./myproject)
        --import-po: push local translations to server
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
        --lang: language list
    """
    copytrans = True
    importpo = False
    force = False
    dir_option = False
    default_folder = None
    deletefiles = False
    tmlfolder = ""
    filelist = []

    import_param = {'transdir': '', 'merge': 'auto', 'lang_list': {}, 'locale_map': {}, 'project_type': 'podir'}

    zanatacmd = ZanataCommand()

    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    get_version(url)

    zanata = generate_zanataresource(url, username, apikey)

    project_id, iteration_id = zanatacmd.check_project(zanata, command_options, project_config)
    log.info("Username: %s" % username)
    log.info("Source language: en-US")

    if command_options.has_key('nocopytrans'):
        copytrans = False

    log.info("Copy previous translations:%s" % copytrans)

    #Keep dir option for publican/po push
    if command_options.has_key('dir'):
        default_folder = command_options['dir'][0]['value']
    
    tmlfolder = process_srcdir(command_options, "podir", project_config, default_folder)
    
    if args:
        try:
            full_path = search_file(tmlfolder, args[0])
            filelist.append(full_path)
        except NoSuchFileException, e:
            log.error(e.msg)
            sys.exit(1)
    else:
        #get all the pot files from the template folder
        publicanutil = PublicanUtility()
        filelist = publicanutil.get_file_list(tmlfolder, ".pot")

        if not filelist:
            log.error("The template folder is empty")
            sys.exit(1)

        deletefiles = True

    if command_options.has_key('force'):
        force = True
            
    log.info("POT directory (originals):%s" % tmlfolder)

    if command_options.has_key('importpo'):
        importpo = True

    if command_options.has_key('pushtrans'):
        log.info("please use --import-po for old publican push command")
        importpo = True
        
    if importpo:
        log.info("Importing translation")
        import_param['transdir'] = process_transdir(command_options, project_config, None)
        log.info("Reading locale folders from %s" % import_param['transdir'])
        import_param['merge'] = process_merge(command_options)
        import_param['lang_list'] = get_lang_list(command_options, project_config)
        if project_config.has_key('locale_map'):
            import_param['locale_map'] = project_config['locale_map']
        else:
            import_param['locale_map'] = None
        if deletefiles:            
            zanatacmd.del_server_content(zanata, tmlfolder, project_id, iteration_id, filelist, force, "podir")
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans, import_param)
    else:
        log.info("Importing source documents only")
        if deletefiles:
            zanatacmd.del_server_content(zanata, tmlfolder, project_id, iteration_id, filelist, force, "podir")
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans)
    
def push(command_options, args, project_type = None):
    """
    Usage: zanata push OPTIONS {documents}

    Generic push command to push content to server for translation.

    Argumensts: documents

    Options:
        -f: force to remove content on server side
        --username: user name
        --apikey: api key of user
        --project-type: project type (gettext or podir)
        --project-id: id of the project
        --project-version: id of the version
        --srcdir: the path of the pot folder (e.g. ./pot)
        --srcfile: the path of the pot file(gettext project only)
        --transdir: the path of the folder that contain locale folders
                    (e.g. ./myproject)
        --push-trans: push local translations to server
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
        --lang: language list
    """
    copytrans = True
    importpo = False
    force = False
    dir_option = False
    deletefiles = False
    command_type = ''
    default_folder = ""
    tmlfolder = ""
    filelist = []

    import_param = {'transdir': '', 'merge': 'auto', 'lang_list': {}, 'locale_map': {}, 'project_type': ''}

    zanatacmd = ZanataCommand()

    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    get_version(url)

    zanata = generate_zanataresource(url, username, apikey)

    project_id, iteration_id = zanatacmd.check_project(zanata, command_options, project_config)
    log.info("Username: %s" % username)
    log.info("Source language: en-US")

    if command_options.has_key('nocopytrans'):
        copytrans = False

    log.info("Copy previous translations:%s" % copytrans)

    if command_options.has_key('project_type'):
        command_type = command_options['project_type'][0]['value']
    elif project_config['project_type']:
        command_type = project_config['project_type']
    else:
        log.error("The project type is unknown")
        sys.exit(1)
    
    if command_type != 'podir' and command_type != 'gettext':
        log.error("The project type is not correct, please use 'podir' and 'gettext' as project type")
        sys.exit(1)

    if command_options.has_key('srcfile'):
        if command_type == 'gettext': 
            tmlfolder, import_file = process_srcfile(command_options)
            filelist.append(import_file)
        else:
            log.warn("srcfile option is not used for podir type project, ignored")

    #Disable dir option for generic push command
    if command_options.has_key('dir'):
        log.warn("dir option is disabled in push command, please use --srcdir and --transdir, or specify value in zanata.xml")
    
    if command_type != 'podir' and command_type != 'gettext':
        log.error("The project type is unknown")
        sys.exit(1)

    if tmlfolder == "":        
        tmlfolder = process_srcdir(command_options, command_type, project_config, None)
        
    if not os.path.isdir(tmlfolder):
        log.error("Can not find source folder, please specify the source folder with '--srcdir' or using zanata.xml")
        sys.exit(1)
    
    if args:
        try:
            full_path = search_file(tmlfolder, args[0])
            filelist.append(full_path)
        except NoSuchFileException, e:
            log.error(e.msg)
            sys.exit(1)
    else:
        #get all the pot files from the template folder
        publicanutil = PublicanUtility()
        filelist = publicanutil.get_file_list(tmlfolder, ".pot")

        if not filelist:
            log.error("The template folder is empty")
            sys.exit(1)
        deletefiles = True

    if command_options.has_key('force'):
        force = True
    
    if command_type == 'podir':
        log.info("POT directory (originals):%s" % tmlfolder)
        folder = None;
    elif command_type == 'gettext':
        log.info("PO directory (originals):%s" % tmlfolder)
        folder = tmlfolder

    if command_options.has_key('importpo'):
        log.info("--import-po option has renamed to --push-trans, please use --push-trans instead")
        importpo = True

    if command_options.has_key('pushtrans'):
        importpo = True

    if importpo:
        log.info("Importing translation")
        import_param['transdir'] = process_transdir(command_options, project_config, folder)
        log.info("Reading locale folders from %s" % import_param['transdir'])
        import_param['merge'] = process_merge(command_options)
        import_param['lang_list'] = get_lang_list(command_options, project_config)
        if project_config.has_key('locale_map'):
            import_param['locale_map'] = project_config['locale_map']
        else:
            import_param['locale_map'] = None
        import_param['project_type'] = command_type
        if deletefiles:
            zanatacmd.del_server_content(zanata, tmlfolder, project_id, iteration_id, filelist, force, command_type)
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans, import_param)
    else:
        log.info("Importing source documents only")
        if deletefiles:
            zanatacmd.del_server_content(zanata, tmlfolder, project_id, iteration_id, filelist, force, command_type)
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans) 

def pull(command_options, args, project_type = None):
    """
    Usage: zanata pull [OPTIONS] {documents} {lang}

    Retrieve translated publican content files from server

    Options:
        --username: user name
        --apikey: api key of user
        --project-type: project type (gettext or podir)
        --project-id: id of the project
        --project-version: id of the version
        --transdir: translations will be written to this folder
        --lang: language list
    """
    dir_option = False
    create_skeletons = True
    filelist = []
    zanatacmd = ZanataCommand()

    project_config = read_project_config(command_options)

    if not project_config:
        log.info("Can not find zanata.xml, please specify the path of zanata.xml")

    url = process_url(project_config, command_options)
    username, apikey = read_user_config(url, command_options)
    get_version(url)

    zanata = generate_zanataresource(url, username, apikey)

    #if file not specified, push all the files in pot folder to zanata server
    project_id, iteration_id = zanatacmd.check_project(zanata, command_options, project_config)
    log.info("Username: %s" % username)

    lang_list = get_lang_list(command_options, project_config)

    #list the files in project
    try:
        filelist = zanata.documents.get_file_list(project_id, iteration_id)
    except Exception, e:
        log.error(str(e))
        sys.exit(1)

    if project_config.has_key('locale_map'):
        locale_map = project_config['locale_map']
    else:
        locale_map = None
    
    if project_type:
        command_type = project_type
        dir_option = True
    elif command_options.has_key('project_type'):
        command_type = command_options['project_type'][0]['value']
    elif project_config['project_type']:
        command_type = project_config['project_type']
    else:
        log.error("The project type is unknown")
        sys.exit(1)

    if dir_option:
        #Keep dir option for publican/po pull
        if command_options.has_key('dir'):
            output_folder = command_options['dir'][0]['value']
        else:
            output_folder = None

        if command_options.has_key('dstdir'):
            output_folder = command_options['dstdir'][0]['value']
    else:
        #Disable dir option for generic pull command
        if command_options.has_key('dir'):
            log.warn("dir option is disabled in pull command, please use --transdir, or specify value in zanata.xml")
        else:
            output_folder = None        
                     
        if command_options.has_key('dstdir'):
            log.warn("dstdir option is changed to transdir option for generic pull command")
            output_folder = command_options['dstdir'][0]['value']
    
    if command_options.has_key('noskeletons'):
        create_skeletons = False

    outpath = create_outpath(command_options, output_folder)

    zanatacmd = ZanataCommand()
    zanatacmd.pull_command(zanata, locale_map, project_id, iteration_id, filelist, lang_list, outpath, command_type,
    create_skeletons)

def glossary_push(command_options, args):
    """
    Usage: zanata glossary push [OPTIONS] GLOSSARY_POFILE

    Push glossary file in po/csv format to zanata server

    Options:
        --url: URL of zanata server
        --username: user name
        --apikey: api key of user
        --lang(po format): language of glossary file
        --sourcecommentsastarget(po format): treat extracted comments and references as target comments of term
                                  or treat as source reference of entry
        --commentcols(csv format): comments header of csv format glossary file
    """
    locale_map = []
    zanatacmd = ZanataCommand()
    optionsutil = OptionsUtil(command_options)
    url, username, apikey = optionsutil.apply_configfiles()
    get_version(url)
    log.info("Username: %s" % username)
 
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

    log.info("pushing glossary document %s to server"%args[0]);

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
    'glossary_push': makeHandler(glossary_push)
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
