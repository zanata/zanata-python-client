#vim:set et sts=4 sw=4: 
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
        "ProjectService", 
   )

"""Provides services to interact with Project and Iteration Resources
ProjectService: handle operaions of list, create and retrieve Project Resources  
"""
import sys
import json
from ordereddict import OrderedDict
from rest.client import RestClient
from project import Project
from project import Iteration
from error import *

class ProjectService:
    def __init__(self, base_url, usrname, apikey):
        self.restclient = RestClient(base_url)
        self.iterations = IterationService(base_url, usrname, apikey)
        self.username = usrname
        self.apikey = apikey

    """
    List the Project Resources on the Flies server
    Args: None
    Returns: list of Project object
    """
    def list(self):
        res, content = self.restclient.request_get('/projects')
        if res['status'] == '200':
            projects = []
            projects_json = json.loads(content)
            for p in projects_json:
                projects.append(Project(json = p))
            return projects
       
    """
    Retrieve a specified Project Resource on Flies server
    Args: projectid: Id of Project Resource
    Returns: Project object
    Raise: a NoSuchProjectException
    """    
    def get(self, projectid):
        res, content = self.restclient.request_get('/projects/p/%s'%projectid)
        if res['status'] == '200':
            return Project(json = json.loads(content), iterations = self.iterations)
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', 'No Such project') 
    
    """
    Create a Project Resource on Flies Server
    Args: project: Project object
    Returns: Success if status of response is 201
    Raises: ProjectExistException, NoSuchProjectException, UnAuthorizedException and BadRequestException
    """
    def create(self, project):
        exist = False
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
        try:
            self.get(project.id)
            raise ProjectExistException('Status 200', 'The project is already exist')
        except NoSuchProjectException:
            exist = False

        body ='''{"name":"%s","id":"%s","description":"%s","type":"IterationProject"}'''%(project.name,project.id,project.desc)
        res, content = self.restclient.request_put('/projects/p/%s'%project.id, args=body, headers=headers)
        
        if res['status'] == '201':
            return "Success"
        elif rest['status'] == '200':
            raise ProjectExistException('Status 200', 'The project is already exist')
        eloif res['status'] == '404':
            raise NoSuchProjectException('Error 404', 'No Such project')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'Un Authorized Operation')
        elif res['status'] == '400':
            raise BadRequestException('Error 400', 'Bad Request')
                    
    def delete(self):
        pass

    def status(self):
        pass

class IterationService:   
    def __init__(self, base_url, usrname = None, apikey = None):
        self.restclient = RestClient(base_url)
        self.username = usrname
        self.apikey = apikey
    
    """
    Retrieve a specified Iteration Resource on Flies server
    Args: 
        projectid: Id of Project Resource
        iteraionid: Id of Iteration Resource
    Returns: Iteration object
    Raise: a NoSuchProjectException
    """
    def get(self, projectid, iterationid):
        res, content = self.restclient.request_get('/projects/p/%s/iterations/i/%s'%(projectid,iterationid))
        if res['status'] == '200':
            return Iteration(json.loads(content))
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', 'No Such project')
    
    """
    Create a Iteration Resource on Flies Server
    Args: 
        projectid: Id of Project Resource
        iteraion: Iteration object
    Returns: Success if status of response is 201
    Raises: ProjectExistException, NoSuchProjectException, UnAuthorizedException and BadRequestException
    """    
    def create(self, projectid, iteration):
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
        
        body = '''{"name":"%s","id":"%s","description":"%s"}'''%(iteration.name, iteration.id, iteration.desc)
        res, content = self.restclient.request_put('/projects/p/%s/iterations/i/%s'%(projectid,iteration.id), args=body, headers=headers)
        if res['status'] == '201':
            return "Success"
        elif rest['status'] == '200':
            raise ProjectExistException('Status 200', 'The project is already exist')
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', 'No Such project')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
            
    def delete(self):
        pass
