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
        "Project","Iteration" 
   )
import json
from jsonmodel import BaseModel

class Links():
    def __init__(self, json):
        self.json = json

    @property
    def href(self):
        return self.json.get('href')
    
    @href.setter
    def href(self, href):
        self.json['href'] = href
    
    @property
    def type(self):
        return self.json.get('type')

    @type.setter
    def type(self, type):
        self.json['type'] = type

    @property
    def rel(self):
        return self.json.get('rel')

    @rel.setter
    def rel(self, rel):
        self.json['rel'] = rel
    
class Iteration(BaseModel):
    def __init__(self, json = {}):
        BaseModel.__init__(self, json)

class Project(BaseModel):
    def __init__(self, json = {}, id = None, name = None, desc = None, iterations = None):
        BaseModel.__init__(self, json)
        self.__iterations = iterations
        if not json:
            self.json['id'] = id
            self.json['name'] = name
            self.json['description'] = desc
    
    @property
    def links(self):
        links = []
        for cont in self.json.get('links'):
            iter = Links(cont)
            links.append(iter)
        return links
    
    @links.setter
    def links(self,links):
        self.json['links'] = links

    def get_iteration(self, id):
        return self.__iterations.get(self.id, id)
