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

import os
import sys
import string

from zanatalib.error import UnAvaliableResourceException
from zanatalib.error import NoSuchFileException
from zanatalib.error import UnavailableServiceError
from zanatacmd import ZanataCommand
from parseconfig import ZanataConfig
from publicanutil import PublicanUtility
from zanatalib.logger import Logger

log = Logger()

class Push:
    def read_project_config(self, command_options):
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

    def process_url(self, project_config, command_options):
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

    def read_user_config(self, url, command_options):
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

        #The value in commandline options will overwrite the value in user-config file
        if command_options.has_key('user_name'):
            user_name = command_options['user_name'][0]['value']

        if command_options.has_key('key'):
            apikey = command_options['key'][0]['value']

        return (user_name, apikey)

    def get_client_version(self, command_options):
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

        return version_number
            
    def process_merge(self, command_options):
        merge = ""

        if command_options.has_key('merge'):
            merge = command_options['merge'][0]['value']
            if merge != 'auto' and merge != 'import':
                log.info("merge option %s is not recognized, assuming default value 'auto'" % merge)
                merge = 'auto'
        else:
            merge = 'auto'

        log.info("merge option set to value %s" % merge)

        return merge

    def generate_zanatacmd(self, url, username, apikey):
        if username and apikey:
            return ZanataCommand(url, username, apikey)
        else:
            log.error("Please specify username and apikey in zanata.ini or with '--username' and '--apikey' options")
            sys.exit(1)

    def get_lang_list(self, command_options, project_config):
        lang_list = []
        if command_options.has_key('lang'):
            lang_list = command_options['lang'][0]['value'].split(',')
        elif project_config.has_key('locale_map'):
            lang_list = project_config['locale_map'].keys()
        else:
            log.error("Please specify the language with '--lang' option or in zanata.xml")
            sys.exit(1)

        return lang_list

    def process_srcdir_withsub(self, command_options):
        tmlfolder = ""

        if command_options.has_key('srcdir'):
            tmlfolder = command_options['srcdir'][0]['value']
        elif command_options.has_key('dir'):
            #Keep dir option for publican/po push
            tmlfolder = command_options['dir'][0]['value']
        else:
            tmlfolder = os.path.abspath(os.getcwd())

        if not os.path.isdir(tmlfolder):
            log.error("Can not find source folder, please specify the source folder with '--srcdir' or 'dir' option")
            sys.exit(1)

        return tmlfolder

    def process_srcdir(self, command_options):
        tmlfolder = ""

        if command_options.has_key('srcdir'):
            tmlfolder = command_options['srcdir'][0]['value']
        else:
            tmlfolder = os.path.abspath(os.getcwd())

        return tmlfolder

    def process_srcfile(self, command_options):
        tmlfolder = ""
        file_path = ""

        if command_options.has_key('srcfile'):
            path = command_options['srcfile'][0]['value']
            file_path = os.path.abspath(path)
            tmlfolder = file_path[0:file_path.rfind('/')]

        return tmlfolder, file_path

    def process_transdir(self, command_options, src_folder):
        trans_folder = ""

        if command_options.has_key('transdir'):
            trans_folder = command_options['transdir'][0]['value']
        elif src_folder:
            trans_folder = src_folder
        else:
            trans_folder = os.getcwd()

        return trans_folder

    def create_outpath(self, command_options, output_folder):
        if command_options.has_key('transdir'):
            output = command_options['transdir'][0]['value']
        elif output_folder:
            output = output_folder
        else:
            output = os.getcwd()

        if not os.path.isdir(output):
            os.mkdir(output)

        return output

    def search_file(self, path, filename):
        for root, dirs, names in os.walk(path):
            if filename in names:
                return os.path.join(root, filename)

        raise NoSuchFileException('Error 404', 'File %s not found' % filename)

    def check_plural_support(self, server_version):
        if server_version == None:
            return False

        version = str(server_version.split('-')[0])
        main_ver = version[:3]
        version_number = string.atof(main_ver)

        if version_number >= 1.6:
            return True
        else:
            return False

    def get_importpo(self, command_options):
        importpo = False

        if command_options.has_key('importpo'):
            importpo = True
        elif command_options.has_key('pushtrans'):
            importpo = True
            log.info("please use --import-po for old publican push command")
        
        return importpo

    def get_pushtrans(self, command_options):
        pushtrans = False

        if command_options.has_key('pushtrans'):
            pushtrans = True
        elif command_options.has_key('importpo'):
            pushtrans = True
            log.info("--import-po option has renamed to --push-trans, please use --push-trans instead")

        return pushtrans

    def get_importparam(self, project_type, command_options, project_config, folder):
        import_param = {'transdir': '', 'merge': 'auto', 'lang_list': {}, 'locale_map': {}, 'project_type': 'gettext'}
        
        import_param['transdir'] = self.process_transdir(command_options, folder)
        log.info("Reading locale folders from %s" % import_param['transdir'])
        import_param['merge'] = self.process_merge(command_options)
        import_param['lang_list'] = self.get_lang_list(command_options, project_config)
        
        if project_config.has_key('locale_map'):
            import_param['locale_map'] = project_config['locale_map']
        else:
            import_param['locale_map'] = None
        
        import_param['project_type'] = project_type

        return import_param

    def get_projectinfo(self, command_options):
        project_id = ''
        version_id = ''
        
        project_config = self.read_project_config(command_options)

        if not project_config:
            log.info("Can not find zanata.xml, please specify the path of zanata.xml")

        url = self.process_url(project_config, command_options)

        if command_options.has_key('project_id'):
            project_id =  command_options['project_id'][0]['value'] 
        else:
            if project_config.has_key('project_id'):
                project_id = project_config['project_id']

        if command_options.has_key('project_version'):
            version_id = command_options['project_version'][0]['value'] 
        else:
            if project_config.has_key('project_version'):
                version_id = project_config['project_version']

        if command_options.has_key('project_type'):
            project_type = command_options['project_type'][0]['value']
        elif project_config['project_type']:
            project_type = project_config['project_type']

        if not project_id:
            log.error("Please specify a valid project id in zanata.xml or with '--project-id' option")
            sys.exit(1)

        if not version_id:
            log.error("Please specify a valid version id in zanata.xml or with '--project-version' option")
            sys.exit(1)

        return url, project_id, version_id, project_type, project_config

    def create_zanatacmd(self, url, command_options):
        server_version = ""

        username, apikey = self.read_user_config(url, command_options)

        zanatacmd = self.generate_zanatacmd(url, username, apikey)

        if command_options.has_key('disablesslcert'):
            zanatacmd.disable_ssl_cert_validation()

        client_version = self.get_client_version(command_options)
        server_version = zanatacmd.get_server_version(url)

        return zanatacmd, username, client_version, server_version

    def create_versioninfo(self, client_version, server_version):
        version_info =  "zanata python client version: "+client_version        
        
        if server_version:
            version_info = version_info+", zanata server API version: "+server_version

        return version_info

    def log_message(self, url, version_info, project_id, version_id, username):
        log.info("zanata server: %s" % url)
        log.info(version_info)
        log.info("Project: %s" % project_id)
        log.info("Version: %s" % version_id)        
        log.info("Username: %s" % username)
        log.info("Source language: en-US")

