__all__ = (
        "Flies",
    )
import urlparse
import urllib
import exceptions 
from flieslib import Connection     
from flieslib.Exception import InvalidOptionException

class Flies:
	def __init__(self, base_url, username = None, apikey = None):
		self.base_url = base_url
		self.username = username
		self.apikey = apikey
                self.connection = Connection(base_url, None, None)
	
        def get_projects(self):
            return self.connection.request_get('/projects')

	def get_project_info(self, projectid):
            return self.connection.request_get('/projects/p/%s'%projectid)
        
        def get_iteration_info(self, projectid, iterationid):
            return self.connection.request_get('/projects/p/%s/iterations/i/%s'%(projectid,iterationid))

	def create_project(self, projectid, projectname, projectdesc):
	    error = 'Invalid Options'
            headers = {}
            headers['X-Auth-User'] = self.username
            headers['X-Auth-Token'] = self.apikey
            if projectname and projectdesc :
               body = '''{"name":"%s","id":"%s","description":"%s","type":"IterationProject"}'''%(projectname,projectid,projectdesc)
               res, content = self.connection.request_put('/projects/p/%s'%projectid, args=body, headers=headers)
               if res['status'] == '201': 
                  return True
               elif res['status'] == '404':
                  raise NoSuchProjectException('Error 404', 'No Such project')
            else:
               raise InvalidOptionException('Error','Invalid Options')
        def create_iteration(self, projectid, iterationid, iterationname, iterationdesc):
            headers = {}
            headers['X-Auth-User'] = self.username
            headers['X-Auth-Token'] = self.apikey
            if iterationname and iterationdesc :
               body = '''{"name":"%s","id":"%s","description":"%s"}'''%(iterationname, iterationid, iterationdesc)
               res, content = self.connection.request_put('/projects/p/%s/iterations/i/%s'%(projectid,iterationid), args=body, headers=headers)
               if res['status'] == '201':
                  return True
            else:
               raise Exception("Invalid Options")


