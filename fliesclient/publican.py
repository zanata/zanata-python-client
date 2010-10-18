# vim:set et sts=4 sw=4: 
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
            "Publican",
          )

import polib
import hashlib

class Publican:
    def __init__(self, filepath):
        self.path = filepath
	
    def get_potheader(self, entry):
        extracted_comment = entry.comment
        
    def covert_txtflow(self):
        """
        Convert the content of the pot file to a list of text flow.
        @return: the dictionary object of textflow
        """
        po = polib.pofile(self.path)
        textflows = []
        for entry in po:
            m = hashlib.md5()
            m.update(entry.msgid.encode('utf-8'))
            textflowId = m.hexdigest() 
            
            textflow = {'id': textflowId, 'lang':'en', 'content':entry.msgid, 'extensions':}
            textflows.append(textflow)
        return textflows
    
    def covert_txtflowtarget(self):
        """
        Convert the content of the po file to a list of text flow.
        @return: the dictionary object of textflow
        """
        po = polib.pofile(self.path)
        textflowtargets = []
        """
        "resId", "state", "translator", "content", "extensions" 
        """
        for entry in po:
            m = hashlib.md5()
            m.update(entry.msgid.encode('utf-8'))
            textflowId = m.hexdigest()
            if entry.msgstr:
                state = 3
            else:
                state = 1
            textflowtarget = {'resId': textflowId, 'state': state, 'content':entry.msgstr, 'extensions':[]}
            textflowtargets.append(textflowtarget)
        return textflowtargets

    def extract_potheader(self):
        pass
        
    def load_po(self):
        """
        Convert the po file to a pofile object in polib.
        @return: pofile object
        """
        return polib.pofile(self.path)
        
