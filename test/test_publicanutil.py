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

all__ = (
    "PublicanUtilityTest",
)

import unittest
import sys
import os
import json
sys.path.insert(0, os.path.abspath(__file__ + "/../.."))

from zanataclient.publicanutil import PublicanUtility


class PublicanUtilityTest(unittest.TestCase):
    def setUp(self):
        self.publican = PublicanUtility()

    def test_strippath(self):
        filename = self.publican.strip_path("./testfiles/pot/test.pot", "./testfiles/pot", '.pot')
        self.assertEqual(filename, "test")

    """
    def test_potfiletojson(self):
        body, filename = self.publican.potfile_to_json("./testfiles/pot/test.pot", "./testfiles/pot")
        json_data = open('./testfiles/pot/test.json')
        result = json.loads(body)
        expect_json = json.load(json_data)
        self.assertEqual(result['name'], "test")
        self.assertEqual(result['textFlows'], expect_json['textFlows'])
        self.assertEqual(result['contentType'], "application/x-gettext")
        self.assertEqual(result['extensions'], expect_json['extensions'])

        json_data.close()

    def test_pofiletojson(self):
        body = self.publican.pofile_to_json("./testfiles/po/test.po")
        json_data = open('./testfiles/po/test.json')
        result = json.loads(body)
        expect_json = json.load(json_data)
        self.assertEqual(result['textFlowTargets'], expect_json['textFlowTargets'])
        self.assertEqual(result['extensions'], expect_json['extensions'])
        json_data.close()

    def test_msgidplural(self):
        body, filename = self.publican.potfile_to_json("./testfiles/test_plural.po", "./testfiles/po")
        json_data = open('./testfiles/msgid_plural.json')
        result = json.loads(body)
        expect_json = json.load(json_data)
        self.assertEqual(result['textFlows'], expect_json['textFlows'])
        json_data.close()

    def test_msgstrplural(self):
        body = self.publican.pofile_to_json("./testfiles/test_plural.po")
        json_data = open('./testfiles/msgstr_plural.json')
        result = json.loads(body)
        expect_json = json.load(json_data)
        print result
        self.assertEqual(result['textFlowTargets'], expect_json['textFlowTargets'])
        self.assertEqual(result['extensions'], expect_json['extensions'])
        json_data.close()
    """
if __name__ == '__main__':
    unittest.main()
