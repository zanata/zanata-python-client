# 
# Flies Python Client
#
# Copyright (c) 2010 Jian Ni <jni@redhat.com>
# Copyright (c) 2010 Red Hat, Inc.
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
        "FliesConfig",
    )

import ConfigParser
import os.path
from xml.dom import minidom 

project_config = {'project_url':'', 'project_id':'', 'project_version':'', 'locale_map':{}}

class FliesConfig:
     def set_userconfig(self, path):
        userconfig = path
        self.configparser = ConfigParser.ConfigParser()
        self._config = self.configparser.read([userconfig, os.path.expanduser(userconfig)])
     
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
            except ConfigParser.NoOptionError, NoSectionError:
                return None
        else:
            return None       
             
     def get_value(self, name, section, server):
        if self._config:
            try:
                value = self.configparser.get('servers', server+'.'+name)
                return value
            except ConfigParser.NoOptionError, NoSectionError:
                return None
        else:
            return None
     
     def get_config_value(self, name, server):
         return self.get_value(name, 'defaults', server) 

     def read_project_config(self, filename):
        project_config={'project_url':'', 'project_id':'', 'project_version':'', 'locale_map':{}}
        xmldoc = minidom.parse(filename)

        #Read the project url
        node = xmldoc.getElementsByTagName("url")[0]
        rc = ""

        for node in node.childNodes:
            if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
                rc = rc + node.data
        project_config['project_url'] = rc

        #Read the project id
        node = xmldoc.getElementsByTagName("project")[0]
        rc = ""

        for node in node.childNodes:
            if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
                rc = rc + node.data
        project_config['project_id'] = rc
        
        #Read the project-version
        node = xmldoc.getElementsByTagName("project-version")[0]
        rc = ""
        
        for node in node.childNodes:
            if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
                rc = rc + node.data
        project_config['project_version'] = rc

        #Read the locale map
        locales = xmldoc.getElementsByTagName("locales")[0]
        
        
        localelist = locales.getElementsByTagName("locale")
        for locale in localelist:
            for node in locale.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    if locale.getAttribute("map-from"):
                        map = {locale.getAttribute("map-from"):node.data}
                        project_config['locale_map'].update(map)
                    else:
                        map = {node.data:node.data}
                        project_config['locale_map'].update(map)
        
        return project_config
    


