#vim:set et sts=4 sw=4: 
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
        "DocumentService",
   )

try:
    import json
except ImportError:
    import simplejson as json
from error import InternalServerError
from error import UnAuthorizedException
from error import BadRequestBodyException
from error import SameNameDocumentException
from error import UnAvaliableResourceException


class DocumentService:    
    def __init__(self, projects):
        self.projects = projects
    
    def get_file_list(self, projectid, iterationid):
        res, content = self.projects.restclient.request_get('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r'%(projectid, iterationid))
        
        if res['status'] == '200' or res['status'] == '304':
            files = json.loads(content)
            filelist = [item.get('name') for item in files]
            return filelist
        elif res['status'] == '500':
            raise InternalServerError('Error 500', 'An internal server error happens')
    
    def update_template(self, projectid, iterationid, file_id, resources, copytrans):
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
         
        res = self.projects.restclient.request_put('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s'%(projectid,iterationid,file_id), args=resources, headers=headers, copytrans=copytrans)
         
        if res['status'] == '201' or res['status'] == '200':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', 'Unable to read request body.')
        elif res['status'] == '409':
            raise SameNameDocumentException('Error 409', 'A document with same name already exists.')
    
    def commit_template(self, projectid, iterationid, resources, copytrans):
        """
        Push the json object to Zanata server
        @param projectid: id of project
        @param iterationid: id of iteration
        @param resources: json object of the content that want to commit to Zanata server
        @return: True
        @raise UnAuthorizedException:
        @raise BadRequestBodyException:
        @raise SameNameDocumentException:
        """
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
        
        res, content = self.projects.restclient.request_post('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r'%(projectid,iterationid), args=resources, headers=headers, copytrans=copytrans)
        
        if res['status'] == '201':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', content)
        elif res['status'] == '409':
            raise SameNameDocumentException('Error 409', content)

    def delete_template(self, projectid, iterationid, file_id):
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey    
       
        res, content = self.projects.restclient.request_delete('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s'%(projectid, iterationid, file_id), headers=headers)
         
        if res['status'] == '200' or res['status'] == '304':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey') 
    
    def retrieve_template(self, projectid, iterationid, file_id):
        res, content = self.projects.restclient.request_get('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s'%(projectid, iterationid, file_id))
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey 
        
        if res['status'] == '200' or res['status'] == '304':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')       

    def retrieve_translation(self, lang, projectid, iterationid, file_id):
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
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey 

        res, content = self.projects.restclient.request_get('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s/translations/%s'%(projectid, iterationid, file_id, lang))
                
        if res['status'] == '200' or res['status'] == '304':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', content)
  
    def commit_translation(self, projectid, iterationid, fileid, localeid, resources, merge):
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
        
        res, content = self.projects.restclient.request_put('/seam/resource/restv1/projects/p/%s/iterations/i/%s/r/%s/translations/%s'%(projectid,iterationid,fileid,localeid), args=resources, headers=headers, merge=merge)

        if res['status'] == '200':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', content)
      

