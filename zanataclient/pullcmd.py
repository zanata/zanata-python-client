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

from .zanatalib.logger import Logger
from .pushcmd import PushPull

log = Logger()


class GenericPull(PushPull):
    def __init__(self, *args, **kargs):
        super(GenericPull, self).__init__(*args, **kargs)

    def run(self):
        skeletons = True
        filelist = []
        output_folder = None

        lang_list = self.get_lang_list()

        # list the files in project
        try:
            filelist = self.zanatacmd.get_file_list(self.project_id, self.version_id)
        except Exception as e:
            log.error(str(e))
            sys.exit(1)

        locale_map = self.context_data.get('locale_map')
        command_type = self.context_data.get('project_type')

        if self.context_data.get('publican_po'):
            # Keep dir option for publican/po pull
            if 'dir' in self.context_data:
                output_folder = self.context_data.get('dir')

            if 'dstdir' in self.context_data:
                output_folder = self.context_data.get('dstdir')
        else:
            # Disable dir option for generic pull command
            if 'dir' in self.context_data:
                log.warn("dir option is disabled in pull command, please use --transdir, or specify value in zanata.xml")

            if 'dstdir' in self.context_data:
                log.warn("dstdir option is changed to transdir option for generic pull command")
                output_folder = self.context_data.get('dstdir')

        if 'noskeletons' in self.context_data:
            skeletons = False

        outpath = self.create_outpath(output_folder)
        filedict = self.zanatacmd.get_project_translation_stats(
            self.project_id, self.version_id, self.context_data['mindocpercent'], lang_list, locale_map
        ) if self.context_data.get('mindocpercent') else dict((file, lang_list) for file in filelist)
        self.zanatacmd.pull_command(locale_map, self.project_id, self.version_id, filedict, outpath, command_type, skeletons)
