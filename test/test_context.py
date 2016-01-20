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

all__ = (
    "ProjectContextTest",
)

import unittest
import sys
import os
import mock
sys.path.insert(0, os.path.abspath(__file__ + "/../.."))
from zanataclient.context import ProjectContext

# test data
command_options = {'comment_cols': [{'name': '--commentcols', 'value': 'en-US,es,pos,description',
                                     'internal': 'comment_cols', 'long': ['--commentcols'],
                                     'type': 'command', 'metavar': 'COMMENTCOLS'}],
                   'user_config': [{'name': '--user-config',
                                    'value': './testfiles/zanata.ini', 'internal': 'user_config',
                                    'long': ['--user-config'], 'type': 'command', 'metavar': 'USER-CONFIG'}],
                   'project_config': [{'name': '--project-config', 'value': './testfiles/zanata.xml',
                                       'internal': 'project_config', 'long': ['--project-config'],
                                       'type': 'command', 'metavar': 'PROJECT-CONFIG'}],
                   'project_type': [{'name': '--project-type', 'value': 'podir', 'internal': 'project_type',
                                     'long': ['--project-type'], 'type': 'command', 'metavar': 'PROJECTTYPE'}]}

version_service_return_content = {'versionNo': '3.7.3', 'buildTimeStamp': 'unknown', 'scmDescribe': 'unknown'}

iteration_locales_return_content = [{'displayName': 'English (United States)', 'localeId': 'en-US'},
                                    {'alias': 'pa-IN', 'displayName': 'Punjabi', 'localeId': 'pa'},
                                    {'alias': 'hi-IN', 'displayName': 'Hindi', 'localeId': 'hi'},
                                    {'displayName': 'Tamil (India)', 'localeId': 'ta-IN'},
                                    {'displayName': 'Bengali (India)', 'localeId': 'bn-IN'}]

project_locales_return_content = [{"displayName": "English (United States)", "localeId": "en-US"},
                                  {"displayName": "Hindi", "localeId": "hi"}, {"displayName": "Croatian", "localeId": "hr"},
                                  {"displayName": "Japanese", "localeId": "ja"}, {"displayName": "Kannada", "localeId": "kn"},
                                  {"displayName": "Chinese (Traditional, Taiwan)", "localeId": "zh-Hant-TW"}]

project_config_without_locale_map = {'transdir': '/home/user/project/target', 'project_type': 'gettext',
                                     'http_headers': {'Accept': 'application/json', 'X-Auth-User': 'username', 'X-Auth-Token': 'key'},
                                     'url': 'http://localhost:8080/zanata', 'key': 'key', 'srcdir': '/home/user/project/source',
                                     'project_version': '1.0', 'client_version': '1.3.12-74-g0b1d-mod', 'project_id': 'test-project',
                                     'user_name': 'username'}

mock_project_remote_config = {'url': 'http://localhost/zanata/', 'project': 'id', 'project-version': '1', 'project-type': 'podir'}


