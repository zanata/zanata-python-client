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

__all__ = (
        "RestClient",
    )  

import urlparse
import urllib
import base64
import warnings 
import socket
import sys

with warnings.catch_warnings():
     warnings.filterwarnings("ignore",category=DeprecationWarning)
     import httplib2
     
class RestClient():
    def __init__(self, base_url):
        self.base_url = base_url
        self.url = urlparse.urlparse(base_url)
    
    def request_get(self, resource, args = None, body = None, headers = {}):
        return self.request(resource, "get", args, body, headers)
    
    def request_post(self, resource, args = None, body = None, headers = {}):
        return self.request(resource, "post", args, body, headers)
    
    def request_put(self, resource, args = None, body = None, headers = {}):
        return self.request(resource, "put", args, body, headers)
    
    def request(self, resource, method = "get", args = None, body = None, headers = {}):
        path = resource
        headers['Accept'] = 'application/json'
        http = httplib2.Http()
        
        if args:
            if method == "put" or method == "post":
                headers['Content-Type'] = 'application/json'
                body = args
        try:
            response, content = http.request("%s%s" % (self.base_url, resource), method.upper(), body=body, headers=headers)
            return (response, content.decode("UTF-8"))
        except Exception as e:
            raise 

