# vim: set et sts=4 sw=4:
#
# Zanata Python Client
#
# Copyright (c) 2016 Sundeep Anand <suanand@redhat.com>
# Copyright (c) 2016 Red Hat, Inc.
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

import fnmatch
import os
import sys
from datetime import datetime

from .cmdbase import CommandsBase, CommandsInit
from .context import ContextBase
from .parseconfig import ZanataConfig
from .zanatalib.logger import Logger, TextColour
from .zanatalib.projectutils import ToolBox


try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


log = Logger()


class ZanataInit(CommandsInit, ContextBase):
    """
    Implementation of command: zanata init
    """
    def __init__(self, *args, **kargs):
        super(ZanataInit, self).__init__(*args, **kargs)
        self.config = ZanataConfig()
        self.mode = 'default'
        self.remote_config, self.local_config, \
            self.command_dict = [{} for i in range(3)]
        self.command_dict.update(**self.context_data)
        self.zanata_cmd = None

    def run(self):
        init_stages = self.get_init_stages()
        [method() for method in init_stages]

    def get_init_stages(self):
        init_mode_dict = {
            'default': [self.update_server_url, self._update_url,
                        self._update_user_config, self._update_http_headers,
                        self._update_client_version, self.check_config_exists,
                        self.set_zanata_command, self.project_options,
                        self.version_options, self._update_project_type,
                        self.post_project_version, self.source_target_dirs,
                        self.dump_project_config, self.whats_next]
        }
        return init_mode_dict[self.mode]

    def ptxt(self, colour, msg):
        text = {
            'info_blue': TextColour.OKBLUE + msg + TextColour.ENDC,
            'info_green': TextColour.OKGREEN + "[>] " + msg + TextColour.ENDC,
            'input': TextColour.WARNING + "[?] " + msg + TextColour.ENDC,
            'alert': TextColour.FAIL + "[!] " + msg + TextColour.ENDC,
            'header': TextColour.HEADER + msg + TextColour.ENDC
        }
        print(text[colour])

    def print_options(self, header, options, message, filter_mode=None):
        counter = 0
        choice = None
        counter_dict = {}
        self.ptxt('header', header)
        for option in options:
            if option:
                counter += 1
                counter_dict.update({str(counter): option})
                self.ptxt('info_blue', "\t%s) %s" % (str(counter), option))
        choice = input(message)
        while choice not in counter_dict:
            if filter_mode:
                filtered_options = filter(
                    lambda option:
                    option if option.find(choice) != -1 else None, options
                )
                return self.print_options(header, filtered_options, message, True)
            else:
                self.ptxt('alert', "Expecting %s but got: %s" % (str(counter_dict.keys()), choice))
                choice = input(message)
        return counter_dict[choice]

    def print_yes_no(self, message):
        yes_no = input(message)
        while yes_no not in ('y', 'n', 'Y', 'N'):
            yes_no = input(message)
        return yes_no in ('y', 'Y')

    def update_server_url(self):
        self.check_essential(
            self.context_data.get('servers'),
            'Can not find or parse user-config file: zanata.ini',
        )
        url = self.print_options(
            "\tFound servers in zanata.ini:",
            self.context_data.get('servers'),
            "[?] Which Zanata server do you want to use? "
        )
        self.local_config.update({'url': url})

    def check_config_exists(self):
        user_config_path = os.path.join(os.path.curdir + '/zanata.xml')
        if os.path.exists(user_config_path):
            self.ptxt('alert', 'Project config (zanata.xml) already exists. If you continue it will be backed up.')
            if self.print_yes_no('[?] Do you want to continue (y/n)? '):
                backup_file = os.path.join(user_config_path + '.' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
                os.rename(user_config_path, backup_file)
                self.local_config.update({'backup_file': backup_file})
                log.info('Old project config has been renamed to %s' % backup_file)
            else:
                sys.exit(1)

    def set_zanata_command(self):
        self.zanata_cmd = CommandsBase(None, self.local_config).generate_zanatacmd(
            self.local_config.get('url'), self.local_config.get('http_headers')
        )

    def _choose_from_existing_projects(self):
        projects_dict = dict((project.id, project.name) for project in self.zanata_cmd.get_projects())
        project_choice = self.print_options(
            "\n\t======= Available project(s): ID (name) ======",
            ['%s %s%s%s' % (id, '(', name, ')') for id, name in projects_dict.items()],
            "\n[?] Please select your project (index number) or enter part of the project ID/name to filter: ",
            True
        )
        project_id = project_choice.split()[0]
        self.local_config.update({'project_id': project_id})
        self.local_config.update({'project_name': projects_dict.get(project_id)})
        log.info('Now working with project %s.' % project_id)

    def _create_new_project(self):
        print("Refer to http://zanata.org/help/projects/create-project/ for help.")
        print("Project ID must start and end with letter or number, and contain only "
              "letters, numbers, underscores and hyphens.")
        input_project_id = input("[?] What ID should your project have? ")
        input_project_name = input("[?] What display name should your project have? ")
        input_project_desc = input("[?] What discription should your project have? ")
        input_project_type = input("[?] What is your project type (gettext, podir)? ")
        project_type = input_project_type if input_project_type in ('gettext', 'podir') \
            else 'IterationProject'
        try:
            log.info("Creating project on the server...")
            if not self.zanata_cmd.create_project(input_project_id, input_project_name,
                                                  input_project_desc, project_type):
                raise Exception
        except Exception as e:
            if self.print_yes_no("[?] Do you want to try again (y/n)? "):
                return self._create_new_project()
            else:
                sys.exit(1)
        else:
            self.local_config.update({'project_id': input_project_id})
            self.local_config.update({'project_name': input_project_name})
            self.local_config.update({'project_type': project_type})
            log.info('Now working with project %s.' % input_project_id)

    def project_options(self):
        proj_menu_opts = ['Select an existing project', 'Create a new project']
        proj_menu_choice = self.print_options('Do you want to...',
                                              proj_menu_opts, '(1/2)? ')
        if proj_menu_choice == proj_menu_opts[0]:
            self._choose_from_existing_projects()
        elif proj_menu_choice == proj_menu_opts[1]:
            self._create_new_project()

    def _choose_from_existing_versions(self):
        versions = self.zanata_cmd.get_project_versions(
            self.local_config.get('project_id')
        )
        if not versions:
            log.warn("No versions found. Please create one.")
            self._create_new_version()
            return
        version_choice = self.print_options(
            "\n\t======= Available versions(s) for project %s ======" % self.local_config.get('project_id'),
            versions,
            "\n[?] Please select your version (index number) or enter part of the version ID to filter: ",
            True
        )
        self.local_config.update({'project_version': version_choice})
        log.info('Now working with version: %s' % version_choice)

    def _create_new_version(self):
        input_version_id = input("[?] What ID should your version have: ")
        try:
            log.info("Creating version on the server...")
            if not self.zanata_cmd.create_version(self.local_config.get('project_id'),
                                                  input_version_id):
                raise Exception
        except Exception as e:
            if self.print_yes_no("[?] Do you want to try again (y/n)? "):
                return self._create_new_version()
            else:
                sys.exit(1)
        else:
            self.local_config.update({'project_version': input_version_id})
            log.info('Now working with version: %s' % input_version_id)

    def version_options(self):
        version_menu_opts = ['Select an existing version', 'Create a new version']
        version_menu_choice = self.print_options('Do you want to...',
                                                 version_menu_opts, '(1/2)? ')
        if version_menu_choice == version_menu_opts[0]:
            self._choose_from_existing_versions()
        elif version_menu_choice == version_menu_opts[1]:
            self._create_new_version()

    def post_project_version(self):
        if not self.local_config.get('project_type') and self.remote_config.get('project_type'):
            self.local_config['project_type'] = self.remote_config['project_type']

        if not self.local_config.get('project_type'):
            self.local_config['project_type'] = self.print_options(
                "\tSelect Project Type...", ('gettext', 'podir'),
                "[?] What is your project type (gettext, podir)? ",
            )
        self.ptxt('alert', "If you want to customize your project's translatable language list, "
                           "do so now on the following web page. Continue once it is done.")
        print("\t-- Go to your project-version homepage to view details and change advanced options: "
              "https://translate.zanata.org/zanata/iteration/view/%s/%s" % (self.local_config.get('project_id'),
                                                                            self.local_config.get('project_version')))
        self.ptxt('info_green', "Now working with Project: '%s' on Version: '%s' of Type: '%s'." % (
            self.local_config.get('project_id'),
            self.local_config.get('project_version'),
            self.local_config.get('project_type')
        )) if self.print_yes_no("[?] Do you want to continue (y/n)? ") else sys.exit(1)

    def print_trans_matches(self, match, locale, transdir):
        if self.local_config.get('project_type') == 'gettext':
            elements = match.split('/')
            elements[0] = transdir
            elements[len(elements) - 1] = locale + '.po'
            self.ptxt('info_blue', "\t  " + '/'.join(elements))
        elif self.local_config.get('project_type') == 'podir':
            elements = match.split('/')
            elements[0] = transdir
            elements.insert(len(elements) - 1, locale)
            self.ptxt('info_blue', "\t  " + '/'.join(elements).replace('pot', 'po'))

    def print_dir_contents(self, directory, mode, transdir):
        matches = []
        ext = '.pot'
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*%s' % ext):
                matches.append(os.path.join(root, filename))
        if len(matches) > 0:
            locale = 'en-US'
            if mode == 'source':
                self.ptxt('header', "\n\tFound %s documents: " % mode)
            else:
                self.ptxt('header', '\n\tZanata will put translation files as '
                                    'below (e.g. for locale %s): ' % locale)
            for match in matches:
                if mode == 'source':
                    self.ptxt('info_blue', "\t\t%s" % match.rstrip(ext))
                else:
                    self.print_trans_matches(match, locale, transdir)

    def input_dirs(self, message, mode):
        input_dir = input(message)
        while not (input_dir and os.path.isdir(os.path.curdir + '/' + input_dir)):
            self.ptxt('alert', "Directory %s does not exist! Please re-enter." % input_dir) if input_dir \
                else self.ptxt('alert', "Can not have blank answer. Please try again.")
            input_dir = input(message)
        if mode == 'target' and self.local_config.get('srcdir'):
            list_dir = self.local_config['srcdir']
        else:
            list_dir = input_dir
        transdir = input_dir
        self.print_dir_contents(list_dir, mode, transdir)
        if not self.print_yes_no("[?] Continue with %s directory settings (y/n)? " % mode):
            if mode == 'source':
                print("\tThere are more advanced options available which can only be given from commandline. "
                      "See help for detail.")
                print("\t - Add the default excludes (.svn, .git, etc) to the excludes list (default: true)")
                print("\t - Consider case of filenames in includes and excludes options. (default: true)")
                print("\t - Exclude filenames which match project configured locales (other than the source locale). "
                      "For instance, if project includes de and fr, then the files messages_de.properties and "
                      "messages_fr.properties will not be treated as source files. "
                      "NB: This parameter will be ignored for some project types which use different file naming "
                      "conventions (eg podir, gettext). (default: true)")
            return self.input_dirs(message, mode)
        return input_dir

    def source_target_dirs(self):
        srcdir = self.input_dirs(
            "[?] What is your base directory for source files (eg '.', 'pot', 'src/main/resources')? ",
            "source"
        )
        self.local_config.update({'srcdir': srcdir})
        log.info('Source directory selected: %s' % srcdir)
        transdir = self.input_dirs(
            "[?] What is your base directory for translated files (eg '.', 'po', 'src/main/resources')? ",
            "target"
        )
        self.local_config.update({'transdir': transdir})
        log.info('Translation directory selected: %s' % transdir)

    def dump_project_config(self):
        project_config_dict = OrderedDict()
        project_config_dict['url'] = {'text': self.local_config.get('url')}
        project_config_dict['project'] = {'text': self.local_config.get('project_id')}
        project_config_dict['project-version'] = {'text': self.local_config.get('project_version')}
        project_config_dict['project-type'] = {'text': self.local_config.get('project_type')}
        project_config_dict['src-dir'] = {'text': self.local_config.get('srcdir')}
        project_config_dict['trans-dir'] = {'text': self.local_config.get('transdir')}
        xmldoc = ToolBox.dict2xml('config', project_config_dict)
        try:
            with open('zanata.xml', 'w') as project_config_file:
                project_config_file.write(xmldoc.decode("utf-8"))
        except IOError:
            log.error("Something went wrong. Try Again.")
        else:
            self.ptxt('info_green', "Project config created at: zanata.xml")

    def whats_next(self):
        print("\tWhat can I do next?")
        if self.local_config.get('backup_file'):
            print("\t- Compare the new config to the old one [%s] and see if any customization can be reused. "
                  "i.e. rules or command hooks" % self.local_config['backup_file'])
        print("\t- Go to your project-version homepage to view details and change advanced options: "
              "https://translate.zanata.org/zanata/iteration/view/%s/%s" % (self.local_config.get('project_id'),
                                                                            self.local_config.get('project_version')))
        print("\t- To upload source files, run: zanata push")
        print("\t- To upload source and translation files, run: zanata push --push-type both")
        print("\t- To upload translation files, run: zanata push --push-type trans")
        print("\t- View command-line help by running: zanata help")
        print("\t- Browse online help at http://zanata.org/help")
