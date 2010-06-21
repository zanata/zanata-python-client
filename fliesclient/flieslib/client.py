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
        "FliesResource", 
   )
import urlparse
import urllib
import os
import json
from rest.client import RestClient
from publican import Publican
from project import Project
from project import Iteration

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

class BadRequestException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class ProjectService:
    def __init__(self, base_url, usrname, apikey):
        self.restclient = RestClient(base_url)
        self.iterations = IterationService(base_url, usrname, apikey)
        self.username = usrname
        self.apikey = apikey

    def list(self):
        res, content = self.restclient.request_get('/projects')
        if res['status'] == '200':
            projects = []
            projects_json = json.loads(content)
            for p in projects_json:
                projects.append(Project(json = p))
            return projects

    def get(self, projectid):
        res, content = self.restclient.request_get('/projects/p/%s'%projectid)
        if res['status'] == '200':
            my_project = Project(json = json.loads(content), iterations = self.iterations)
            return my_project
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', 'No Such project')

    def create(self, project):
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
        if project.name and project.desc :
            body ='''{"name":"%s","id":"%s","description":"%s","type":"IterationProject"}'''%(project.name,project.id,project.desc)
            res, content = self.restclient.request_put('/projects/p/%s'%project.id, args=body, headers=headers)
            if res['status'] == '201':
                return "Success"
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'Un Authorized Operation')
            elif res['status'] == '400':
                raise BadRequestException('Error 400', 'Bad Request')
        else:
            raise InvalidOptionException('Error','Invalid Options') 
            
    def delete(self):
        pass

    def status(self):
        pass

class IterationService:   
    def __init__(self, base_url, usrname = None, apikey = None):
        self.restclient = RestClient(base_url)
        self.username = usrname
        self.apikey = apikey
    
    def get(self, projectid, iterationid):
        res, content = self.restclient.request_get('/projects/p/%s/iterations/i/%s'%(projectid,iterationid))
        if res['status'] == '200':
            iter = Iteration(json.loads(content))
            return iter
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', 'No Such project')
        
    def create(self, projectid, iteration):
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
        
        if iteration.name and iteration.desc :
            body = {"name":"%s","id":"%s","description":"%s"}%(iteration.name, iteration.id, iteration.desc)
            res, content = self.restclient.request_put('/projects/p/%s/iterations/i/%s'%(projectid,iteration.id), args=body, headers=headers)
            if res['status'] == '201':
                return "Success"
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        else:
            raise InvalidOptionException('Error', 'Invalid Options')
    
    def delete(self):
        pass
    
class PublicanService:    
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

class FliesResource:
    def __init__(self, base_url, username = None, apikey = None):
        self.base_url = base_url
        self.projects = ProjectService(base_url, username, apikey)


