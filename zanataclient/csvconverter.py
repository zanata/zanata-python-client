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
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

__all__ = (
            "CSVConverter",
          )

import polib
import hashlib
import os

try:
    import json
except ImportError:
    import simplejson as json
import sys

from zanatalib.logger import Logger


class CSVConverter:
    def __init__(self):
        self.log = Logger()
    
    def read_data(self, csv_file):
        data = []
        try:
            content = open(csv_file, 'r')
            headers = content.readline().rstrip()
            header = headers.split(',')
            size = len(header)               
            for line in content:
                items = {}
                entries = line.split(',', size-1)
                entry_size = len(entries)                
                for x in range(size):  
                    if x < entry_size:  
                        item = {header[x]: entries[x]}
                    else:
                        item = {header[x]: ""}
                    items.update(item)
            
                data.append(items)
        except IOError:
            self.log.error("Can not find csv file: %s"%csv_file)
        
        return data

    def convert_to_json(self, filepath, locale_map, comments_header):
        data = self.read_data(filepath)
        srclocales = []
        srclocales.append('en-US')
        entries = []
        targetlocales = []
        for item in data:
            comments = []
            terms = []

            for header in comments_header:
                if item.has_key(header):                
                    comments.append(item.pop(header))
            
            for key in item.keys():
                if key == 'en':
                    term = {'locale':'en-US', 'content':item[key], 'comments':comments}
                else:
                    if key in locale_map:
                        locale = locale_map[key]
                    else:
                        locale = key
                    term = {'locale':locale, 'content':item[key], 'comments':[]}
                    if key not in targetlocales:
                        targetlocales.append(key)
                terms.append(term)

            entry= {'srcLang':'en-US','glossaryTerms':terms, 'sourcereference':''}
            entries.append(entry)

        glossary = {'sourceLocales':srclocales, 'glossaryEntries':entries, 'targetLocales':targetlocales}

        return json.dumps(glossary)
    
if __name__ == "__main__":
    converter = CSVConverter()        
    converter.convert_to_json("/home/jamesni/Downloads/test_data.csv", {'es':'es-ES'}, ["description", "pos"])
