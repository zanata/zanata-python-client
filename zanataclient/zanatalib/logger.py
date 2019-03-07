# vim:set et sts=4 sw=4:
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
__all__ = (
    "Logger",
)


class TextColour:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Logger:
    def __init__(self):
        self.enable_infoprefix = True
        self.enable_warnprefix = True
        self.enable_errprefix = True
        self.enable_successprefix = True
        self.success_prefix = '[SUCCESS] '
        self.warn_prefix = '[WARN] '
        self.error_prefix = '[ERROR] '
        self.info_prefix = '[INFO] '

    def success(self, message):
        if self.enable_successprefix:
            print(TextColour.OKGREEN + self.success_prefix + message + TextColour.ENDC)
        else:
            print(message)

    def info(self, message):
        if self.enable_infoprefix:
            print(TextColour.OKBLUE + self.info_prefix + message + TextColour.ENDC)
        else:
            print(message)

    def warn(self, message):
        if self.enable_warnprefix:
            print(TextColour.WARNING + self.warn_prefix + message + TextColour.ENDC)
        else:
            print(message)

    def error(self, message):
        if self.enable_errprefix:
            print(TextColour.FAIL + self.error_prefix + message + TextColour.ENDC)
        else:
            print(message)
