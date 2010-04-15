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

	def request_get(self, resource, args = None, headers = {}):
                return self.request(resource, "get", args, headers)

	def request_post(self, resource, args = None, headers = {}):
		return self.request(resource, "post", args, headers)

	def request(self, resource, method = "get", args = None, headers = {}):
		params = None
		path = resource
		if args:
			path += "?" + urllib.urlencode(args)

		#if self.username and self.password:
		#	encoded = base64.b64encode("%s:%s" % (self.username, self.password))
		#        headers["Authorization"] = "Basic %s" % encoded
                                
                http = httplib2.Http()
		response, content = http.request("%s%s" % (self.base_url, resource), method.upper(), None, headers)
		return (response, content.decode("UTF-8"))
  
