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
    def __init__(self, href = None, type = None, rel = None):
        self.__href = href
        self.__type = type
        self.__rel = rel

    def get_href(self):
        return self.__href

    def get_type(self):
        return self.__type

    def get_rel(self):
        return self.__rel
    
    href = property(get_href)
    type = property(get_type)
    rel = property(get_rel)


class Iteration():
    def __init__(self, id = None, name = None, desc = None):
        self.__id = id
        self.__name = name
        self.__desc = desc
    
    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_desc(self):
        return self.__desc

    id = property(get_id)
    name = property(get_name)
    desc = property(get_desc)

class Project():
    def __init__(self, id = None, name = None, desc = None, type = None, links = None):
        self.__id = id
        self.__name = name
        self.__desc = desc
        self.__type = type
        self.__links = links
 
    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__type

    def get_desc(self):
        return self.__desc

    def get_links(self):
        return self.__links
    
    id = property(get_id, set_id)
    name = property(get_name)
    type = property(get_type)
    desc = property(get_desc)
    links = property(get_links)
