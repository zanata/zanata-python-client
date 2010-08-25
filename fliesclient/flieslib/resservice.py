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
        "ResourceService",
   )

import os
import json
import hashlib
import polib
import shutil
import sys
from rest.client import RestClient
from error import *

class ResourceService:    
    def __init__(self, projects):
        self.projects = projects
    
    def hash_matches(self, message, id):
        m = hashlib.md5()
        m.update(message.msgid)
        if m.hexdigest() == id:
            return True
        else:
            return False

    def get_file_list(self, projectid, iterationid):
        res, content = self.projects.restclient.request_get('/projects/p/%s/iterations/i/%s/r'%(projectid, iterationid))
        
        if res['status'] == '200':
            list = json.loads(content)
            filelist = [file.get('name') for file in list]
            return filelist
                     
    def commit_translation(self, projectid, iterationid, resources):
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException as e:
                print "%s :%s"%(e.expr, e.msg)
                sys.exit()

        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
        
        res, content = self.projects.restclient.request_post('/projects/p/%s/iterations/i/%s/r'%(projectid,iterationid), args=resources, headers=headers)

        if res['status'] == '201':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', 'Unable to read request body.')
        elif res['status'] == '409':
            raise SameNameDocumentException('Error 409', 'A document with same name already exists.')
                
    def retrieve_translation(self, lang, projectid, iterationid, file):
        """
        Get translation content of file from Flies server
        Args: 
            projectid: Id of project
            iterationid: Id of iteration
            filename: name of PO file
            lang: language
        Returns:
            content: translation content
        Raises:
            UnAvaliableResourceException, UnAuthorizedException 
        """
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException as e:
                print "%s :%s"%(e.expr, e.msg)

        
        res, content = self.projects.restclient.request_get('/projects/p/%s/iterations/i/%s/r/%s/translations/%s'%(projectid, iterationid, file, lang))

        if res['status'] == '200':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
  
    def update_translation(self, projectid, iterationid):
        pass            

