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
    "ServiceTest",
)

import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + "/../.."))
from zanataclient.zanatalib.service import Service
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


# test data
SERVICE_RESPONSE_200 = {'status': '200'}
SERVICE_RESPONSE_201 = {'status': '201'}
SERVICE_RESPONSE_401 = {'status': '401'}
SERVICE_RESPONSE_503 = {'status': '503'}
RESPONSE_CONTENT = {}
RESPONSE_CONTENT_200 = '[{"project-name": "test-project", "project-id": "12345"}]'
SERVICE_RESPONSE_200_XML = {'status': '200', 'content-type': 'application/xml'}
RESPONSE_CONTENT_200_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
                           '<config xmlns="http://zanata.org/namespace/config/">\n  ' \
                           '<url>https://translate.zanata.org/zanata/</url>\n  ' \
                           '<project>test-project</project>\n  ' \
                           '<project-version>12345</project-version>\n  ' \
                           '<project-type>podir</project-type>\n\n</config>\n'


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = Service(base_url="http://localhost", username='user',
                               apikey='key', http_headers=None)

    def test_messages_status_200(self):
        result_set = self.service.messages(SERVICE_RESPONSE_200, RESPONSE_CONTENT_200)
        self.assertEqual(result_set[0]['project-id'], "12345")
        self.assertEqual(result_set[0]['project-name'], "test-project")

    def test_messages_status_200_xml(self):
        result_set = self.service.messages(SERVICE_RESPONSE_200_XML, RESPONSE_CONTENT_200_XML)
        self.assertEqual(result_set['project-version'], "12345")
        self.assertEqual(result_set['project'], "test-project")
        self.assertEqual(result_set['project-type'], "podir")

    def test_messages_status_201(self):
        result_set = self.service.messages(SERVICE_RESPONSE_201, RESPONSE_CONTENT)
        self.assertTrue(result_set)

    @unittest.skipIf(
        sys.version_info < (2, 7),
        'https://docs.python.org/2/library/unittest.html#unittest.TestCase.assertRaises'
    )
    def test_messages_status_401_503(self):
        with self.assertRaises(SystemExit):
            self.service.messages(SERVICE_RESPONSE_401, RESPONSE_CONTENT)
        with self.assertRaises(SystemExit) as ex:
            self.service.messages(SERVICE_RESPONSE_503, RESPONSE_CONTENT)
        self.assertEqual(ex.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
