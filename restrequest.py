__all__ = (
        "Connection",
    )  

import urlparse
import urllib
import base64
import warnings 

with warnings.catch_warnings():
     warnings.filterwarnings("ignore",category=DeprecationWarning)
     import httplib2
     
class Connection:
	def __init__(self, base_url, username, password):
		self.base_url = base_url
		self.username = username
		self.password = password
		self.url = urlparse.urlparse(base_url)

	def request_get(self, resource, args = None, body = None, headers = {}):
                return self.request(resource, "get", args, body, headers)

	def request_post(self, resource, args = None, body = None, headers = {}):
		return self.request(resource, "post", args, body, headers)
        
        def request_put(self, resource, args = None, body = None, headers = {}):
                return self.request(resource, "put", args, body, headers)

	def request(self, resource, method = "get", args = None, body = None, headers = {}):
		path = resource
                headers['Accept'] = 'application/json'       
                http = httplib2.Http('.cache')
                if args:
                   if method == "put" or method == "post":
                      headers['Content-Type'] = 'application/json'
                      body = urllib.urlencode(args)
                response, content = http.request("%s%s" % (self.base_url, resource), method.upper(), body=body, headers=headers)
		return (response, content.decode("UTF-8"))
  
