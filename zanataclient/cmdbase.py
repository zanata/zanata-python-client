# vim: set et sts=4 sw=4:
#
# Zanata Python Client
#
# Copyright (c) 2015 Sundeep Anand <suanand@redhat.com>
# Copyright (c) 2015 Red Hat, Inc.
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
import string
import sys

from .publicanutil import PublicanUtility
from .zanatacmd import ZanataCommand
from .zanatalib.error import NoSuchFileException
from .zanatalib.logger import Logger


log = Logger()


class CommandsInit(object):
    _fields = ['args', 'context_data']

    def __init__(self, *args, **kargs):
        for name, val in zip(self._fields, args):
            setattr(self, name, val)
        for key, value in kargs.items():
            setattr(self, key, value)

    def check_essential(self, item, message):
        if not item:
            log.error(message)
            sys.exit(1)
        return item


class CommandsBase(CommandsInit):
    """
    This is base class for zpc commands
    """
    def __init__(self, *args, **kargs):
        super(CommandsBase, self).__init__(*args, **kargs)
        self.zanatacmd = self.create_zanatacmd()

    def create_zanatacmd(self):
        zanatacmd = self.generate_zanatacmd(
            self.context_data.get('url'),
            self.context_data.get('http_headers')
        )
        if 'disablesslcert' in self.context_data:
            zanatacmd.disable_ssl_cert_validation()
        return zanatacmd

    def generate_zanatacmd(self, url, headers):
        if self.context_data.get('auth_req'):
            if not headers.get('X-Auth-User') and not headers.get('X-Auth-Token'):
                log.error("Please specify username and apikey in zanata.ini or with '--username' and '--apikey' options")
                sys.exit(1)
        return ZanataCommand(url, headers)


class ListProjects(CommandsBase):
    def __init__(self, *args, **kargs):
        super(ListProjects, self).__init__(*args, **kargs)

    def run(self):
        self.zanatacmd.list_projects()


class ProjectInfo(CommandsBase):
    def __init__(self, *args, **kargs):
        super(ProjectInfo, self).__init__(*args, **kargs)

    def run(self):
        if self.context_data.get('project_id'):
            self.zanatacmd.project_info(self.context_data['project_id'])
        else:
            log.error('Please use zanata project info --project-id=project_id or zanata.xml to specify the project id')
            sys.exit(1)


class VersionInfo(CommandsBase):
    def __init__(self, *args, **kargs):
        super(VersionInfo, self).__init__(*args, **kargs)

    def run(self):
        if self.context_data.get('project_id') and self.context_data.get('project_version'):
            project_id, iteration_id = self.context_data['project_id'], self.context_data['project_version']
            self.zanatacmd.version_info(project_id, iteration_id)
        else:
            log.error("Please use zanata version info --project-id=project_id "
                      "--project-version=project_version to retrieve the version")
            sys.exit(1)


class CreateProject(CommandsBase):
    def __init__(self, *args, **kargs):
        super(CreateProject, self).__init__(*args, **kargs)

    def run(self):
        if len(self.args) > 0:
            project_id = self.args[0]
        else:
            log.error("Please provide PROJECT_ID for creating project")
            sys.exit(1)
        self.check_essential(
            self.context_data.get('project_name'),
            "Please specify project name with '--project-name' option"
        )
        project_name = self.context_data['project_name']
        project_desc = self.context_data['project_desc'] \
            if self.context_data.get('project_desc') else ''
        project_type = (
            self.context_data['project_type']
            if self.context_data.get('project_type') and (self.context_data.get('project_type')
                                                          in ('gettext', 'podir'))
            else 'IterationProject'
        )
        self.zanatacmd.create_project(
            project_id, project_name, project_desc, project_type
        )


class CreateVersion(CommandsBase):
    def __init__(self, *args, **kargs):
        super(CreateVersion, self).__init__(*args, **kargs)

    def run(self):
        if self.context_data.get('project_id'):
            project_id = self.context_data['project_id']
        else:
            log.error("Please specify PROJECT_ID with --project-id option or using zanata.xml")
            sys.exit(1)
        log.info("Project ID: %s" % project_id)

        if self.args:
            version_id = self.args[0]
        else:
            log.error("Please provide ITERATION_ID for creating version")
            sys.exit(1)
        version_name, version_desc = None, None
        if self.context_data.get('version_name'):
            version_name = self.context_data['version_name']
            log.warn("--version-name is deprecated, it should not be used on new zanata server")
        if self.context_data.get('version_desc'):
            version_desc = self.context_data['version_desc']
            log.warn("--version-desc is deprecated, it should not be used on new zanata server")
        self.zanatacmd.create_version(project_id, version_id, version_name, version_desc)


