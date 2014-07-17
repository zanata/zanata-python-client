#vim:set et sts=4 sw=4: 
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
        "VersionService",
   )

try:
    import json
except ImportError:
    import simplejson as json
from rest.client import RestClient
from error import UnAvaliableResourceException
from error import UnavailableServiceError


class VersionService:
    def __init__(self, base_url,headers=None):
        self.restclient = RestClient(base_url)
        self.http_headers = headers

    def disable_ssl_cert_validation(self):
        self.restclient.disable_ssl_cert_validation()
        
    def get_server_version(self):
        print self.http_headers
        res, content = self.restclient.request_version('/seam/resource/restv1/version',self.http_headers)
        
        if res['status'] == '200' or res['status'] == '304':
            version = json.loads(content)
            return version
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '503':
            raise UnavailableServiceError('Error 503', 'Service Temporarily Unavailable')
