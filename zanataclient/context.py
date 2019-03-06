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

__all__ = (
    "ProjectContext",
)

import functools
import os
import re
import sys

from .parseconfig import ZanataConfig
from .zanatalib.error import (
    UnAvaliableResourceException,
    UnavailableServiceError,
)
from .zanatalib.logger import Logger
from .zanatalib.projectservice import IterationService, LocaleService
from .zanatalib.versionservice import VersionService


log = Logger()

project_config_file_tuple = ('zanata.xml', 'flies.xml')
user_config_file_tuple = ('zanata.ini', 'flies.ini')
client_version_file = 'VERSION-FILE'


class ContextBase(object):
    """
    Base class to build context_data dict for the project.
    """
    def __init__(self, command_options, *args, **kwargs):
        self.command_options = command_options
        self.mode = args[0] if len(args) > 0 and args[0] else 'default'
        self.log = Logger()
        self.config = ZanataConfig()

        self.remote_config, self.local_config, \
            self.command_dict = [{} for i in range(3)]

        for option_set in self.command_options:
            self.command_dict.update(
                {option_set: self.command_options[option_set][0]['value']}
            )

    def _update_project_config(self):
        """
        Reads project configuration file, and updates local config.
        (1) --project-config option (2) zanata.xml in cwd
        """
        config_files = [os.path.join(os.getcwd(), filename) for filename
                        in project_config_file_tuple]

        if 'project_config' in self.command_dict:
            config_files.insert(0, self.command_dict['project_config'])

        for path in config_files:
            if os.path.exists(path):
                log.info("Loading zanata project config from: %s" % path)
                self.local_config.update(self.config.read_project_config(path))
                break

    def _update_url(self):
        """
        Process Server URL and update dicts
        """
        url_sources = (self.command_dict, self.local_config)
        url = url_sources[0].get('url') or url_sources[1].get('url')
        # validate url
        url_regex = re.compile(
            r'^(?:http)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url or url.isspace() or not url_regex.match(url):
            log.error("Please specify valid server url in zanata.xml or with '--url' option")
            sys.exit(1)
        # format url
        if ' ' in url or '\n' in url:
            log.info("Warning, the url which contains '\\n' or whitespace is not valid, please check zanata.xml")
            url = url.strip()
        if url[-1] == "/":
            url = url[:-1]
        # update url source dict
        for source in url_sources:
            if 'url' in source:
                source['url'] = url

    def _update_user_config(self):
        """
        Reads user configuration file and updates local config.
        (1) --user-config option (2) zanata.ini in $HOME/.config
        """
        user_config = [os.path.join(os.path.expanduser("~") + '/.config', filename)
                       for filename in user_config_file_tuple]
        if 'user_config' in self.command_dict and self.command_dict.get('user_config'):
            user_config.insert(0, self.command_dict['user_config'])

        for path in user_config:
            if os.path.exists(path):
                log.info("Loading zanata user config from: %s" % path)
                # Read the user-config file
                self.config.set_userconfig(path)
                try:
                    if self.mode == 'init':
                        self.local_config.update({'servers': self.config.get_servers()})
                        return
                    server = self.config.get_server(self.get_url())
                    if server:
                        user_name = self.config.get_config_value("username", "servers", server)
                        apikey = self.config.get_config_value("key", "servers", server)
                        if not (user_name, apikey):
                            log.info("Can not find user-config file in home folder,"
                                     "current path or path in '--user-config' option")
                        else:
                            self.local_config.update({'user_name': user_name, 'key': apikey})
                            log.info("zanata server: %s" % self.get_url())
                            return True
                except Exception as e:
                    log.error("Processing user-config file: %s" % str(e))
                    break
                break

    def _update_http_headers(self, accept_format=None):
        """
        Updates http_header in local_config
        """
        headers = {
            'X-Auth-User': self.command_dict.get('user_name') or self.local_config.get('user_name') or '',
            'X-Auth-Token': self.command_dict.get('key') or self.local_config.get('key') or '',
            'Accept': accept_format or 'application/json'
        }
        self.local_config.update({'http_headers': headers})

    def _update_client_version(self):
        """
        Updates client version in local_config
        """
        version_number = ""
        path = os.path.dirname(os.path.realpath(__file__))
        version_file = os.path.join(path, client_version_file)

        try:
            version = open(version_file, 'r')
            client_version = version.read()
            version.close()
            version_number = client_version.rstrip()[len('version: '):]
        except IOError:
            log.error("Please run VERSION-GEN or 'make install' to generate VERSION-FILE")
            version_number = "UNKNOWN"
        self.local_config.update({'client_version': version_number})

    def get_url(self):
        return self.command_dict.get('url') or self.local_config.get('url')

    def get_project_id_version(self):
        return (
            self.command_dict.get('project_id') or self.local_config.get('project_id'),
            self.command_dict.get('project_version') or self.local_config.get('project_version')
        )

    def _update_server_version(self):
        """
        This fetches and updates server version
        """
        version = VersionService(self.get_url(), self.local_config.get('http_headers'))

        if 'disablesslcert' in self.command_dict:
            version.disable_ssl_cert_validation()

        try:
            content = version.get_server_version()
            if content:
                server_version = content.get('versionNo')
                log.info("zanata python client version: %s, zanata server API version: %s" %
                         (self.local_config.get('client_version'), server_version))
                self.remote_config.update({'server_version': server_version})
        except UnAvaliableResourceException:
            log.info("zanata python client version: %s" % self.local_config.get('client_version'))
            log.error("Can not retrieve the server version, server may not support the version service")
        except UnavailableServiceError:
            log.error("Service Temporarily Unavailable, stop processing!")
            sys.exit(1)

    def _update_locale_mapping(self):
        """
        This fetches locale-mapping from server
        """
        local_config_locale_map = self.local_config.get('locale_map')
        if local_config_locale_map and len(local_config_locale_map.keys()) > 0:
            log.warn('Locale mappings are now handled using locale aliases on the server, '
                     'so locale mappings in the project config file (zanata.xml) are now deprecated.'
                     '\nPlease add a locale alias in the project language settings to replace each locale '
                     'mapping in zanata.xml, then remove the <locales> section from zanata.xml.')
            return
        # Call locale service
        locale_service = LocaleService(self.get_url(), self.local_config.get('http_headers'))
        project, version = self.get_project_id_version()
        if project:
            locales = locale_service.get_locales(project, version)
            locale_map = self.process_locales(locales)
            self.remote_config.update({'locale_map': locale_map})

    def _update_project_type(self):
        """
        This fetches project_type from server
        """
        if self.local_config.get('project_id') and self.local_config.get('project_version'):
            if self.local_config.get('http_headers').get('Content-Type'):
                self.local_config['http_headers']['Content-Type'] = 'application/xml'
            project_config = \
                IterationService(self.get_url(), self.local_config.get('http_headers')).config(
                    self.local_config.get('project_id'), self.local_config.get('project_version')
                )
            if project_config and project_config.get('project-type'):
                self.remote_config.update({'project_type': project_config['project-type']})

    def process_locales(self, locales):
        """
        process locales received from server
        :param locales:
        :return: locale_map
        """
        locale_map = {}
        if locales and len(locales) > 0:
            for locale in locales:
                locale_map.update(
                    {locale.get('alias') or locale.get('localeId'): locale.get('localeId')}
                )
        return locale_map

    def get_local_configs(self):
        """
        Selects methods for local configs for a given mode
        :return: methods_list
        """
        context_local_configs = {
            'default': [self._update_project_config, self._update_url, self._update_user_config,
                        self._update_http_headers, self._update_client_version],
            'init': [self._update_user_config, self._update_client_version],
        }
        return context_local_configs[self.mode]

    def get_remote_configs(self):
        """
        Selects methods for remote configs for a given mode
        :return: methods_list
        """
        context_remote_configs = {
            'default': [self._update_server_version, self._update_locale_mapping,
                        self._update_project_type],
            'init': [],
        }
        return context_remote_configs[self.mode]


class ProjectContext(ContextBase):
    """
    Class to build context_data dict for the project.
    Order of precedence would be (1) command options (2) local config (3) remote config
    """

    def get_context_data(self):
        """
        updates context_data with remote_config, local_config and command_dict
        """
        build_configs = [self.build_local_config,
                         self.build_remote_config]
        [method() for method in build_configs]
        # lowest to highest
        precedence = [self.remote_config, self.local_config, self.command_dict]
        context_data = functools.reduce(lambda option, value: {**option, **value}, precedence)
        return self.filter_context_data(context_data)

    def filter_context_data(self, data):
        """
        filters context data
        """
        # key was to fill http_header['token']
        remove_items = ['key']
        for item in remove_items:
            data.pop(item, None)
        return data

    def build_local_config(self):
        """
        This builds local configuration dict.
        """
        local_config_methods = self.get_local_configs()
        [method() for method in local_config_methods]

    def build_remote_config(self):
        """
        This builds remote configuration dict.
        """
        build_remote_config = self.get_remote_configs()
        [method() for method in build_remote_config]
        return self.remote_config