class GenericPush(Push):
    def run(self, command_options, args):
        copytrans = True
        pushtrans = None
        push_trans_only = False
        force = False
        deletefiles = False
        plural_support = False
        project_type = ''
        tmlfolder = ""
        filelist = []

        url, project_id, version_id, project_type, project_config = self.get_projectinfo(command_options)
        zanatacmd, username, client_version, server_version = self.create_zanatacmd(url, command_options)
        plural_support = self.check_plural_support(server_version)
        version_info = self.create_versioninfo(client_version, server_version)
        self.log_message(url, version_info, project_id, version_id, username)
        zanatacmd.verify_project(project_id, version_id)

        if command_options.has_key('nocopytrans'):
            copytrans = False

        log.info("Copy previous translations:%s" % copytrans)

        if not project_type:
            log.error("The project type is unknown")
            sys.exit(1)
        elif project_type != 'podir' and project_type != 'gettext':
            log.error("The project type is not correct, please use 'podir' and 'gettext' as project type")
            sys.exit(1)

        if command_options.has_key('srcfile'):
            if project_type == 'gettext': 
                tmlfolder, import_file = self.process_srcfile(command_options)
                filelist.append(import_file)
            else:
                log.warn("srcfile option is not used for podir type project, ignored")

        #Disable dir option for generic push command
        if command_options.has_key('dir'):
            log.warn("dir option is disabled in push command, please use --srcdir and --transdir, or specify value in zanata.xml")

        if command_options.has_key('pushtype'):
            if command_options.has_key('pushtrans'):
                log.warn("--push-trans option will be omitted")
            push_type = command_options['pushtype'][0]['value']
            if push_type == "source":
                pushtrans = False
            elif push_type == "target":
                push_trans_only = True
            elif push_type == "both":
                pushtrans = True

        if command_options.has_key('pushtransonly'):
            push_trans_only = True

        if push_trans_only:
            transfolder = self.process_transdir(command_options, "")
            merge = self.process_merge(command_options)
            lang_list = self.get_lang_list(command_options, project_config)

            if project_config.has_key('locale_map'):
                locale_map = project_config['locale_map']
            else:
                locale_map = None

            zanatacmd.push_trans_command(transfolder, project_id, version_id, lang_list, locale_map, project_type, merge)
            sys.exit(0)

        if tmlfolder == "":
            tmlfolder = self.process_srcdir(command_options)

        if not os.path.isdir(tmlfolder):
            log.error("Can not find source folder, please specify the source folder with '--srcdir' or using zanata.xml")
            sys.exit(1)

        if args:
            try:
                full_path = self.search_file(tmlfolder, args[0])
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

        if project_type == 'podir':
            log.info("POT directory (originals):%s" % tmlfolder)
            folder = None
        elif project_type == 'gettext':
            log.info("PO directory (originals):%s" % tmlfolder)
            folder = tmlfolder

        if pushtrans is None:
            pushtrans = self.get_pushtrans(command_options)

        if deletefiles:
            zanatacmd.del_server_content(tmlfolder, project_id, version_id, filelist, force, project_type)

        if pushtrans:
            log.info("Importing translation")
            import_param = self.get_importparam(project_type, command_options,  project_config, folder)
            zanatacmd.push_command(filelist, tmlfolder, project_id, version_id, copytrans, plural_support, import_param)
        else:
            log.info("Importing source documents only")
            zanatacmd.push_command(filelist, tmlfolder, project_id, version_id, copytrans, plural_support)

