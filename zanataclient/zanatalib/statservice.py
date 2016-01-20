# vim:set et sts=4 sw=4:
#
# Zanata Python Client
#
# Copyright (c) 2015 Sundeep Anand <suanand@redhat.com>
# Copyright (c) 2015 Red Hat, Inc.
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
    "StatService",
)

from .service import Service


class StatService(Service):
    _fields = ['base_url', 'http_headers']

    def __init__(self, *args, **kargs):
        super(StatService, self).__init__(*args, **kargs)

    def disable_ssl_cert_validation(self):
        self.restclient.disable_ssl_cert_validation()

    def _append_locales(self, ext, locales):
        for locale in locales:
            ext += '&locale=%s' % locale
        return ext

    def get_project_stats(
            self, project_id, project_version, word=False, locales=None
    ):
        ext = "?detail=true&word=true" if word else "?detail=true&word=false"
        if isinstance(locales, list) and len(locales) > 0:
            ext = self._append_locales(ext, locales)
        res, content = self.restclient.process_request(
            'proj_trans_stats', project_id, project_version,
            headers=self.http_headers, extension=ext
        )
        return self.messages(res, content)

    def get_doc_stats(
            self, project_id, project_version, doc_id, word=False, locales=None
    ):
        ext = "?detail=true&word=true" if word else "?detail=true&word=false"
        if isinstance(locales, list) and len(locales) > 0:
            ext = self._append_locales(ext, locales)
        res, content = self.restclient.process_request(
            'doc_trans_stats', project_id, project_version, doc_id,
            headers=self.http_headers, extension=ext
        )
        return self.messages(res, content)
