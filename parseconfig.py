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
