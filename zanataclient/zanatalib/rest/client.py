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

import urlparse
import warnings
import sys
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
import httplib2

class RestClient(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.url = urlparse.urlparse(base_url)
        self.http_client = httplib2.Http()

    def disable_ssl_cert_validation(self):
        params = dir(self.http_client)
        if 'disable_ssl_certificate_validation' in params:
            self.http_client.disable_ssl_certificate_validation = True

    def set_headers(self, headers, method, args):
        headers['Accept'] = 'application/json'

        if args:
            if method == "put" or method == "post":
                headers['Content-Type'] = 'application/json' 

        return headers

    def set_resource(self, resource, extension = None):
        if extension:
            return "%s%s%s" % (self.base_url, resource, extension)
        else:
            return "%s%s" % (self.base_url, resource)

    def request_get(self, resource, args = None, body = None,
                    headers = {}, extension = None):
        headers = self.set_headers(headers, "get", args)
        resource = self.set_resource(resource, extension)
        return self.request(resource, "get", body, headers)

    def request_post(self, resource, args = None, body = None,
                     headers = {}, extension = None):
        headers = self.set_headers(headers, "post", args)
        if args:
            body = args
        resource = self.set_resource(resource, extension)
        return self.request(resource, "post", body, headers)

    def request_put(self, resource, args = None, body = None,
                    headers = {}, extension = None):
        headers = self.set_headers(headers, "put", args)
        if args:
            body = args
        resource = self.set_resource(resource, extension)  
        return self.request(resource, "put", body, headers)

    def request_delete(self, resource, args = None, body = None,
                       headers = {}, extension = None):
        headers = self.set_headers(headers, "delete", args)
        resource = self.set_resource(resource, extension)
        return self.request(resource, "delete", body, headers)

    def request_version(self, resource):
        resource = self.set_resource(resource)
        return self.request(resource, "get")

    def request(self, resource, method = "get", body = None, headers = None):
        try:
            response, content = self.http_client.request(resource, method.upper(), body, headers=headers)
            if response.previous is not None:
                if response.previous.status == 301 or response.previous.status == 302:
                    new_url = response.previous['-x-permanent-redirect-url'][:-len(resource)]
                    print "HTTP redirect: redirect to %s, please update the server URL to new URL" % new_url
            return (response, content.decode("UTF-8"))
        except httplib2.ServerNotFoundError, e:
            print "error: %s, Maybe the flies sever is down?" % e
            sys.exit(2)
        except httplib2.HttpLib2Error, e:
            print "error: %s" % e
            sys.exit(2)
        except Exception, e:
            value = str(e).rstrip()
            if value == 'a float is required':
                print "error: Error happens when processing https"
                if sys.version_info[:2] == (2, 6):
                    print "If version of python-httplib2 < 0.4.0, please use the patch in http://code.google.com/p/httplib2/issues/detail?id=39"
                sys.exit(2)
            else:
                print "error: %s" % e
                sys.exit(2)
