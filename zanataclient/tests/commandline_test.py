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

all__ = (
            "CommandlineTest",
        )

import unittest
import sys
from zanataclient.zanata import options
from zanataclient.zanata import ZanataConsole

class CommandlineTest(unittest.TestCase):
    def setUp(self):
        self.console = ZanataConsole()
        
    def test_helpcommandoption(self):
        sys.argv = ["zanata", "help"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(command, "help")
    
    #"url=", "project-id=", "project-version=", "project-name=",
    #"project-desc=", "version-name=", "version-desc=", "lang=",  "user-config=", "project-config=", "apikey=",
    #"username=", "srcdir=", "dstdir=", "email=", "transdir=", "import-po", "copytrans"

    def test_listcommandoption(self):
        sys.argv = ["zanata", "list", "--url", "http://example.com/flies"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(command, "list")
        self.assertEqual(options['url'], "http://example.com/flies")

    def test_projectcommandoption(self):
        sys.argv = ["zanata", "project", "info", "--project-id", "test-project"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(options['project_id'], "test-project")

        sys.argv = ["zanata", "project", "create", "test-project", "--project-name", "test project", "--project-desc", "This is test project"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(command, "project_create")
        self.assertEqual(command_args, ['test-project'])
        self.assertEqual(options['project_name'], "test project")
        self.assertEqual(options['project_desc'], "This is test project")

    def test_versioncommandoption(self):
        sys.argv = ["zanata", "version", "info", "--project-id", "test-project", "--project-version", "1.0"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(command, "version_info")
        self.assertEqual(options['project_id'], "test-project")
        self.assertEqual(options['project_version'], "1.0")

        sys.argv = ["zanata", "version", "create", "1.0", "--project-id", "test-project", "--version-name", "Version 1.0", "--version-desc", "This is Version 1.0"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(command, "version_create")
        self.assertEqual(command_args, ['1.0'])
        self.assertEqual(options['project_id'], "test-project")
        self.assertEqual(options['version_name'], "Version 1.0")
        self.assertEqual(options['version_desc'], "This is Version 1.0")

    def test_publicancommandoption(self):
        sys.argv = ["zanata", "publican", "push", "--project-id", "test-project", "--project-version", "1.0", "--srcdir",
        "/home/fc12/pot", "--no-copytrans", "--import-po"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(command, "publican_push")
        self.assertEqual(options['project_id'], "test-project")
        self.assertEqual(options['project_version'], "1.0")
        self.assertEqual(options['srcdir'], "/home/fc12/pot")
        self.assertFalse(options['copytrans'])
        self.assertTrue(options['importpo'])

        sys.argv = ["zanata", "publican", "pull"]        
        command, command_args = self.console._process_command_line()
        self.assertEqual(command, "publican_pull")

if __name__ == '__main__':
    unittest.main()
