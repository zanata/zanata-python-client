# vim:set et sts=4 sw=4:
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
    "DocumentService",
)

from .service import Service


class DocumentService(Service):
    _fields = ['projects', 'base_url', 'http_headers']

    def __init__(self, *args, **kargs):
        super(DocumentService, self).__init__(*args, **kargs)

    def get_file_list(self, projectid, iterationid):
        res, content = self.projects.restclient.process_request('list_files', projectid, iterationid,
                                                                headers=self.http_headers)
        files = self.messages(res, content)
        filelist = [item.get('name') for item in files]
        return filelist

    def update_template(self, projectid, iterationid, file_id, resources, copytrans):
        ext = "?ext=gettext&ext=comment&copyTrans=%s" % copytrans
        res, content = self.projects.restclient.process_request('update_template', projectid, iterationid, file_id,
                                                                body=resources, headers=self.http_headers, extension=ext)
        return self.messages(res, content)

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
        ext = "?ext=gettext&ext=comment&copyTrans=%s" % copytrans
        res, content = self.projects.restclient.process_request('commit_template', projectid, iterationid,
                                                                body=resources, headers=self.http_headers, extension=ext)
        return self.messages(res, content)

    def delete_template(self, projectid, iterationid, file_id):
        res, content = self.projects.restclient.process_request('delete_template', projectid, iterationid, file_id,
                                                                headers=self.http_headers)
        return self.messages(res, content)

    def retrieve_template(self, projectid, iterationid, file_id):
        ext = "?ext=gettext&ext=comment"
        res, content = self.projects.restclient.process_request('retrieve_template', projectid, iterationid, file_id,
                                                                headers=self.http_headers, extension=ext)
        return self.messages(res, content)

    def retrieve_translation(self, lang, projectid, iterationid, file_id, skeletons):
        """
        Get translation content of file from Zanata server
        @param lang: language
        @param projectid: Id of project
        @param iterationid: Id of iteration
        @param file: name of document
        @return: translation content of document
        @raise UnAvaliableResourceException:
        @raise UnAuthorizedException:
        """
        ext = "?ext=gettext&ext=comment"
        if skeletons:
            ext = ext + "&skeletons=true"
        res, content = self.projects.restclient.process_request('retrieve_translation', projectid, iterationid, file_id, lang,
                                                                headers=self.http_headers, extension=ext)
        return self.messages(res, content)

    def commit_translation(self, projectid, iterationid, fileid, localeid, resources, merge):
        ext = "?ext=gettext&ext=comment&merge=%s" % merge
        res, content = self.projects.restclient.process_request('commit_translation', projectid, iterationid, fileid, localeid,
                                                                body=resources, headers=self.http_headers, extension=ext)
        return self.messages(res, content)
