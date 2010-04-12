import httplib
import urlparse
import urllib
import base64

class Connection:
	def __init__(self, base_url, username, password):
		self.base_url = base_url
		self.username = username
		self.password = password
		self.url = urlparse.urlparse(base_url)

	def request_get(self, resource, args = None):
		return self.request(resource, "get", args)

	def request_post(self, resource, args = None):
		return self.request(resource, "post", args)

	def request(self, resource, method = "get", args = None):
		params = None
		path = resource
		headers = {}

		if args:
			path += "?" + urllib.urlencode(args)

		if self.username and self.password:
			encoded = base64.encodestring("%s:%s" % (self.username, self.password))[:-1]
			headers["Authorization"] = "Basic %s" % encoded

		if (self.url.port == 443):
			conn = httplib.HTTPSConnection(self.url.netloc)
		else:
			conn = httplib.HTTPConnection(self.url.netloc)

		req = conn.request(method.upper(), "/" + path, None, headers)

		return conn.getresponse()
  
