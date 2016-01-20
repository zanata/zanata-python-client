# vim: set et sts=4 sw=4:
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
    "RestClient",
)

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import sys
import warnings
from io import StringIO
warnings.simplefilter("ignore", DeprecationWarning)
import httplib2

from .config import ServiceConfig


class RestClient(object):
    def __init__(self, base_url, disable_ssl_certificate_validation=True):
        self.base_url = base_url
        self.url = urlparse(base_url)
        self.http_client = httplib2.Http(disable_ssl_certificate_validation=True)

    def disable_ssl_cert_validation(self):
        params = dir(self.http_client)
        if 'disable_ssl_certificate_validation' in params:
            self.http_client.disable_ssl_certificate_validation = True

    def request(self, resource, method="get", body=None, headers=None, extension=None):
        if extension:
            resource = resource + extension

        if body is not None:
            thelen = str(len(body))
            headers['Content-Length'] = thelen
            body = StringIO(body)

        try:
            response, content = self.http_client.request(resource, method.upper(), body, headers=headers)
            if response.previous is not None:
                if response.previous.status == 301 or response.previous.status == 302:
                    if '-x-permanent-redirect-url' in response.previous:
                        new_url = response.previous['-x-permanent-redirect-url'][:-len(resource)]
                    elif 'location' in response.previous:
                        new_url = response.previous['location']
                    if new_url:
                        print("\nRedirecting to: %s" % '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(new_url)))
                        print("HTTP Redirect: Please update the Server URL.")
                        response, content = self.http_client.request(new_url, method.upper(), body, headers=headers)
            return (response, content.decode("UTF-8"))
        except httplib2.ServerNotFoundError as e:
            print("error: %s, Maybe the Zanata server is down?" % e)
            sys.exit(2)
        except httplib2.HttpLib2Error as e:
            print("error: %s" % e)
            sys.exit(2)
        except MemoryError as e:
            print("error: The file is too big to process")
        except Exception as e:
            value = str(e).rstrip()
            if value == 'a float is required':
                print("error: Error happens when processing https")
                if sys.version_info[:2] == (2, 6):
                    print("If version of python-httplib2 < 0.4.0, "
                          "please use the patch in http://code.google.com/p/httplib2/issues/detail?id=39")
                sys.exit(2)
            else:
                print("error: %s" % e)
                sys.exit(2)

    def process_request(self, service_name, *args, **kwargs):
        headers = kwargs['headers'] if 'headers' in kwargs else {}
        body = kwargs['body'] if 'body' in kwargs else None
        extension = kwargs['extension'] if 'extension' in kwargs else None
        service_details = ServiceConfig(service_name)
        # set headers
        if hasattr(service_details, 'response_media_type') and service_details.response_media_type:
            headers['Accept'] = service_details.response_media_type
        if hasattr(service_details, 'request_media_type') and service_details.request_media_type and body:
            headers['Content-Type'] = service_details.request_media_type
        # set resource
        resource = (
            service_details.resource.format(**dict(zip(service_details.path_params, args)))
            if args else service_details.resource
        )
        # initiate service call
        return self.request(self.base_url + resource, service_details.http_method, body, headers, extension)
