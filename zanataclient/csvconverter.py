# vim:set et sts=4 sw=4:
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
    "CSVConverter",
)

import csv
import sys
from os.path import expanduser

try:
    import json
except ImportError:
    import simplejson as json

from .zanatalib.logger import Logger


class CSVConverter:
    def __init__(self):
        self.log = Logger()

    def read_data(self, csv_file):
        data = []
        try:
            reader = csv.reader(open(csv_file, 'rb'))
            header = reader.next()
            size = len(header)
            for line in reader:
                items = {}
                entry_size = len(line)
                for x in range(size):
                    if x < entry_size:
                        item = {header[x]: line[x]}
                    else:
                        item = {header[x]: ""}
                    items.update(item)

            data.append(items)
        except IOError:
            self.log.error("Can not find csv file: %s" % csv_file)

        return data

    def read_csv_file(self, csv_file):
        data = []
        try:
            reader = csv.reader(open(csv_file, 'rb'))
            data = [line for line in reader]
        except IOError:
            self.log.error("Can not find csv file: %s" % csv_file)
        return data

    def convert_to_json(self, filepath, locale_map, comments_header):
        data = self.read_csv_file(expanduser(filepath))
        srclocales = []
        # srclocales.append('en-US')
        entries = []
        targetlocales = []
        csv_locales = []
        comments = []
        for index, item in enumerate(data):
            terms = []
            if index == 0:
                # Assuming last two names refers to column names,for example consider following csv file
                # en-US,es,ko,ru,pos,description
                # Hello,Hola,test,111,noun,Greeting
                # first line always contains locales and last two specifies column names
                comments = [comm for comm in item[-2:]]
                csv_locales = [lc for lc in item[:-2]]
                continue
            else:
                glossary_len = len(item)
                csv_locales_len = len(csv_locales)
                comments_len = len(comments)
                if glossary_len != csv_locales_len + comments_len:
                    print("Wrong entries in csv file, please check your csv file")
                    print("Entry in csv file", item)
                    sys.exit(1)
                glossary_comments = item[-2:]
                for j in range(csv_locales_len):
                    if j == 0:
                        term = {'locale': csv_locales[j], 'content': item[j], 'comments': glossary_comments}
                    else:
                        term = {'locale': csv_locales[j], 'content': item[j], 'comments': []}
                    terms.append(term)
            entry = {'srcLang': 'en-US', 'glossaryTerms': terms}
            entries.append(entry)

        glossary = {'sourceLocales': srclocales, 'glossaryEntries': entries, 'targetLocales': targetlocales}
        # glossary = {'source-locales':srclocales, 'glossary-entries':entries, 'target-locales':targetlocales}
        return json.dumps(glossary)

if __name__ == "__main__":
    converter = CSVConverter()
    converter.convert_to_json("~/Downloads/test_data.csv", {'es': 'es-ES'}, ["description", "pos"])
