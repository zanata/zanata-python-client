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
from jsonmodel import BaseJsonModel
from rest.client import RestClient
from publican import Publican
from project import Project

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
        res, content = self.restclient.request_get('/projects')
        if res['status'] == '200':
            jsonmodel = BaseJsonModel(content)
            projects = jsonmodel.load_json()
            project = []
            for p in projects:
                id = p['id']
                name = p['name']
                type = p['type']
                p = Project(id=id, name = name, type = type)
                project.append(p)
            return project

    def get_project_info(self, projectid):
        res, content = self.restclient.request_get('/projects/p/%s'%projectid)
        if res['status'] == '200':
            jsonmodel = BaseJsonModel(content)
            project = jsonmodel.load_json()
            id = project['id']
            name = project['name']
            type = project['type']
            desc = project['description']
            p = Project(id=id, name = name, type = type, desc = desc)
            return p
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', 'No Such project')

    def get_iteration_info(self, projectid, iterationid):
        return self.restclient.request_get('/projects/p/%s/iterations/i/%s'%(projectid,iterationid))

    def create_project(self, projectid, projectname, projectdesc):
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
           
        if projectname and projectdesc :
            body = '''{"name":"%s","id":"%s","description":"%s","type":"IterationProject"}'''%(projectname,projectid,projectdesc)
            res, content = self.restclient.request_put('/projects/p/%s'%projectid, args=body, headers=headers)
                         
            if res['status'] == '201': 
                return "Success"
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
                return "Success"
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')

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
                    'textFlows':textflows,
                    'name': filename,
                    'type': 'FILE',
                    'contentType': 'application/x-gettext',
                    'extensions': [],
                    'lang': 'en'
                 }
        body = json.JSONEncoder().encode(content)
               
        if projectid and iterationid :
            res, content = self.restclient.request_post('/projects/p/%s/iterations/i/%s/resources/'%(projectid,iterationid), args=body, headers=headers)
            
            if res['status'] == '201':
                return "Success"
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        else:
            raise InvalidOptionException('Error', 'Invalid Options')
           
    def pull_publican():
	    pass    

    def remove_project():
        pass

    def remove_iteration():
        pass

    def project_status():
        pass