class GlossaryPush(CommandsBase):
    def __init__(self, *args, **kargs):
        super(GlossaryPush, self).__init__(*args, **kargs)

    def run(self):
        if self.args:
            path = os.path.join(os.getcwd(), self.args[0])
            if not os.path.isfile(path):
                log.error("Can not find glossary file %s under current path" % self.args[0])
                sys.exit(1)
        else:
            log.info("Please specify the file name of glossary file")
            sys.exit(1)

        basename, extension = os.path.splitext(path)
        locale_map = self.context_data.get('locale_map')
        log.info("pushing glossary document %s to server" % self.args[0])

        if extension == '.po':
            if self.context_data.get('lang'):
                lang = self.context_data['lang'].split(',')[0]
            else:
                log.error("Please specify the language with '--lang' option")
                sys.exit(1)

            if lang in locale_map:
                lang = locale_map[lang]

            if 'sourcecomments' in self.context_data:
                sourcecomments = True
            else:
                sourcecomments = False
            self.zanatacmd.poglossary_push(path, lang, sourcecomments)
        elif extension == '.csv':
            if self.context_data.get('comment_cols'):
                comments_header = self.context_data['comment_cols'].split(',')
            else:
                log.error("Please specify the comments header, otherwise processing will be fault")
                sys.exit(1)
        self.zanatacmd.csvglossary_push(path, locale_map, comments_header)


class GlossaryDelete(CommandsBase):
    def __init__(self, *args, **kargs):
        super(GlossaryDelete, self).__init__(*args, **kargs)

    def run(self):
        lang = None
        if self.context_data.get('lang'):
            lang = self.context_data['lang'].split(',')[0]
            log.info("Delete the glossary terms in %s on the server" % lang)
        else:
            log.info("Delete all the glossary terms on the server")
        self.zanatacmd.delete_glossary(lang)


class Stats(CommandsBase):
    def __init__(self, *args, **kargs):
        super(Stats, self).__init__(*args, **kargs)

    def run(self):
        log.info("Project: %s" % self.check_essential(
            self.context_data.get('project_id'),
            "Please specify PROJECT_ID with --project-id option or using zanata.xml"
        ))
        log.info("Version: %s" % self.check_essential(
            self.context_data.get('project_version'),
            "Please specify PROJECT_VERSION with --project-version option or using zanata.xml"
        ))
        id_version = (self.context_data['project_id'], self.context_data['project_version'])
        cmd_opts = dict([(cmd, self.context_data.get(cmd, True))
                         for cmd in ('detailstats', 'wordstats', 'docid')
                         if cmd in self.context_data])
        cmd_opts['locale_map'] = self.context_data.get('locale_map')
        if self.context_data.get('lang') and isinstance(self.context_data['lang'], str):
            cmd_opts['lang'] = filter(lambda locale: locale if locale else None,
                                      self.context_data['lang'].split(','))
        self.zanatacmd.display_translation_stats(*id_version, **cmd_opts)


