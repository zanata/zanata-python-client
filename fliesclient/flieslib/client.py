#vim:set et sts=4 sw=4: 
# 
# Flies Python Client
#
# Copyright (c) 2010 Jian Ni <jni@gmail.com>
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
        "FliesClient",
   )
import urlparse
import urllib
import os
import json
from rest.client import RestClient
from publican import Publican

class NoSuchProjectException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class InvalidOptionException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class NoSuchFileException(Exception):
    def __init__(self, expr, msg):
       	self.expr = expr
       	self.msg = msg

class UnAuthorizedException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class FliesClient:

    def __init__(self, base_url, username = None, apikey = None):
	self.base_url = base_url
	self.username = username
	self.apikey = apikey
	self.restclient = RestClient(self.base_url)
       	
    def list_projects(self):
        return self.restclient.Get('/projects')
    
    def get_project_info(self, projectid):
        return self.restclient.Get('/projects/p/%s'%projectid)
        
    def get_iteration_info(self, projectid, iterationid):
        return self.restclient.Get(self,'/projects/p/%s/iterations/i/%s'%(projectid,iterationid))

    def create_project(self, projectid, projectname, projectdesc):
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
           
        if projectname and projectdesc :
            body = '''{"name":"%s","id":"%s","description":"%s","type":"IterationProject"}'''%(projectname,projectid,projectdesc)
            res, content = self.restclient.request_put('/projects/p/%s'%projectid, args=body, headers=headers)
                         
            if res['status'] == '201': 
                return True
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'Un Authorized Operation')
        else:
            raise InvalidOptionException('Error','Invalid Options')
        
    def create_iteration(self, projectid, iterationid, iterationname, iterationdesc):
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
        
        if iterationname and iterationdesc :
            body = '''{"name":"%s","id":"%s","description":"%s"}'''%(iterationname, iterationid, iterationdesc)
            res, content = self.restclient.request_put('/projects/p/%s/iterations/i/%s'%(projectid,iterationid), args=body, headers=headers)
            if res['status'] == '201':
                return True
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'Un Authorized Operation')

        else:
            raise InvalidOptionException('Error', 'Invalid Options')
    
    def push_publican(self, filename, projectid, iterationid):
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
        filepath = os.path.join(os.getcwd(), filename)

        if not os.path.isfile(filepath):
            raise NoSuchFileException('Error', 'No Such File')
            
        publican = Publican(filepath) 
        textflows = publican.read_po()
        content ={
                    'name': filename,
                    'contenttype': 'text/plain',
                    'type': 'file',
                    'lang': 'en',
                    'extensions': [],
                    'textFlows': textflows
                 }
        body = json.JSONEncoder().encode(content)
        
        if projectid and iterationid :
            res, content = self.restclient.request_put('/projects/p/%s/iterations/i/%s/resources'%(projectid,iterationid), args=body, headers=headers)
            print res
            if res['status'] == '201':
                return True
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'Un Authorized Operation')
        else:
            raise InvalidOptionException('Error', 'Invalid Options')
           
    def pull_publican():
	    pass    

