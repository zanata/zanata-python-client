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

all__ = (
            "PublicanUtilityTest",
        )
import os
import unittest
from fliesclient.publicanutil import PublicanUtility

class PublicanUtilityTest(unittest.TestCase):
    def setUp(self):
        self.publican = PublicanUtility()

    def test_strippath(self):
        filename, path = self.publican.strip_path("./pot/test.pot")
        self.assertEqual(filename, "test")
        self.assertEqual(path, "./pot/test.pot")
        
    def test_potfiletojson(self):
        body, filename = self.publican.potfile_to_json("./pot/test.pot")
        expect = """{"lang": "en-US", "extensions": [{"comment": "SOME DESCRIPTIVE TITLE.\\nCopyright (C) YEAR Free Software Foundation, Inc.\\nFIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\\n", "object-type": "po-header", "entries": [{"value": "PACKAGE VERSION", "key": "Project-Id-Version"}, {"value": "2001-02-09 01:25+0100", "key": "POT-Creation-Date"}, {"value": "YEAR-MO-DA HO:MI+ZONE", "key": "PO-Revision-Date"}, {"value": "FULL NAME <EMAIL@ADDRESS>", "key": "Last-Translator"}, {"value": "LANGUAGE <LL@li.org>", "key": "Language-Team"}, {"value": "1.0", "key": "MIME-Version"}, {"value": "application/x-xml2pot; charset=UTF-8", "key": "Content-Type"}, {"value": "ENCODING", "key": "Content-Transfer-Encoding"}]}], "contentType": "application/x-gettext", "name": "test", "textFlows": [{"lang": "en-US", "content": "<title>Access Control Lists</title>", "extensions": [{"object-type": "pot-entry-header", "references": ["Acls.xml:8"], "flags": ["no-c-format"], "context": "", "extractedComment": "Tag: title"}], "id": "782f49c4e93c32403ba0b51821b38b90", "revision": 1}]}"""
        self.assertEqual(expect, body)
        self.assertEqual(filename, "test")  

    def test_pofiletojson(self):
        body, filename = self.publican.pofile_to_json("./po/test.po")
        expect = """{"textFlowTargets": [{"content": "<title>\\u8bbf\\u95ee\\u5b58\\u53d6\\u63a7\\u5236\\u5217\\u8868</title>", "extensions": [{"object-type": "comment", "value": "testcomment", "space": "preserve"}], "state": "Approved", "resId": "782f49c4e93c32403ba0b51821b38b90"}], "extensions": [], "links": []}"""
        self.assertEqual(expect, body)
        self.assertEqual(filename, "test")
        
if __name__ == '__main__':
    unittest.main()