class PublicanPush(Push):
    def run(self, command_options, args):
        copytrans = True
        importpo = False
        force = False
        deletefiles = False
        plural_support = False
        tmlfolder = ""
        filelist = []

        url, project_id, version_id, project_type, project_config = self.get_projectinfo(command_options)
        zanatacmd, username, client_version, server_version = self.create_zanatacmd(url, command_options)
        plural_support = self.check_plural_support(server_version)
        version_info = self.create_versioninfo(client_version, server_version)
        self.log_message(url, version_info, project_id, version_id, username)
        zanatacmd.verify_project(project_id, version_id)

        if command_options.has_key('nocopytrans'):
            copytrans = False

        log.info("Copy previous translations:%s" % copytrans)

        tmlfolder = self.process_srcdir_withsub(command_options)

        if args:
            try:
                full_path = self.search_file(tmlfolder, args[0])
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

        importpo = self.get_importpo(command_options)
        
        if deletefiles:
            zanatacmd.del_server_content(tmlfolder, project_id, version_id, filelist, force, "podir")
        
        if importpo:
            import_param = self.get_importparam("podir", command_options,  project_config, tmlfolder)
            zanatacmd.push_command(filelist, tmlfolder, project_id, version_id, copytrans, plural_support, import_param)
        else:
            log.info("Importing source documents only")
            zanatacmd.push_command(filelist, tmlfolder, project_id, version_id, copytrans, plural_support)

class PoPush(Push):
    def run(self, command_options, args):
        copytrans = True
        importpo = False
        force = False
        tmlfolder = ""
        plural_support = False
        filelist = []

        url, project_id, version_id, project_type, project_config = self.get_projectinfo(command_options)
        zanatacmd, username, client_version, server_version = self.create_zanatacmd(url, command_options)
        plural_support = self.check_plural_support(server_version)
        version_info = self.create_versioninfo(client_version, server_version)
        self.log_message(url, version_info, project_id, version_id, username)
        zanatacmd.verify_project(project_id, version_id)

        if command_options.has_key('nocopytrans'):
            copytrans = False

        log.info("Copy previous translations:%s" % copytrans)

        if command_options.has_key('srcfile'):
            tmlfolder, import_file = self.process_srcfile(command_options)
            filelist.append(import_file)

        tmlfolder = self.process_srcdir_withsub(command_options)

        if not os.path.isdir(tmlfolder):
            log.error("Can not find source folder, please specify the source folder with '--srcdir' or 'dir' option")
            sys.exit(1)

        log.info("PO directory (originals):%s" % tmlfolder)

        importpo = self.get_importpo(command_options)

        if importpo:
            log.info("Importing translation")
            import_param = self.get_importparam("gettext", command_options,  project_config, tmlfolder)
        else:
            log.info("Importing source documents only")

        if args:
            try:
                full_path = self.search_file(tmlfolder, args[0])
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
            zanatacmd.del_server_content(tmlfolder, project_id, version_id, filelist, force, "gettext")

        if importpo:
            zanatacmd.push_command(filelist, tmlfolder, project_id, version_id, copytrans, plural_support, import_param)
        else:
            zanatacmd.push_command(filelist, tmlfolder, project_id, version_id, copytrans, plural_support)
        
