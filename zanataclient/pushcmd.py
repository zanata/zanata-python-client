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

from .cmdbase import PushPull
from .zanatalib.logger import Logger

log = Logger()


class GenericPush(PushPull):

    def __init__(self, *args, **kargs):
        super(GenericPush, self).__init__(*args, **kargs)

    def run(self):
        pushtrans = None
        push_trans_only = False
        force = False
        project_type, deletefiles, tmlfolder, filelist = self.get_files()
        # Disable dir option for generic push command
        if 'dir' in self.context_data:
            log.warn("dir option is disabled in push command, please use --srcdir and --transdir, or specify value in zanata.xml")

        if 'pushtrans' in self.context_data:
            log.warn("--push-trans is deprecated, please use '--push-type both' instead")
            pushtrans = True

        if 'pushtype' in self.context_data:
            push_type = self.context_data.get('pushtype')
            if push_type == "source":
                pushtrans = False
            elif push_type == "target":
                push_trans_only = True
            elif push_type == "both":
                pushtrans = True

        if 'pushtransonly' in self.context_data:
            push_trans_only = True

        if push_trans_only:
            transfolder = self.process_transdir('')
            merge = self.process_merge()
            lang_list = self.get_lang_list()
            locale_map = self.context_data.get('locale_map')
            self.zanatacmd.push_trans_command(transfolder, self.project_id, self.version_id, lang_list, locale_map, project_type, merge)
            sys.exit(0)

        if not os.path.isdir(tmlfolder):
            log.error("Can not find source folder, please specify the source folder with '--srcdir' or using zanata.xml")
            sys.exit(1)

        if 'force' in self.context_data:
            force = True

        if project_type == 'podir':
            log.info("POT directory (originals):%s" % tmlfolder)
            folder = None
        elif project_type == 'gettext':
            log.info("PO directory (originals):%s" % tmlfolder)
            folder = tmlfolder

        if pushtrans is None:
            pushtrans = self.get_pushtrans()

        if deletefiles:
            self.zanatacmd.del_server_content(tmlfolder, self.project_id, self.version_id, filelist, force, project_type)

        if pushtrans:
            log.info("Send local translation: True")
            import_param = self.get_importparam(project_type, folder)
            self.zanatacmd.push_command(filelist, tmlfolder, self.project_id, self.version_id, self.copytrans, self.plural_support, import_param)
        else:
            log.info("Send local translation: False")
            self.zanatacmd.push_command(filelist, tmlfolder, self.project_id, self.version_id, self.copytrans, self.plural_support)


class PublicanPush(PushPull):
    def __init__(self, *args, **kargs):
        super(PublicanPush, self).__init__(*args, **kargs)

    def run(self):
        importpo = False
        force = False
        project_type, deletefiles, tmlfolder, filelist = self.get_files()

        log.info("Reuse previous translation on server:%s" % self.copytrans)

        if 'force' in self.context_data:
            force = True

        log.info("POT directory (originals):%s" % tmlfolder)

        importpo = self.get_importpo()

        if deletefiles:
            self.zanatacmd.del_server_content(tmlfolder, self.project_id, self.version_id, filelist, force, "podir")

        if importpo:
            import_param = self.get_importparam("podir", tmlfolder)
            self.zanatacmd.push_command(filelist, tmlfolder, self.project_id, self.version_id, self.copytrans, self.plural_support, import_param)
        else:
            log.info("Importing source documents only")
            self.zanatacmd.push_command(filelist, tmlfolder, self.project_id, self.version_id, self.copytrans, self.plural_support)


class PoPush(PushPull):
    def __init__(self, *args, **kargs):
        super(PoPush, self).__init__(*args, **kargs)

    def run(self):
        importpo = False
        force = False
        project_type, deletefiles, tmlfolder, filelist = self.get_files()
        log.info("Reuse previous translation on server: %s" % self.copytrans)
        importpo = self.get_importpo()

        if importpo:
            log.info("Importing translation")
            import_param = self.get_importparam("gettext", tmlfolder)
        else:
            log.info("Importing source documents only")

        if 'force' in self.context_data:
            force = True
        if deletefiles is True:
            self.zanatacmd.del_server_content(tmlfolder, self.project_id, self.version_id, filelist, force, "gettext")

        if importpo:
            self.zanatacmd.push_command(filelist, tmlfolder, self.project_id, self.version_id, self.copytrans, self.plural_support, import_param)
        else:
            self.zanatacmd.push_command(filelist, tmlfolder, self.project_id, self.version_id, self.copytrans, self.plural_support)
