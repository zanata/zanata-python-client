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

all__ = (
            "PublicanUtilityTest",
        )

import unittest
import sys, os
sys.path.insert(0, os.path.abspath(__file__+"/../.."))

from zanataclient.publicanutil import PublicanUtility


class PublicanUtilityTest(unittest.TestCase):
    def setUp(self):
        self.publican = PublicanUtility()

    def test_strippath(self):
        filename = self.publican.strip_path("./pot/test.pot", "./pot")
        self.assertEqual(filename, "test")
        
    def test_potfiletojson(self):
        body, filename = self.publican.potfile_to_json("./pot/test.pot", "./pot")
        expect = """{"lang": "en-US", "extensions": [{"comment": "SOME DESCRIPTIVE TITLE.\\nCopyright (C) YEAR Free Software Foundation, Inc.\\nFIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\\n", "object-type": "po-header", "entries": [{"value": "PACKAGE VERSION", "key": "Project-Id-Version"}, {"value": "2001-02-09 01:25+0100", "key": "POT-Creation-Date"}, {"value": "YEAR-MO-DA HO:MI+ZONE", "key": "PO-Revision-Date"}, {"value": "FULL NAME <EMAIL@ADDRESS>", "key": "Last-Translator"}, {"value": "LANGUAGE <LL@li.org>", "key": "Language-Team"}, {"value": "1.0", "key": "MIME-Version"}, {"value": "application/x-xml2pot; charset=UTF-8", "key": "Content-Type"}, {"value": "ENCODING", "key": "Content-Transfer-Encoding"}]}], "contentType": "application/x-gettext", "name": "test", "textFlows": [{"lang": "en-US", "content": "<title>Access Control Lists</title>", "extensions": [{"object-type": "comment", "value": "Tag: title", "space": "preserve"}, {"object-type": "pot-entry-header", "references": ["Acls.xml:8"], "flags": ["no-c-format"], "context": "", "extractedComment": ""}], "id": "782f49c4e93c32403ba0b51821b38b90", "revision": 1}]}"""
        self.assertEqual(expect, body)
        self.assertEqual(filename, "test")  

    def test_pofiletojson(self):
        body = self.publican.pofile_to_json("./po/test.po")
        expect = """{"textFlowTargets": [{"content": "<title>\\u8bbf\\u95ee\\u5b58\\u53d6\\u63a7\\u5236\\u5217\\u8868</title>", "extensions": [{"object-type": "comment", "value": "Tag: title", "space": "preserve"}], "state": "Approved", "resId": "782f49c4e93c32403ba0b51821b38b90"}], "extensions": [{"comment": "translation of Acls.po to Traditional Chinese\\ntranslation of Acls.po to\\nCopyright (C) 2003, 2007 Free Software Foundation, Inc.\\n\\nSarah Wang <sarahs@redhat.com>, 2003.\\nXi HUANG <xhuang@redhat.com>, 2007.\\nChester Cheng <ccheng@redhat.com>, 2007.", "object-type": "po-target-header", "entries": [{"value": "Acls", "key": "Project-Id-Version"}, {"value": "http://bugs.kde.org", "key": "Report-Msgid-Bugs-To"}, {"value": "2001-02-09 01:25+0100", "key": "POT-Creation-Date"}, {"value": "2007-07-11 14:49+1000", "key": "PO-Revision-Date"}, {"value": "Chester Cheng <ccheng@redhat.com>", "key": "Last-Translator"}, {"value": "Traditional Chinese <zh_TW@li.org>", "key": "Language-Team"}, {"value": "1.0", "key": "MIME-Version"}, {"value": "text/plain; charset=UTF-8", "key": "Content-Type"}, {"value": "8bit", "key": "Content-Transfer-Encoding"}, {"value": "KBabel 1.11.4", "key": "X-Generator"}]}], "links": []}"""
        self.assertEqual(expect, body)
                
if __name__ == '__main__':
    unittest.main()

