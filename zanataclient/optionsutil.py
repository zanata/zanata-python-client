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

__all__ = (
            "OptionsUtil",
          )

import os
import sys

from zanatalib.logger import Logger
from parseconfig import ZanataConfig

class OptionsUtil:
    def __init__(self, options):
        self.command_options = options
        self.project_config = {}
        self.log = Logger()
        self.config = ZanataConfig()

    def apply_configfiles(self):
        url = self.apply_project_config()
        username, apikey = self.apply_user_config(url)
        
        #The value in commandline options will overwrite the value in user-config file
        if self.command_options.has_key('user_name'):
            username = self.command_options['user_name'][0]['value']

        if self.command_options.has_key('key'):
            apikey = self.command_options['key'][0]['value']

        self.log.info("zanata server: %s" % url)

        return url, username, apikey

    def apply_project_config(self):
        url = ""
        #Read the project configuration file using --project-config option
        config_file = [os.path.join(os.getcwd(), filename) for filename\
                    in ['zanata.xml', 'flies.xml']]

        if self.command_options.has_key('project_config'):
            config_file.append(self.command_options['project_config'][0]['value'])

        for path in config_file:

            if os.path.exists(path):
                self.log.info("Loading zanata project config from: %s" % path)
                self.project_config = self.config.read_project_config(path)
                break

        if not self.project_config:
            self.log.info("Can not find zanata.xml, please specify the path of zanata.xml")
            
        #process the url of server
        if self.project_config.has_key('project_url'):
            url = self.project_config['project_url']

        #The value in options will override the value in project-config file
        if self.command_options.has_key('url'):
            self.log.info("Overriding url of server with command line option")
            url = self.command_options['url'][0]['value']

        if not url or url.isspace():
            self.log.error("Please specify valid server url in zanata.xml or with '--url' option")
            sys.exit(1)

        url = self.trim_url(url)
        
        return url

    def trim_url(self, url):
        if ' ' in url or '\n' in url:
            self.log.info("Warning, the url which contains '\\n' or whitespace is not valid, please check zanata.xml")
        url = url.strip()

        if url[-1] == "/":
            url = url[:-1]

        return url

    def get_localemap(self):
        if self.project_config and self.project_config.has_key('locale_map'):
            locale_map = self.project_config['locale_map']

        return locale_map

    def apply_user_config(self, url):
        user_name = ""
        apikey = ""
        #Try to read user-config file
        user_config = [os.path.join(os.path.expanduser("~") + '/.config', filename) for filename in ['zanata.ini', 'flies.ini']]

        if self.command_options.has_key('user_config'):
            user_config.append(self.command_options['user_config'][0]['value'])

        for path in user_config:
            if os.path.exists(path):
                self.log.info("Loading zanata user config from: %s" % path)

            #Read the user-config file
            self.config.set_userconfig(path)

            try:
                server = self.config.get_server(url)
                if server:
                    user_name = self.config.get_config_value("username", "servers", server)
                    apikey = self.config.get_config_value("key", "servers", server)
            except Exception, e:
                self.log.info("Processing user-config file:%s" % str(e))
                break
            
            break

                
        if not (user_name, apikey):
            self.log.info("Can not find user-config file in home folder, current path or path in 'user-config' option")

        return (user_name, apikey)        
