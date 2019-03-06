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
    "Project", "Iteration", "Stats", "ToolBox", "FileMappingRule"
)

import fnmatch
import os
import sys
from xml.etree import cElementTree as ET

from lxml import etree


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
                    stat['locale']: int((float(stat.get('translated', 0) * 100) // float(stat.get('total', 0))))
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


class ToolBox(object):
    """
    Various Useful Utilities
    """
    XMLNS = "http://zanata.org/namespace/config/"

    @staticmethod
    def xmlstring2dict(xmlstring):
        """
        Converts xmlstring to python dict
        :param xmlstring:
        :return: dict
        """
        tree = ET.fromstring(xmlstring)
        xmldict = {}
        for child in tree:
            xmldict[child.tag.split("}")[1]] = child.text
        return xmldict

    @staticmethod
    def populate_etree(element, data):
        """
        Populates an etree with the given dictionary
        """
        if not isinstance(data, dict):
            raise AttributeError('Unexpected Dict Structure')
        for k, v in data.items():
            if isinstance(v, dict):
                # child dictionary
                child = etree.Element(k)
                ToolBox.populate_etree(child, v)
                element.append(child)
            elif isinstance(v, list) or isinstance(v, tuple):
                # child list or tuple of dictionaries
                for item in v:
                    child = etree.Element(k)
                    ToolBox.populate_etree(child, item)
                    element.append(child)
            elif k.lower() == 'text':
                # set text
                element.text = v
            else:
                # set attribute
                element.set(k, str(v))

    @staticmethod
    def dict2xml(root_elem, dict_object):
        """
        Converts dict of key/value pairs into XML
        """
        root = etree.Element(root_elem, xmlns=ToolBox.XMLNS)
        ToolBox.populate_etree(root, dict_object)

        return etree.tostring(
            root, pretty_print=True, xml_declaration=True,
            encoding='UTF-8', standalone=True
        )


class FileMappingRule(object):
    """
    Build translation's paths for pull and push considering rules

    The mapping rules configuration is optional in zanata.xml.
    If not specified, standard rules are applied according to project type.
    """

    project_filemapping_default_config = {
        'gettext': '{path}/{locale_with_underscore}.{extension}',
        'podir': '{locale}/{path}/{filename}.{extension}',
        'properties': '{path}/{filename}_{locale_with_underscore}.{extension}',
        'utf8properties': '{path}/{filename}_{locale_with_underscore}.{extension}',
        'xliff': '{path}/{filename}_{locale_with_underscore}.{extension}',
        'xml': '{path}/{filename}_{locale_with_underscore}.{extension}',
        'file': '{locale}/{path}/{filename}.{extension}'
    }

    def __init__(self, *args, **kwargs):
        self.project_type, self.locale, self.extension, self.mapping_rules = args
        self.path = kwargs.get('path')
        self.filename = kwargs.get('filename')
        self.locale_with_underscore = self.locale.replace('-', '_')
        self.translation_folder = kwargs.get('trans_folder')
        self.remote_filepath = kwargs.get('remote_filepath')
        self.template_extension = 'pot'

    def _process_map_path(self, map_path):
        if self.translation_folder:
            if os.path.isabs(map_path):
                map_path = map_path[1:]
            map_path = os.path.join(self.translation_folder, map_path)
        if '//' in map_path:
            map_path = map_path.replace('//', '/')
        return map_path

    def _apply_standard_mapping_rules(self):
        if self.project_type in self.project_filemapping_default_config:
            map_path = self.project_filemapping_default_config[self.project_type]
            map_path = map_path.format(
                path=self.path, locale=self.locale,
                locale_with_underscore=self.locale_with_underscore,
                filename=self.filename, extension=self.extension
            )
            return self._process_map_path(map_path)
        else:
            print("Unsupported Project Type.")
            sys.exit(1)

    def _get_custom_mapping_rule(self):
        if self.mapping_rules and len(self.mapping_rules) > 0:
            for pattern, rule in self.mapping_rules.items():
                if '/' in pattern and '/' not in self.remote_filepath:
                    self.remote_filepath = '/' + self.remote_filepath
                if pattern == rule or fnmatch.fnmatch(
                        self.remote_filepath,
                        pattern.rstrip('.%s' % self.template_extension)
                ):
                    return rule
        return False

    def _apply_custom_mapping_rules(self):
        map_path = self._get_custom_mapping_rule()
        map_path = map_path.format(
            path=self.path, locale=self.locale,
            locale_with_underscore=self.locale_with_underscore,
            filename=self.filename, extension=self.extension
        )
        return self._process_map_path(map_path)

    @property
    def translation_path(self):
        translation_path = (
            self._apply_standard_mapping_rules()
            if not self.mapping_rules else
            self._apply_custom_mapping_rules()
        )
        return translation_path
