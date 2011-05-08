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

__all__ = (
            "HelpInfo",
        )

import zanata 

class HelpInfo:    
    def print_usage(self):
        print ('\nClient for talking to a Zanata/Flies Server\n\n'
               'Usage: zanata <command> [COMMANDOPTION]...\n\n'
               'list of commands:\n'
               ' list                List all available projects\n'
               ' project info        Show information about a project\n'
               ' version info        Show information about a version\n'
               ' project create      Create a project\n'
               ' version create      Create a version within a project\n'
               ' publican pull       Pull the content of publican file\n'
               ' publican push       Push the content of publican file to Zanata/Flies server\n'
               ' po pull       Pull the content of software project file\n'
               ' po push       Push the content of software project file to Zanata/Flies server\n'
               "Use 'zanata help' for the full list of commands\n"
               "Use 'zanata help COMMAND' for usage of commands\n")

    def print_help_info(self, args):
        """
        Output the general help information or the help information for each command
        @param args: the name of command and sub command
        """
        if not args:
            print ('Client for talking to a Zanata/Flies Server:\n\n'
                  'Usage: zanata <command> [COMMANDOPTION]...\n\n'
                  'list of commands:\n'
                  ' help                Display this help and exit\n'
                  ' list                List all available projects\n'
                  ' project info        Show information about a project\n'
                  ' version info        Show information about a version\n'
                  ' project create      Create a project\n'
                  ' version create      Create a version within a project\n'
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican file to Zanata/Flies server\n'
                  ' po pull       Pull the content of software project file\n'
                  ' po push       Push the content of software project file to Zanata/Flies server\n'
                  "Use 'zanata help COMMAND' for usage of commands\n")
        else:
            command = args[0]
            sub = args[1:]
            if zanata.sub_command.has_key(command):
                if zanata.sub_command[command]:
                    if sub:
                        if sub[0] in zanata.sub_command[command]:
                            command = command+'_'+sub[0]
                        else:
                            self.log.error("Unknown command")
                            sys.exit(1)
            else:
                self.log.error("Unknown command")
                sys.exit(1)

            self._command_help(command)

    def _command_help(self, command):      
        if command == 'list':
            self._list_help()
        elif command == 'project':
            print ("Command:'zanata project info'\n"
                   "        'zanata project create'")
        elif command == 'project_info':
            self._projec_info_help()
        elif command == 'project_create':
            self._project_create_help()
        elif command == 'version':
            print ("Command:'zanata version info'\n"
                   "        'zanata version create'")
        elif command == 'version_info':
            self._iteration_info_help()
        elif command == 'version_create':
            self._iteration_create_help()
        elif command == 'publican':
            print ("Command:'zanata publican push'\n"
                   "        'zanata publican pull'")
        elif command == 'publican_push':
            self._publican_push_help()
        elif command == 'publican_pull':
            self._publican_pull_help()
        elif command == 'po':
            print ("Command:'zanata po push'\n"
                   "        'zanata po pull'")
        elif command == 'po_push':
            self._pofile_push_help()
        elif command == 'po_pull':
            self._pofile_pull_help()

    def _list_help(self):
       	print ('zanata list [OPTIONS]\n'
               'list all available projects\n'
               'options:\n'
               ' --url address of the Zanata/Flies server, eg http://example.com/zanata')
    
    def _projec_info_help(self):
	    print ('zanata project info [OPTIONS]\n'
               'show infomation about a project\n'
               'options:\n'
               '--project-id: project id')

    def _project_create_help(self):
        print ('zanata project create [PROJECT_ID] [OPTIONS]\n'
               'create a project\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-name: project name\n'
               '--project-desc: project description')

    def _iteration_info_help(self):
	    print ('zanata version info [OPTIONS]\n'
               'show infomation about a version\n'
               'options:\n'
               '--project-id: project id\n'
               '--project-version: id of project version')

    def _iteration_create_help(self):
        print ('zanata version create [VERSION_ID] [OPTIONS]\n'
               'create a version\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--version-name: version name\n'
               '--version-desc: version description')

    def _publican_push_help(self):
        print ('zanata publican push [OPTIONS] {documents}\n'
               'push publican content to server for translation\n'
               'options:\n'
               '-f: force to remove content on server side\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--project-version: id of the version\n'
               '--dir: the full path of the folder that contain pot folder and locale folders\n'
               '--srcdir: the full path of the pot folder\n'
               '--transdir: the full path of the folder that contain locale folders\n'
               '--import-po: push local translations to server\n'
               '--merge: override merge algorithm: auto (default) or import\n'
               '--no-copytrans: prevent server from copying translations from other versions')

    def _publican_pull_help(self):
        print ('zanata publican pull [OPTIONS] {documents} {lang}\n'
               'retrieve translated publican content files from server\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--project-version: id of the version\n'
               '--dir: output folder\n'
               '--dstdir: output folder for po files\n'
               '--lang: language list')
    
    def _pofile_push_help(self):
        print ('zanata po push [OPTIONS] {documents}\n'
               'push software project source and translation files to server\n'
               'options:\n'
               '-f: force to remove content on server side\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--project-version: id of the version\n'
               '--srcdir: the full path of the pot folder\n'
               '--srcfile: the full path of the source file\n'
               '--transdir: the full path of the folder that contain locale folders\n'
               '--import-po: push local translations to server\n'
               '--merge: override merge algorithm: auto (default) or import\n'
               '--no-copytrans: prevent server from copying translations from other versions')

    def _pofile_pull_help(self):
        print ('zanata po pull [OPTIONS] {documents} {lang}\n'
               'retrieve software project translation files from server\n'
               'options:\n'
               '--username: user name\n'
               '--apikey: api key of user\n'
               '--project-id: id of the project\n'
               '--project-version: id of the version\n'
               '--dstdir: output folder for po files\n'
               '--lang: language list')
