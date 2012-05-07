#vim:set et sts=4 sw=4: 
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
        "Project","Iteration" 
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
                setattr(self, str(a), [Link(item) for item in b])

    def set_iteration(self, iterations):
        self.__iterations = iterations

    def get_iteration(self, version_id):
        project_id = getattr(self, 'id')
        return self.__iterations.get(project_id, version_id)
