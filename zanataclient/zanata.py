import getopt
import sys
import os
import string
import signal

from zanatalib.versionservice import VersionService
from zanatalib.client import ZanataResource
from zanatalib.error import UnAvaliableResourceException
from zanatalib.error import NoSuchFileException
from zanatalib.error import UnavailableServiceError
from zanatalib.outpututil import Logger
from zanatacmd import ZanataCommand
from parseconfig import ZanataConfig
from publicanutil import PublicanUtility

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
    'dstdir': [
        dict(
            type='command',
            long=['--dstdir'],
            metavar='DSTDIR',
        ),
    ],
    'transdir': [
        dict(
            type='command',
            long=['--transdir'],
            metavar='TRANSDIR',
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
    'importpo': [
        dict(
            type='command',
            long=['--import-po'],
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
    'push':[]
    }

usage = """Client for talking to a Zanata/Flies Server
Usage: zanata <command> [COMMANDOPTION]...

list of commands:
help                Display this help and exit
list                List all available projects
project info        Show information about a project
version info        Show information about a version
project create      Create a project
version create      Create a version within a project
publican pull       Pull the content of publican file
publican push       Push the content of publican file to Zanata/Flies server
po pull       Pull the content of software project file
po push       Push the content of software project file to Zanata/Flies server
push          Push the content of software project/docbook project to Zanata/Flies server

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
        log.info("merge option set to value %s" % merge)

        if not merge == 'auto' or not merge == 'import':
            log.info("merge option %s is not acceptable, change to default value 'auto'" % merge)
            merge = 'auto'
    else:
        merge = 'auto'

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

def process_srcdir(command_options, project_type):
    tmlfolder = ""

    if project_type == "publican":
        sub_folder = "pot"
    elif project_type == "software":
        sub_folder = "po"

    if command_options.has_key('srcdir'):
        tmlfolder = command_options['srcdir'][0]['value']
    elif command_options.has_key('dir'):
        folder = command_options['dir'][0]['value']
        tmlfolder = os.path.abspath(os.path.join(folder, sub_folder))
    else:
        tmlfolder = os.path.abspath(os.path.join(os.getcwd(), sub_folder))

    if not os.path.isdir(tmlfolder):
        log.error("Can not find source folder, please specify the source folder with '--srcdir' or '--dir' option")
        sys.exit(1)

    return tmlfolder

def process_srcfile(command_options):
    tmlfolder = ""
    file_path = ""

    if command_options.has_key('srcfile'):
        path = command_options['srcfile'][0]['value']
        file_path = os.path.abspath(path)
        import_file = file_path.split('/')[-1]
        tmlfolder = file_path.split(import_file)[0]
        if tmlfolder[-1] == '/':
            tmlfolder = tmlfolder[:-1]

    return tmlfolder, file_path

def process_transdir(command_options):
    trans_folder = ""
    
    if command_options.has_key('transdir'):
        trans_folder = command_options['transdir'][0]['value']
    elif command_options.has_key('dir'):
        trans_folder = command_options['dir'][0]['value']
    else:
        trans_folder = os.getcwd()

    return trans_folder

def create_outpath(command_options):
    if command_options.has_key('dstdir'):
        output = command_options['dstdir'][0]['value']
    elif command_options.has_key('dir'):
        output = command_options['dir'][0]['value']
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
        project_name = command_options['project_desc'][0]['value']

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

    Retrieve software project translation files from server

    Options:
        --username: user name
        --apikey: api key of user
        --project-id: id of the project
        --project-version: id of the version
        --dir: output folder for po files (same to --dstdir)
        --dstdir: output folder for po files
        --lang: language list'
    """
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

    outpath = create_outpath(command_options)

    locale_map = project_config['locale_map']
    zanatacmd = ZanataCommand()
    print filelist
    zanatacmd.pull_command(zanata, locale_map, project_id, iteration_id, filelist, lang_list, outpath, "software")

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
        --dir: the full path of the folder that contain pot files and po files,
               no need to specify --srcdir and --transdir if specified --dir option
        --srcdir: the full path of the po folder
        --srcfile: the full path of the source file
        --transdir: the full path of the folder that contain po files(e.g. zh_CN.po)
        --import-po: push local translations to server
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
    """
    push(command_options, args, "software")
    
def publican_pull(command_options, args):
    """
    Usage: zanata publican pull [OPTIONS] {documents} {lang}

    Retrieve translated publican content files from server

    Options:
        --username: user name
        --apikey: api key of user
        --project-id: id of the project
        --project-version: id of the version
        --dir: output folder for store loacle folders (same to --dstdir option)
        --dstdir: output folder for store loacle folders
        --lang: language list
    """
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

    outpath = create_outpath(command_options)

    locale_map = project_config['locale_map']

    zanatacmd = ZanataCommand()
    zanatacmd.pull_command(zanata, locale_map, project_id, iteration_id, filelist, lang_list, outpath, "publican")

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
        --dir: the full path of the folder that contain pot folder and locale folders,
               no need to specify --srcdir and --transdir if specified --dir option
        --srcdir: the full path of the pot folder (e.g. /home/jamesni/myproject/pot)
        --transdir: the full path of the folder that contain locale folders
                    (e.g. /home/jamesni/myproject)
        --import-po: push local translations to server
        --merge: override merge algorithm: auto (default) or import
        --no-copytrans: prevent server from copying translations from other versions
    """
    push(command_options, args, "publican")
    
def push(command_options, args, project_type = None):
    copytrans = True
    importpo = False
    force = False
    command_type = ''
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
    elif project_type:
        command_type = project_type
    else:
        log.error("The project type is unknown")
        sys.exit(1)
        
    if command_type == 'software' and command_options.has_key('srcfile'):
        tmlfolder, import_file = process_srcfile(command_options)
        filelist.append(import_file)
    else:
        tmlfolder = process_srcdir(command_options, command_type)
    
    if command_type == 'publican':
        log.info("POT directory (originals):%s" % tmlfolder)
    elif command_type == 'software':
        log.info("PO directory (originals):%s" % tmlfolder)
        
    if command_options.has_key('importpo'):
        log.info("Importing translation")
        import_param['transdir'] = process_transdir(command_options)
        log.info("Reading locale folders from %s" % import_param['transdir'])
        import_param['merge'] = process_merge(command_options)
        import_param['lang_list'] = get_lang_list(command_options, project_config)
        import_param['locale_map'] = project_config['locale_map']
        import_param['project_type'] = command_type
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
    zanatacmd.del_server_content(zanata, tmlfolder, project_id, iteration_id, filelist, force)

    if importpo:
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans, import_param)
    else:
        zanatacmd.push_command(zanata, filelist, tmlfolder, project_id, iteration_id, copytrans)    

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
    'push': makeHandler(push)
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
