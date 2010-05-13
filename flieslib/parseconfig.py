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
        "FliesConfig",
    )

import ConfigParser
import os.path

class FliesConfig:
     def __init__(self):
    	 projectconfig = "./.fliesrc"
         userconfig = "~/.fliesrc"
         self.configparser = ConfigParser.ConfigParser()
         self._config = self.configparser.read([projectconfig, os.path.expanduser(userconfig)])
        
     def get_value(self, name, section, default_value = None):
         if self._config:
            try:
            	value = self.configparser.get(section, name)
                return value
            except ConfigParser.NoOptionError, NoSectionError:
                return default_value
         else:
            return default_value
     
     def get_config_value(self, name, default_value = None):
         return self.get_value(name, 'Config', default_value) 
