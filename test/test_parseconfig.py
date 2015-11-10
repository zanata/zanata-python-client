#
# Zanata Python Client
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
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

all__ = (
    "ConfigTest",
)

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + "/../.."))

from zanataclient.parseconfig import ZanataConfig


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = ZanataConfig()

    def test_user_config(self):
        self.config.set_userconfig("./testfiles/zanata.ini")
        server = self.config.get_server("http://localhost:8080/zanata")
        user_name = self.config.get_config_value("username", 'servers', server)
        apikey = self.config.get_config_value("key", 'servers', server)
        self.assertEqual(server, "local")
        self.assertEqual(user_name, "username")
        self.assertEqual(apikey, "key")

    def test_project_config(self):
        project_config = self.config.read_project_config("./testfiles/zanata.xml")
        self.assertEqual(project_config['project_url'], "http://localhost:8080/zanata/")
        self.assertEqual(project_config['project_id'], "test-project")
        self.assertEqual(project_config['project_version'], "1.0")
        self.assertEqual(project_config['locale_map'], {"zh-CN": "zh-Hans"})
        self.assertEqual(project_config['src_dir'], "/home/user/project/source")
        self.assertEqual(project_config['trans_dir'], "/home/user/project/target")

if __name__ == '__main__':
    unittest.main()
