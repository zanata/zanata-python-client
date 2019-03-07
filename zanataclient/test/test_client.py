#
# Zanata Python Client
#
# Copyright (c) 2016 Sundeep Anand <suanand@redhat.com>
# Copyright (c) 2016 Red Hat, Inc.
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
    "RestHandleTest",
)

import os
import sys

import mock

from zanataclient.zanatalib.rest.client import RestHandle


if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
sys.path.insert(0, os.path.abspath(__file__ + "/../../.."))

# test data
URL = r'http://localhost:8080/zanata'
RESOURCE = r'/seam/resource/restv1/projects'
METHOD = 'GET'
HEADERS = {'Accept': 'application/json',
           'Content-Type': 'application/json'}


# mock data
class FalseDict(dict):
    """
    false dict class
    """
    @property
    def previous(self):
        return None

    @property
    def status(self):
        return 200


response = FalseDict()
response.update({'status': '200', 'access-control-allow-headers': 'X-Requested-With, Content-Type, Accept,',
                 'content-location': 'http://localhost:8080/zanata/seam/resource/restv1/projects',
                 'x-powered-by': 'Undertow/1', 'transfer-encoding': 'chunked',
                 'set-cookie': 'JSESSIONID=agEMOfPqFX_8HfWUTHgvjTcBONgArrZJbpSUHrY2.dhcp201-126; path=/zanata',
                 'server': 'WildFly/8', 'connection': 'keep-alive', 'date': 'Wed, 02 Mar 2016 12:25:52 GMT',
                 'access-control-allow-origin': '*', 'access-control-allow-methods': 'GET',
                 'content-type': 'application/json'})

content = b'[{"id":"black-silver","defaultType":"","name":"Black Silver",' \
          b'"links":[{"href":"p/black-silver","rel":"self","type":"application/vnd.zanata.project+json"}],' \
          b'"status":"ACTIVE"}]'


class RestHandleTest(unittest.TestCase):
    def setUp(self):
        self.http_client = RestHandle(
            URL, RESOURCE, METHOD, headers=HEADERS
        )

    @unittest.skipIf(
        sys.version_info < (2, 7),
        'https://docs.python.org/2/library/unittest.html#unittest.TestCase.assertRaises'
    )
    def test_insufficient_args(self):
        with self.assertRaises(Exception):
            RestHandle(URL, RESOURCE, None)

    @mock.patch('zanataclient.zanatalib.rest.client.RestHandle._call_request')
    def test_get_response_content(self, mock_call_request):
        mock_call_request.return_value = response, content
        response_content = self.http_client.get_response_content()
        self.assertEqual(len(response_content), 2, 'both response and content')
        self.assertEqual(response_content[0]['status'], '200', 'http response status')
        self.assertEqual(response_content[0]['content-type'], 'application/json', 'valid response')
        self.assertTrue('id' in response_content[1], 'project id should be in content')
        self.assertTrue('name' in response_content[1], 'project name should be in content')
        self.assertTrue('links' in response_content[1], 'links should be in content')
        self.assertTrue('status' in response_content[1], 'project status should be in content')


if __name__ == '__main__':
    unittest.main()
