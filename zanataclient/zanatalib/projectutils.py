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
    "Project", "Iteration", "Stats"
)


class Link(object):
    def __init__(self, dict):
        for a, b in dict.items():
            setattr(self, str(a), b)


class Iteration(object):
    def __init__(self, dict):
        for a, b in dict.items():
            setattr(self, str(a), b)


class Project(object):
    def __init__(self, d):
        for a, b in d.items():
            if not a == 'links':
                setattr(self, str(a), b)
            else:
                if b is not None:
                    setattr(self, str(a), [Link(item) for item in b])

    def set_iteration(self, iterations):
        self.__iterations = iterations

    def get_iteration(self, version_id):
        project_id = getattr(self, 'id')
        return self.__iterations.get(project_id, version_id)


class Stats(object):
    def __init__(self, stats):
        self.stats_dict = stats

    def _get_doc_trans_percent(self, doc_name, stats_dict):
        trans_percent = {}
        for stat in stats_dict:
            if stat.get('locale'):
                trans_percent.update({
                    stat['locale']: int((float(stat.get('translated', 0) * 100) /
                                         float(stat.get('total', 0))))
                })
        return {doc_name: trans_percent}

    @property
    def stats_id(self):
        return self.stats_dict.get('id')

    @property
    def trans_stats_dict(self):
        return self.stats_dict.get('stats')

    @property
    def trans_percent_dict(self):
        trans_percent = {}
        detailed_stats = self.stats_dict.get('detailedStats')
        if isinstance(detailed_stats, list):
            for doc in detailed_stats:
                if isinstance(doc, dict) and doc.get('id') and doc.get('stats'):
                    trans_percent.update(self._get_doc_trans_percent(doc['id'], doc['stats']))
        return trans_percent

    @property
    def trans_stats_detail_dict(self):
        trans_dict = {}
        detailed_stats = self.stats_dict.get('detailedStats')
        if isinstance(detailed_stats, list):
            for doc in detailed_stats:
                if isinstance(doc, dict) and doc.get('id') and doc.get('stats'):
                    trans_dict.update({doc['id']: doc['stats']})
        return trans_dict
