__all__ = (
        "Flies",
    )
import urlparse
import urllib  
from restrequest import Connection     

class Flies:
	def __init__(self, base_url, username, password):
		self.base_url = base_url
		self.username = username
		self.password = password
                self.connection = Connection(base_url, None, None)
	
        def get_projects(self):
            return self.connection.request_get('/projects')

	def get_project_info(self, projectid):
            return self.connection.request_get('/projects/p/%s'%projectid)
        
        def get_iteration_info(self, projectid, iterationid):
            return self.connection.request_get('/projects/p/%s/iterations/i/%s'%(projectid,iterationid))

	def create_project(self, username, password, projectid, projectname, projectdesc):
	    if projectname and desc :
               body = '''{"name":"%s","id":"%s","description":"%s","type":"IterationProject"}'''%(projectname,projectid,projectdesc)
               res, content = self.connection.request_put('/projects/p/%s'%projectid, args=body, headers=headers)
               print 'Status: '+res['status']
            else:
               print "Please provide valid options: '--name=project_name --description=project_description'"
        
       # def create_iteration():

