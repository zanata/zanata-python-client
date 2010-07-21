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
        "NoSuchProjectException", "InvalidOptionException", 
        "NoSuchFileException", "InvalidPOTFileException",
        "UnAuthorizedException", "BadRequestException",
        "ProjectExistException", "UnAvaliableResourceException",
        "UnAvaliablePOTException"
)

class NoSuchProjectException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class InvalidOptionException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class NoSuchFileException(Exception):
    def __init__(self, expr, msg):
       	self.expr = expr
       	self.msg = msg

class InvalidPOTFileException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class UnAuthorizedException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class UnAvaliablePOTException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class UnAvaliableResourceException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class BadRequestException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class ProjectExistException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
