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

import sys
try:
    import json
except ImportError:
    import simplejson as json
from rest.client import RestClient
from project import Project
from project import Iteration
from error import *

class ProjectService:
    """
    Provides services to interact with Project, handle operaions of list, create and retrieve Project Resources  
    """
    def __init__(self, base_url, usrname, apikey):
        self.restclient = RestClient(base_url)
        self.iterations = IterationService(base_url, usrname, apikey)
        self.username = usrname
        self.apikey = apikey

    def list(self):
        """
        List the Project Resources on the Flies server
        @return: list of Project object
        """
        res, content = self.restclient.request_get('/seam/resource/restv1/projects')
         
        if res['status'] == '200':
            projects = []
            projects_json = json.loads(content)
            
            for p in projects_json:
                projects.append(Project(p))
            return projects
       
    def get(self, projectid):
        """
        Retrieve a specified Project Resource on Flies server
        @param projectid: Id of Project Resource
        @return: Project object
        @raise NoSuchProjectException:
        """     
        res, content = self.restclient.request_get('/seam/resource/restv1/projects/p/%s'%projectid)
        if res['status'] == '200' or res['status'] == '304':
            project = Project(json.loads(content))
            project.set_iteration(self.iterations)
            return project
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', content) 

    def create(self, project):
        """
        Create a Project Resource on Flies Server
        @param project: Project object
        @return: Success if status of response is 201
        @raise ProjectExistException:
        @raise NoSuchProjectException:
        @raise UnAuthorizedException:
        @raise BadRequestException:
        """
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
        res, content = self.restclient.request_put('/seam/resource/restv1/projects/p/%s'%project.id, args=body, headers=headers)
        
        if res['status'] == '201':
            return "Success"
        elif res['status'] == '200':
            raise ProjectExistException('Status 200', "The project is already exist on server")
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', content)
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')
        elif res['status'] == '400':
            raise BadRequestException('Error 400', content)
                    
    def delete(self):
        pass

    def status(self):
        pass

class IterationService:
    """
    Provides services to interact with Project iteration, handle operaions of list, create and retrieve iteration Resources
    """
    def __init__(self, base_url, usrname = None, apikey = None):
        self.restclient = RestClient(base_url)
        self.username = usrname
        self.apikey = apikey

    def get(self, projectid, iterationid):
        """
        Retrieve a specified Iteration Resource on Flies server
        @param projectid: Id of Project Resource
        @param iterationid: Id of Iteration Resource
        @return: Iteration object
        @raise NoSuchProjectException:
        """
        
        res, content = self.restclient.request_get('/seam/resource/restv1/projects/p/%s/iterations/i/%s'%(projectid,iterationid))
                
        if res['status'] == '200' or res['status'] == '304':
            return Iteration(json.loads(content))
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', content)
  
    def create(self, projectid, iteration):
        """
        Create a Iteration Resource on Flies Server
        @param projectid: Id of Project Resource
        @param iteration: Iteration object
        @return: Success if status of response is 201
        @raise ProjectExistException:
        @raise NoSuchProjectException:
        @raise UnAuthorizedException:
        @raise BadRequestException:
        """ 
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey
        
        body = '''{"name":"%s","id":"%s","description":"%s"}'''%(iteration.name, iteration.id, iteration.desc)
        res, content = self.restclient.request_put('/seam/resource/restv1/projects/p/%s/iterations/i/%s'%(projectid,iteration.id), args=body, headers=headers)
        if res['status'] == '201':
            return "Success"
        elif res['status'] == '200':
            raise ProjectExistException('Status 200', "The version is already exist on server")
        elif res['status'] == '404':
            raise NoSuchProjectException('Error 404', content)
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')
            
    def delete(self):
        pass
