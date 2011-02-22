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
        "DocumentService",
   )

import os
try:
    import json
except ImportError:
    import simplejson as json
import sys
from rest.client import RestClient
from error import *

class DocumentService:    
    def __init__(self, projects):
        self.projects = projects
    
    def get_file_list(self, projectid, iterationid):
        res, content = self.projects.restclient.request_get('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r'%(projectid, iterationid))
        
        if res['status'] == '200' or res['status'] == '304':
            list = json.loads(content)
            filelist = [file.get('name') for file in list]
            return filelist
        elif res['status'] == '500':
            raise InternalServerError('Error 500', 'An internal server error happens')
    
    def update_template(self, projectid, iterationid, file, resources, extension, copytrans):
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException,e:
                print "[ERROR] %s"%(e.msg)
                sys.exit()

        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
         
        res, content = self.projects.restclient.request_put('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s'%(projectid,iterationid,file), args=resources, headers=headers, extension=extension, copytrans=copytrans)
         
        if res['status'] == '201' or res['status'] == '200':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', 'Unable to read request body.')
        elif res['status'] == '409':
            raise SameNameDocumentException('Error 409', 'A document with same name already exists.')
    
    def commit_template(self, projectid, iterationid, resources, extension, copytrans):
        """
        Push the json object to flies server
        @param projectid: id of project
        @param iterationid: id of iteration
        @param resources: json object of the content that want to commit to flies server
        @return: True
        @raise UnAuthorizedException:
        @raise BadRequestBodyException:
        @raise SameNameDocumentException:
        """
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException,e:
                print "[ERROR] %s"%(e.msg)
                sys.exit()

        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
        
        res, content = self.projects.restclient.request_post('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r'%(projectid,iterationid), args=resources, headers=headers, extension=extension, copytrans=copytrans)
        
        if res['status'] == '201':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', content)
        elif res['status'] == '409':
            raise SameNameDocumentException('Error 409', content)

    def delete_template(self, projectid, iterationid, file, extension):
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException, e:
                print "[ERROR] %s"%(e.msg)
                sys.exit()
        
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey    
        
        res, content = self.projects.restclient.request_delete('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s'%(projectid, iterationid, file), headers=headers, extension=extension)
        
        if res['status'] == '200' or res['status'] == '304':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation') 
    
    def retrieve_template(self, projectid, iterationid, file, extension):
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException, e:
                print "[ERROR] %s"%(e.msg)
                sys.exit()
        
        res, content = self.projects.restclient.request_get('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s'%(projectid, iterationid, file), extension=extension)
                
        if res['status'] == '200' or res['status'] == '304':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')        

    def retrieve_translation(self, lang, projectid, iterationid, file, extension):
        """
        Get translation content of file from Flies server
        @param lang: language
        @param projectid: Id of project
        @param iterationid: Id of iteration
        @param file: name of document
        @return: translation content of document
        @raise UnAvaliableResourceException:
        @raise UnAuthorizedException: 
        """
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException, e:
                print "[ERROR] %s"%(e.msg)
        
        res, content = self.projects.restclient.request_get('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s/translations/%s'%(projectid, iterationid, file, lang), extension=extension)
        
        if res['status'] == '200' or res['status'] == '304':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
  
    def commit_translation(self, projectid, iterationid, fileid, localeid, resources, extension):
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException, e:
                print "[ERROR] %s"%(e.msg)
                sys.exit()

        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
        
        res, content = self.projects.restclient.request_put('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s/translations/%s'%(projectid,iterationid,fileid,localeid), args=resources, headers=headers, extension=extension)

        if res['status'] == '200':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', content)
      