class PushPull(CommandsBase):
    """
    This is base class for push-pull commands
    """
    def __init__(self, *args, **kargs):
        super(PushPull, self).__init__(*args, **kargs)

        url, self.project_id, self.version_id = (
            self.context_data.get('url'), self.context_data.get('project_id'),
            self.context_data.get('project_version')
        )
        username, client_version, server_version = (
            self.context_data.get('user_name'),
            self.context_data.get('client_version'),
            self.context_data.get('server_version')
        )
        self.plural_support = self.check_plural_support(server_version)
        self.log_message(self.project_id, self.version_id, username)
        self.zanatacmd.verify_project(self.project_id, self.version_id)
        if 'copytrans' in self.context_data:
            if 'nocopytrans' in self.context_data:
                log.error("--copytrans option cannot be used with --no-copytrans. Aborting.")
                sys.exit(1)
            else:
                self.copytrans = True
        # This warning makes no sense for pull commands.
        # elif not self.command_options.has_key('nocopytrans'):
        #    log.warn("copytrans is now disabled by default")
        else:
            self.copytrans = False
        self.file_mapping_rules = self.context_data['file_mapping_rules'] \
            if 'file_mapping_rules' in self.context_data else None

    # Functions in PoPush and GenericPush get tmlfile,file list
    def get_files(self):
        deletefiles = False
        filelist = []
        tmlfolder = ""
        project_type = self.context_data.get('project_type')
        if project_type != 'podir' and project_type != 'gettext':
            log.error("The project type is not correct, please use 'podir' or 'gettext' as project type")
            sys.exit(1)

        if 'srcfile' in self.context_data:
            if project_type == 'gettext':
                tmlfolder, import_file = self.process_srcfile()
                filelist.append(import_file)
            else:
                log.warn("srcfile option is not used for podir type project, ignored")

        if tmlfolder == "":
            tmlfolder = self.process_srcdir_withsub()

        if self.args:
            try:
                full_path = self.search_file(tmlfolder, self.args[0])
                filelist.append(full_path)
            except NoSuchFileException as e:
                log.error(e.msg)
                sys.exit(1)
        else:
            # get all the pot files from the template folder
            supported_file_ext = ".pot"
            publicanutil = PublicanUtility()
            filelist = publicanutil.get_file_list(tmlfolder, supported_file_ext)

            if not filelist:
                log.error("No %s files found in directory %s." % (supported_file_ext, tmlfolder))
                sys.exit(1)
            deletefiles = True
        return project_type, deletefiles, tmlfolder, filelist

    def process_merge(self):
        merge = ""

        if 'merge' in self.context_data:
            merge = self.context_data.get('merge')
            if merge != 'auto' and merge != 'import':
                log.info("merge option %s is not recognized, assuming default value 'auto'" % merge)
                merge = 'auto'
        else:
            merge = 'auto'

        log.info("merge option set to value %s" % merge)

        return merge

    def get_lang_list(self):
        lang_list = []
        if 'lang' in self.context_data:
            lang_list = self.context_data.get('lang').split(',')
        elif 'locale_map' in self.context_data:
            lang_list = self.context_data.get('locale_map').keys()
        else:
            log.error("Please specify the language with '--lang' option or in zanata.xml")
            sys.exit(1)

        return lang_list

    def process_srcdir_withsub(self):
        tmlfolder = ""

        if 'srcdir' in self.context_data:
            tmlfolder = self.context_data.get('srcdir')
        elif 'dir' in self.context_data:
            # Keep dir option for publican/po push
            tmlfolder = self.context_data.get('dir')
        else:
            tmlfolder = os.path.abspath(os.getcwd())

        tmlfolder = os.path.expanduser(tmlfolder)

        if not os.path.isdir(tmlfolder):
            log.error("Can not find source folder, please specify the source folder with '--srcdir' or 'dir' option")
            sys.exit(1)

        return tmlfolder

    def process_srcdir(self):
        tmlfolder = ""

        if 'srcdir' in self.context_data:
            tmlfolder = self.context_data.get('srcdir')
        else:
            tmlfolder = os.path.abspath(os.getcwd())

        tmlfolder = os.path.expanduser(tmlfolder)
        return tmlfolder

    def process_srcfile(self):
        tmlfolder = ""
        file_path = ""

        if 'srcfile' in self.context_data:
            path = self.context_data.get('srcfile')
            file_path = os.path.abspath(path)
            tmlfolder = file_path[0:file_path.rfind('/')]

        return tmlfolder, file_path

    def process_transdir(self, src_folder):
        trans_folder = ""

        if 'transdir' in self.context_data:
            trans_folder = self.context_data.get('transdir')
        elif src_folder:
            trans_folder = src_folder
        else:
            trans_folder = os.getcwd()

        trans_folder = os.path.expanduser(trans_folder)
        return trans_folder

    def create_outpath(self, output_folder):
        if 'transdir' in self.context_data:
            output = self.context_data.get('transdir')
        elif output_folder:
            output = output_folder
        else:
            output = os.getcwd()

        output = os.path.expanduser(output)

        try:
            if not os.path.isdir(output):
                os.mkdir(output)
        except OSError:
            log.error("Directory %s could not be created" % output)
            sys.exit(1)

        return output

    def search_file(self, path, filename):
        for root, dirs, names in os.walk(path):
            if filename in names:
                return os.path.join(root, filename)

        raise NoSuchFileException('Error 404', 'File %s not found' % filename)

    def check_plural_support(self, server_version):
        if not server_version:
            return False

        version = str(server_version.split('-')[0])
        main_ver = version[:3]
        version_number = float(main_ver)

        if version_number >= 1.6:
            return True
        else:
            return False

    def get_importpo(self):
        importpo = False

        if 'importpo' in self.context_data:
            importpo = True
        elif 'pushtrans' in self.context_data:
            importpo = True
            log.info("please use --import-po for old publican push command")

        return importpo

    def get_pushtrans(self):
        pushtrans = False

        if 'pushtrans' in self.context_data:
            pushtrans = True
        elif 'importpo' in self.context_data:
            pushtrans = True
            log.info("--import-po option is deprecated, please use '--push-type both'  instead")

        return pushtrans

    def get_importparam(self, project_type, folder):
        import_param = {'transdir': '', 'merge': 'auto', 'lang_list': {}, 'locale_map': {}, 'project_type': 'gettext'}

        import_param['transdir'] = self.process_transdir(folder)
        log.info("Reading locale folders from %s" % import_param['transdir'])
        import_param['merge'] = self.process_merge()
        import_param['lang_list'] = self.get_lang_list()
        import_param['locale_map'] = self.context_data.get('locale_map')
        import_param['project_type'] = project_type
        return import_param

    def log_message(self, project_id, project_version, username):
        log.info("Project: %s" % self.check_essential(
            project_id, "Please specify PROJECT_ID with --project-id option or using zanata.xml"
        ))
        log.info("Version: %s" % self.check_essential(
            project_version, "Please specify PROJECT_VERSION with --project-version option or using zanata.xml"
        ))
        log.info("Project Type: %s" % self.check_essential(
            self.context_data.get('project_type'),
            "Please specify PROJECT_TYPE with --project-type option or using zanata.xml"
        ))
        log.info("Username: %s" % (username or 'Anonymous'))
        log.info("Source language: en-US")
