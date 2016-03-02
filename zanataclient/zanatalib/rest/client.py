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
    "RestHandle", "RestClient"
)

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import os
import sys
import warnings
from io import StringIO
warnings.simplefilter("ignore", DeprecationWarning)
import httplib2

from .config import ServiceConfig

CACHE_DIR_NAME = ".cache"
NO_CERT_VALIDATION = True
DEFAULT_MAX_REDIRECTS = 5


class RestHandle(object):
    """
    httplib2 wrapper, a handle for REST communication
    """
    def __init__(self, *args, **kwargs):
        """
        RestHandle constructor
        :param args: base="http://localhost", uri="/zanata", method="GET"
        :param kwargs: body=None, headers=None, redirections=DEFAULT_MAX_REDIRECTS, connection_type=None,
                        cache=".cache", ext="?lang=hi"
        """
        enable_cache = False
        if len([arg for arg in args if arg]) != 3:
            raise Exception('Insufficient args.')
        self.base_url, self.uri, self.method = args

        for attrib, value in kwargs.items():
            if value:
                setattr(self, str(attrib), value)

        if enable_cache:
            cache_dir_name = getattr(self, 'cache', None) or CACHE_DIR_NAME
            if cache_dir_name and os.path.exists(cache_dir_name):
                [os.remove(os.path.join(cache_dir_name, file)) for file in os.listdir(cache_dir_name)]
        else:
            cache_dir_name = None

        self.http = httplib2.Http(cache_dir_name,
                                  disable_ssl_certificate_validation=NO_CERT_VALIDATION)
        self.http.clear_credentials()
        self.http.follow_redirects = True

    def _get_url(self):
        if self.base_url[-1:] == '/':
            self.base_url = self.base_url[:-1]
        return '%s%s%s' % (self.base_url, self.uri, getattr(self, 'ext')) \
            if hasattr(self, 'ext') else '%s%s' % (self.base_url, self.uri)

    def _call_request(self, uri, http_method, **args_dict):
        try:
            response, content = self.http.request(
                uri, http_method, **args_dict
            )
            return response, content
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

    def manage_redirection(self, rest_resp, args_dict):
        if rest_resp.previous.status == 301 and '-x-permanent-redirect-url' in rest_resp.previous:
            self.base_url = rest_resp.previous['-x-permanent-redirect-url']
            url = self._get_url()
        elif rest_resp.previous.status == 302 and 'location' in rest_resp.previous:
            url = rest_resp.previous['location']
            print("\nRedirecting to: %s" % '{uri.scheme}://{uri.netloc}/ '
                                           'Please update the Server URL.'.format(uri=urlparse(url)))
        return self._call_request(url, self.method, **args_dict)

    def get_response_content(self):
        request_optional_args = ('body', 'headers', 'connection_type')
        args_dict = dict(zip(
            request_optional_args,
            [getattr(self, arg, None) for arg in request_optional_args]
        ))
        args_dict.update({'redirections': DEFAULT_MAX_REDIRECTS})
        response, content = self._call_request(self._get_url(), self.method, **args_dict)

        while response and response.previous is not None:
            response, content = self.manage_redirection(response, args_dict)

        return response, content.decode("UTF-8")


class RestClient(object):
    def __init__(self, base_url, disable_ssl_certificate_validation=True):
        self.base_url = base_url

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
        # format body
        if body is not None:
            thelen = str(len(body))
            headers['Content-Length'] = thelen
            body = StringIO(body)
        # initiate service call
        rest_handle = RestHandle(
            self.base_url, resource, service_details.http_method,
            body=body, headers=headers, ext=extension, connection_type=None, cache=None
        )
        return rest_handle.get_response_content()
