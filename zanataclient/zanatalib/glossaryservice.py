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
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.


__all__ = (
        "GlossaryService",
   )

from rest.client import RestClient
from service import Service 

class GlossaryService(Service):
    def __init__(self, base_url):
        self.restclient = RestClient(base_url)

    def commit_glossary(self, username, apikey, resources):
        headers = {}
        headers['X-Auth-User'] = username
        headers['X-Auth-Token'] = apikey

        headers['Accept'] = 'application/vnd.zanata.glossary+json'

        res, content = self.restclient.request_put('/seam/resource/restv1/glossary', args=resources, headers=headers)

        res, content = self.restclient.request_put('/seam/resource/restv1/glossary',
                                                   args=resources, 
                                                   headers=headers)
        return self.messages(res,content)


    def delete(self, username, apikey, lang = None):
        headers = {}
        headers['X-Auth-User'] = username
        headers['X-Auth-Token'] = apikey
        resource = '/seam/resource/restv1/glossary'

        if lang:
            resource =  resource + '/'+lang

        res, content = self.restclient.request_delete(resource, headers=headers)
        return self.messages(res,content)



 
