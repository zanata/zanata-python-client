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
import exceptions
import warnings
warnings.simplefilter("ignore",DeprecationWarning)
import httplib2

class RestClient(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.url = urlparse.urlparse(base_url)
    
    def request_get(self, resource, args = None, body = None, headers = {}, extension = None):        
        return self.request(resource, "get", args, body, headers, extension)
    
    def request_post(self, resource, args = None, body = None, headers = {}, extension = None, copytrans = None):
        return self.request(resource, "post", args, body, headers, extension, copytrans)
            
    def request_put(self, resource, args = None, body = None, headers = {}, extension = None, copytrans = None):
        return self.request(resource, "put", args, body, headers, extension, copytrans = copytrans)

    def request_delete(self, resource, args = None, body = None, headers = {}, extension = None):
        return self.request(resource, "delete", args, body, headers, extension)
    
    def request(self, resource, method = "get", args = None, body = None, headers = {}, extension = None, copytrans =
    None):
        headers['Accept'] = 'application/json'
        http = httplib2.Http()
        ext = "?ext=gettext&ext=comment"
                
        if copytrans:
            if ext == "":
                ext="?copyTrans=true"
            else:
                ext=ext+"&copyTrans=true"
        
        if args:
            if method == "put" or method == "post":
                headers['Content-Type'] = 'application/json'
                body = args
        
        try:
            response, content = http.request("%s%s%s" % (self.base_url, resource, ext), method.upper(), body, headers=headers)
            if response.previous.status == 301 or response.previous.status == 302:
                print "warnning: Please update the URL of the server"
            return (response, content.decode("UTF-8"))
        except httplib2.ServerNotFoundError, e:
            print "error: %s, Maybe the flies sever is down?"%e
            sys.exit(2)
        except httplib2.HttpLib2Error, e:
            print "error: %s"%e
            sys.exit(2)
        except Exception, e:
            print "error: %s"%e
            sys.exit(2)

    def request_version(self, resource):
        http = httplib2.Http(".cache")
        try:
            response, content = http.request("%s%s" % (self.base_url, resource), "GET")
            if response.previous.status == 301 or response.previous.status == 302:
                print "warnning: Please update the URL of the server"
            return (response, content.decode("UTF-8"))
        except httplib2.ServerNotFoundError, e:
            print "error: %s, Maybe the Zanata/Flies sever is down?"%e
            sys.exit(2)
        except httplib2.HttpLib2Error, e:
            print "error: %s"%e
            sys.exit(2)
        except Exception, e:
            print "error: %s"%e
            sys.exit(2)
 
