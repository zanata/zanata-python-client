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
    "ZanataCmdTest",
)

import os
import sys
import unittest

from minimock import Mock

from zanataclient.zanatacmd import ZanataCommand
from zanataclient.zanatalib import ZanataResource
from zanataclient.zanatalib.projectutils import Project

sys.path.insert(0, os.path.abspath(__file__ + "/../../.."))


class ZanataCmdTest(unittest.TestCase):
    def setUp(self):
        self.zanatacmd = ZanataCommand()

    def test_list_projects(self):
        projects = []
        project_data = {'id': "test-project", 'name': "Test Project", 'type': "IterationProject", 'links': []}
        projects.append(Project(project_data))

        url = "http://localhost"
        zanata = ZanataResource(url)
        zanata.projects = Mock(url)
        zanata.projects.list.mock_returns = projects
        result = self.zanatacmd.list_projects(zanata)
        self.assertEqual(result[0].id, 'test-project')

    def test_project_info(self):
        pass

    def test_version_info(self):
        pass

    def test_create_project(self):
        pass

    def test_create_version(self):
        pass

    def test_pull_command(self):
        pass

    def test_push_command(self):
        pass


if __name__ == '__main__':
    unittest.main()
