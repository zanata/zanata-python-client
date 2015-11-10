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

from zanatalib.logger import Logger
from pushcmd import Push

log = Logger()


class GenericPull(Push):
    def __init__(self, *args, **kargs):
        super(GenericPull, self).__init__(*args, **kargs)

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

        output = os.path.expanduser(output)

        if not os.path.isdir(output):
            os.mkdir(output)

        return output

    def run(self):
        dir_option = False
        skeletons = True
        filelist = []
        output_folder = None

        lang_list = self.get_lang_list(self.command_options, self.project_config)

        # list the files in project
        try:
            filelist = self.zanatacmd.get_file_list(self.project_id, self.version_id)
        except Exception, e:
            log.error(str(e))
            sys.exit(1)

        if self.project_config.has_key('locale_map'):
            locale_map = self.project_config['locale_map']
        else:
            locale_map = None

        if self.project_type:
            command_type = self.project_type
            dir_option = True
        elif self.command_options.has_key('project_type'):
            command_type = self.command_options['project_type'][0]['value']
        elif self.project_config['project_type']:
            command_type = self.project_config['project_type']
        else:
            log.error("The project type is unknown")
            sys.exit(1)

        if dir_option:
            # Keep dir option for publican/po pull
            if self.command_options.has_key('dir'):
                output_folder = self.command_options['dir'][0]['value']

            if self.command_options.has_key('dstdir'):
                output_folder = self.command_options['dstdir'][0]['value']
        else:
            # Disable dir option for generic pull command
            if self.command_options.has_key('dir'):
                log.warn("dir option is disabled in pull command, please use --transdir, or specify value in zanata.xml")

            if self.command_options.has_key('dstdir'):
                log.warn("dstdir option is changed to transdir option for generic pull command")
                output_folder = self.command_options['dstdir'][0]['value']

        if self.command_options.has_key('noskeletons'):
            skeletons = False

        outpath = self.create_outpath(self.command_options, output_folder)

        self.zanatacmd.pull_command(locale_map, self.project_id, self.version_id, filelist, lang_list, outpath, command_type, skeletons)
