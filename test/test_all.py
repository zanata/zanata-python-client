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

import unittest
# from test_zanata import ZanataTest
from test_parseconfig import ConfigTest
from test_publicanutil import PublicanUtilityTest
# from test_zanatacmd import ZanataCmdTest
from test_service import ServiceTest
from test_context import ProjectContextTest

suite = unittest.TestSuite()
# suite.addTest(unittest.makeSuite(ZanataTest))
suite.addTest(unittest.makeSuite(ConfigTest))
suite.addTest(unittest.makeSuite(PublicanUtilityTest))
# suite.addTest(unittest.makeSuite(ZanataCmdTest))
suite.addTest(unittest.makeSuite(ServiceTest))
suite.addTest(unittest.makeSuite(ProjectContextTest))
results = unittest.TextTestRunner(verbosity=2).run(suite)
