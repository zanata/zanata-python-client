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
        "BaseModel",
   )

import json

class BaseModel():
    def __init__(self, json = {}):
        self.json = json

    def to_json(self):
        return json.JSONEncoder().encode(self.json)

    @property
    def id(self):
        return self.json.get('id')

    @id.setter
    def id(self, id):
        self.json['id'] = id

    @property
    def name(self):
        return self.json.get('name')
    
    @name.setter
    def name(self, name):
        print "name"+name
        self.json['name'] = name

    @property
    def desc(self):
        return self.json.get('description')

    @desc.setter
    def desc(self, desc):
        self.json['description'] = desc

    @property
    def type(self):
        return self.json.get('type')

    @type.setter
    def type(self, type):
        self.json['type'] = type


