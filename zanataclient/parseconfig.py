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
    "ZanataConfig",
)

import ConfigParser
import os.path
from zanatalib.logger import Logger
from xml.dom import minidom


project_config = {'project_url': '', 'project_id': '', 'project_version': '', 'project_type': '', 'locale_map': {}}


class ZanataConfig:
    def __init__(self):
        self.configparser = ""
        self._config = ""

    def set_userconfig(self, path):
        self.configparser = ConfigParser.ConfigParser()
        self._config = self.configparser.read(['zanata.ini', path])

    def get_server(self, url):
        if self._config:
            try:
                item_list = self.configparser.items('servers')
                server = ""
                for item in item_list:
                    if item[1][-1] == "/":
                        address = item[1][:-1]
                    else:
                        address = item[1]

                    if url == address:
                        server = item[0][:-4]
                return server
            except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
                raise
        else:
            return None

    def get_config_value(self, name, section, server):
        if self._config:
            try:
                value = self.configparser.get(section, server + '.' + name)
                return value
            except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
                raise
        else:
            return None

    def read_project_config(self, filename):
        log = Logger()

        if os.path.getsize(filename) == 0:
            log.info('The project config file is empty, need command line options')
            return project_config

        xmldoc = minidom.parse(filename)

        # Read the project url
        if xmldoc.getElementsByTagName("url"):
            node = xmldoc.getElementsByTagName("url")[0]
            project_config['project_url'] = getCombinedTextChildren(node)

        # Read the project id
        if xmldoc.getElementsByTagName("project"):
            node = xmldoc.getElementsByTagName("project")[0]
            project_config['project_id'] = getCombinedTextChildren(node)

        # Read the project-version
        if xmldoc.getElementsByTagName("project-version"):
            node = xmldoc.getElementsByTagName("project-version")[0]
            project_config['project_version'] = getCombinedTextChildren(node)

        # Read the project-type
        if xmldoc.getElementsByTagName("project-type"):
            node = xmldoc.getElementsByTagName("project-type")[0]
            project_config['project_type'] = getCombinedTextChildren(node)

        # Read the locale map
        if xmldoc.getElementsByTagName("locales"):
            locales = xmldoc.getElementsByTagName("locales")[0]
            localelist = locales.getElementsByTagName("locale")

            for locale in localelist:
                for node in locale.childNodes:
                    if node.nodeType == node.TEXT_NODE:
                        if locale.getAttribute("map-from"):
                            locale_map = {str(locale.getAttribute("map-from")): str(node.data)}
                        else:
                            locale_map = {str(node.data): str(node.data)}
                        project_config['locale_map'].update(locale_map)

        return project_config


def getCombinedTextChildren(node):
    """Combine all TEXT_NODE and CDATA_SECTION_NODE children"""

    rc = ""
    for node in node.childNodes:
        if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
            rc = rc + node.data
    return rc
