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
        "FliesConfig",
    )

import ConfigParser
import os.path

class FliesConfig:
     def __init__(self, path):
    	 userconfig = path+"/.config/flies.ini"
         print userconfig
         self.configparser = ConfigParser.ConfigParser()
         self._config = self.configparser.read([userconfig, os.path.expanduser(userconfig)])
         
     def get_value(self, name, section):
         server_value = self.configparser.get(section, 'server')
         
         if self._config:
            try:
                value = self.configparser.get('servers', server_value+'.'+name)
                return value
            except ConfigParser.NoOptionError, NoSectionError:
                return None
         else:
            return None
     
     def get_config_value(self, name):
         return self.get_value(name, 'defaults') 
