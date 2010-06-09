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
        "Project",
   )
import json
from jsonmodel import BaseJsonModel

class Project(BaseJsonModel):
    def __init__(self, id, name, type, desc, links = None, content = None):
        BaseJsonModel.__init__(self, content)
        self.id = id        
        self.name = name
        self.type = type
        self.desc = desc
        self.links = links
        
    
    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_desc(self):
        return self.desc

    def get_links(self):
        return self.links

    def convert_json(self):
        return json.loads(self.content)
        
