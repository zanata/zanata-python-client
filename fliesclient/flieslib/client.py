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
import rest.client
from publican import Publican

class FliesClient(rest.client.RestClient):
    def __init__(self, base_url, username = None, apikey = None):
		self.base_url = base_url
		self.username = username
		self.apikey = apikey
       	
    def ListProjects(self):
            return rest.client.RestClient.Get(self,'/projects')
    
    def GetProjectInfo(self, projectid):
            return rest.client.RestClient.Get(self,'/projects/p/%s'%projectid)
        
    def GetIterationInfo(self, projectid, iterationid):
            return rest.client.RestClient.Get(self,'/projects/p/%s/iterations/i/%s'%(projectid,iterationid))

    def CreateProject(self, projectid, projectname, projectdesc):
            error = 'Invalid Options'
            headers = {}
            headers['X-Auth-User'] = self.username
            headers['X-Auth-Token'] = self.apikey
            if projectname and projectdesc :
               body = '''{"name":"%s","id":"%s","description":"%s","type":"IterationProject"}'''%(projectname,projectid,projectdesc)
               res, content = rest.client.RestClient.Put(self,'/projects/p/%s'%projectid, args=body, headers=headers)
               if res['status'] == '201': 
                  return True
               elif res['status'] == '404':
                  raise NoSuchProjectException('Error 404', 'No Such project')
            else:
               raise InvalidOptionException('Error','Invalid Options')
        
    def CreateIteration(self, projectid, iterationid, iterationname, iterationdesc):
            headers = {}
            headers['X-Auth-User'] = self.username
            headers['X-Auth-Token'] = self.apikey
            if iterationname and iterationdesc :
               body = '''{"name":"%s","id":"%s","description":"%s"}'''%(iterationname, iterationid, iterationdesc)
               res, content = rest.client.RestClient.Put(self,'/projects/p/%s/iterations/i/%s'%(projectid,iterationid), args=body, headers=headers)
               if res['status'] == '201':
                  return True
               elif res['status'] == '404':
                  raise NoSuchProjectException('Error 404', 'No Such project')
            else:
               raise InvalidOptionException('Error', 'Invalid Options')
    
    def PushPublican(self):
        publican = Publican("/home/jni/Deployment_Guide/pot/Email.pot") 
        content = publican.read_po()
        print content    
        
    def PullPublican():
        pass    


