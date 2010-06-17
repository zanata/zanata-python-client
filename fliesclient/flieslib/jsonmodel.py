#vim:set et sts=4 sw=4: 
# 
# Flies Python Client
#
# Copyright (c) 2010 Jian Ni <jni@gmail.com>
# Copyright (c) 2010 Red Hat, Inc.
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
        "BaseJsonModel",
   )

import json
from project import Project
from project import Iteration
from project import Links

class JsonParser():
    def __init__(self):
        self.jsoncontent = None
        self.pycontent = None
        #self.links = None
    '''
    def custom_decode(self, json_thread):
        print json_thread
        if 'type' in json_thread:
            if json_thread['type'] == 'application/vnd.flies.project+json':
                self.links =  Links(json_thread['href'], json_thread['type'], json_thread['rel'])
            elif json_thread['type'] == 'IterationProject':
                if 'description' in json_thread:
                    desc = json_thread['description']
                else:
                    desc = None
                return Project(json_thread['id'], json_thread['name'], desc = desc, type = json_thread['type'], links =
                self.links)
        else:
            return Iteration(json_thread['id'], json_thread['name'], json_thread['description'])
    '''
    def get_json(self):
        return self.jsoncontent

    def parse_json(self, content):
        self.pycontent = json.loads(content)
        return self.pycontent

    def create_json(self, pycontent):
        return json.JSONEncoder().encode(pycontent)


