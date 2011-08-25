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
        "GlossaryService",
   )

try:
    import json
except ImportError:
    import simplejson as json
from rest.client import RestClient
from error import UnAuthorizedException
from error import BadRequestBodyException
from error import UnavailableServiceError
from error import UnexpectedStatusException   

class GlossaryService:
    def __init__(self, base_url):
        self.restclient = RestClient(base_url)

    def commit_glossary(self, username, apikey, resources):
        headers = {}
        headers['X-Auth-User'] = username
        headers['X-Auth-Token'] = apikey        
        
        res, content = self.restclient.request_put('/seam/resource/restv1/glossary', args=resources, headers=headers)
       
        if res['status'] == '201':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'This operation is not authorized, please check username and apikey')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', content)
        elif res['status'] == '503':
            raise UnavailableServiceError('Error 503', 'Service Temporarily Unavailable')
        else:
            raise UnexpectedStatusException('Error', 'Unexpected Status, failed to push')
