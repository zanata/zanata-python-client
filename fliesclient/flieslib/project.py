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

class Links():
    def __init__(self):
        self.__href = None
        self.__type = None
        self.__rel = None

    def get_href(self):
        return self.__href

    def set_href(self, href):
        self.__href = href
    
    def get_type(self):
        return self.__type

    def set_type(self, type):
        self.__type = type

    def get_rel(self):
        return self.__rel

    def set_rel(self, rel):
        self.__rel = rel
    
    href = property(get_href, set_href)
    type = property(get_type, set_type)
    rel = property(get_rel, set_rel)

    def get_property(self, content, property):
        if property in content:
            return content.get(property)        
        else:
            return None

class Iteration():
    def __init__(self):
        self.__id = None
        self.__name = None
        self.__desc = None
    
    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_desc(self):
        return self.__desc

    def set_desc(self, desc):
        self.__desc = desc

    id = property(get_id, set_id)
    name = property(get_name, set_name)
    desc = property(get_desc, set_desc)

    def get_property(self, content, property):
        if property in content:
            return content.get(property)
        else:
            return None

class Project(object):
    def __init__(self):
        self.__id = None
        self.__name = None
        self.__desc = None
        self.__type = None
        self.__links = None
 
    def get_id(self):
        return self.__id
    
    def set_id(self, id):
        self.__id = id

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_desc(self):
        return self.__desc

    def set_desc(self, desc):
        self.__desc = desc

    def get_type(self):
        return self.__type

    def set_type(self, type):
        self.__type = type

    def get_links(self):
        return self.__links

    def set_links(self,links):
        self.__links = links

    def get_property(self, content, property):
        if property in content:
            if 'links' == property:
                links = []
                for cont in content.get('links'):
                    iter = Links()
                    iter.href = iter.get_property(cont, 'href')
                    iter.type = iter.get_property(cont, 'type')
                    iter.rel = iter.get_property(cont, 'rel')
                    links.append(iter)
                return links
            else:
                return content.get(property)        
        else:
            return None
   
    id = property(get_id, set_id)
    name = property(get_name, set_name)
    type = property(get_type, set_type)
    desc = property(get_desc, set_desc)
    links = property(get_links, set_links)