class ProjectContextTest(unittest.TestCase):
    def setUp(self):
        self.context = ProjectContext(command_options)
        self.init_context = ProjectContext(command_options, 'init')

    def test_command_options(self):
        command_options_keys = ['project_type', 'project_config', 'comment_cols', 'user_config']
        self.assertTrue(list(self.context.command_options.keys())[0] in command_options_keys)
        self.assertTrue(list(self.context.command_options.keys())[1] in command_options_keys)
        self.assertTrue(list(self.context.command_options.keys())[2] in command_options_keys)
        self.assertTrue(list(self.context.command_options.keys())[3] in command_options_keys)
        self.assertEqual(
            self.context.command_dict,
            {'project_config': './testfiles/zanata.xml', 'comment_cols': 'en-US,es,pos,description',
             'user_config': './testfiles/zanata.ini', 'project_type': 'podir'}
        )

    def test_build_local_config(self):
        self.context.build_local_config()
        self.assertEqual(self.context.local_config['url'], 'http://localhost:8080/zanata')
        self.assertEqual(self.context.local_config['project_id'], "test-project")
        self.assertEqual(self.context.local_config['project_version'], "1.0")
        self.assertEqual(self.context.local_config['project_type'], "gettext")
        self.assertEqual(self.context.local_config['locale_map'], {"zh-CN": "zh-Hans"})
        self.assertEqual(self.context.local_config['srcdir'], "/home/user/project/source")
        self.assertEqual(self.context.local_config['transdir'], "/home/user/project/target")
        self.assertEqual(self.context.local_config['user_name'], 'username')
        self.assertEqual(self.context.local_config['key'], 'key')
        self.assertEqual(
            self.context.local_config['http_headers'],
            {'Accept': 'application/json', 'X-Auth-User': 'username', 'X-Auth-Token': 'key'}
        )
        self.assertTrue('client_version' in self.context.local_config,
                        'local_config should contain client_version')

    @mock.patch('zanataclient.zanatalib.projectservice.LocaleService.get_locales')
    @mock.patch('zanataclient.zanatalib.versionservice.VersionService.get_server_version')
    @mock.patch('zanataclient.zanatalib.projectservice.IterationService.config')
    def test_build_remote_config(self, mock_config, mock_get_server_version, mock_get_locales):
        mock_config.return_value = mock_project_remote_config
        mock_get_server_version.return_value = version_service_return_content
        mock_get_locales.return_value = iteration_locales_return_content
        self.context.build_local_config()
        self.assertEqual(self.context.local_config['locale_map'], {"zh-CN": "zh-Hans"})
        # removing locale_map from local_config
        self.context.local_config.pop('locale_map', None)
        self.context.build_remote_config()
        self.assertEqual(
            self.context.remote_config['locale_map'],
            {'bn-IN': 'bn-IN', 'pa-IN': 'pa', 'en-US': 'en-US', 'hi-IN': 'hi', 'ta-IN': 'ta-IN'},
            'if not found context will go for remote locale_map'
        )
        self.assertEqual(self.context.remote_config['server_version'], '3.7.3')
        self.assertEqual(self.context.remote_config['project_type'], 'podir')

    @mock.patch('zanataclient.zanatalib.projectservice.LocaleService.get_locales')
    @mock.patch('zanataclient.zanatalib.versionservice.VersionService.get_server_version')
    @mock.patch('zanataclient.zanatalib.projectservice.IterationService.config')
    def test_get_context_data_local_locale_map(self, mock_config, mock_get_server_version, mock_get_locales):
        mock_config.return_value = mock_project_remote_config
        mock_get_server_version.return_value = version_service_return_content
        mock_get_locales.return_value = project_locales_return_content
        context_data = self.context.get_context_data()
        self.assertEqual(context_data['project_type'], 'podir',
                         'Command option overrides the project config project_type')
        self.assertEqual(context_data['locale_map'], {"zh-CN": "zh-Hans"},
                         'context_data should contain locale_map from project_config')
        options_set = []
        for optionset in (self.context.remote_config.keys(), self.context.local_config.keys(),
                          self.context.command_dict.keys()):
            options_set.extend(optionset)
        options_set = list(set(options_set))
        # Adding 1, as 'key' is being filtered out from context_data
        self.assertEqual(len(options_set), (len(context_data.keys()) + 1),
                         'context_data should contain all unique keys and their values')

    @mock.patch('zanataclient.parseconfig.ZanataConfig.read_project_config')
    @mock.patch('zanataclient.zanatalib.projectservice.LocaleService.get_locales')
    @mock.patch('zanataclient.zanatalib.versionservice.VersionService.get_server_version')
    @mock.patch('zanataclient.zanatalib.projectservice.IterationService.config')
    def test_get_context_data_remote_locale_map(
            self, mock_config, mock_get_server_version, mock_get_locales, mock_read_project_config
    ):
        mock_config.return_value = mock_project_remote_config
        mock_get_server_version.return_value = version_service_return_content
        mock_get_locales.return_value = project_locales_return_content
        mock_read_project_config.return_value = project_config_without_locale_map
        context_data = self.context.get_context_data()
        self.assertEqual(
            context_data['locale_map'],
            {'hi': 'hi', 'hr': 'hr', 'en-US': 'en-US', 'zh-Hant-TW': 'zh-Hant-TW', 'ja': 'ja', 'kn': 'kn'},
            'context_data should contain locale_map fetched from server'
        )

    def test_process_locales(self):
        locale_map = self.context.process_locales(iteration_locales_return_content)
        self.assertEqual(locale_map, {'bn-IN': 'bn-IN', 'pa-IN': 'pa', 'en-US': 'en-US',
                                      'hi-IN': 'hi', 'ta-IN': 'ta-IN'})

    def test_init_context(self):
        context_data = self.init_context.get_context_data()
        self.assertTrue('servers' in context_data)
        self.assertTrue('http://localhost:8080/zanata' in context_data['servers'])

if __name__ == '__main__':
    unittest.main()
