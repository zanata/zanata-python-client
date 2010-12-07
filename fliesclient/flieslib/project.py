#vim:set et sts=4 sw=4: 
# 
# Flies Python Client
#
# Copyright (c) 2010 Jian Ni <jni@redhat.com>
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
try:
    import json
except ImportError:
    import simplejson as json


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
                setattr(self, str(a), [Link(item) for item in b])

    def set_iteration(self, iterations):
        self.__iterations = iterations

    def get_iteration(self, id):
        return self.__iterations.get(self.id, id)



