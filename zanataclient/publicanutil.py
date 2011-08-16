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
            "PublicanUtility",
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

class PublicanUtility:
    def __init__(self):
        self.log = Logger()

    def create_txtflow(self, pofile):
        """
        Convert the content of the pot file to a list of text flow.
        @return: the dictionary object of textflow
        """
        textflows = []
        for entry in pofile:
            reflist = []
            if entry.msgctxt:
                self.log.warn("encountered msgctxt; not currently supported")
            m = hashlib.md5()
            m.update(entry.msgid.encode('utf-8'))
            textflowId = m.hexdigest()
            """
            "extensions":[{"object-type":"pot-entry-header","context":"context",
            "references":["fff"],"extractedComment":"extractedComment",
            "flags":["java-format"]}]
            """
            extracted_comment = entry.comment
            references = entry.occurrences
            for ref in references:
                node = ref[0]+":"+ref[1]
                reflist.append(node)
            flags = entry.flags
            
            #extensions_single_comment = [{'object-type':'comment','value':'test','space':'preserve'}]
            #extensions_pot_entry_header = [{"object-type":"pot-entry-header","context":"context","references":["fff"],"extractedComment":"extractedComment","flags":["java-format"]}]

            extensions=[{'object-type':'comment','value':extracted_comment,'space':'preserve'}, {"object-type":"pot-entry-header","context":"","references":reflist,"extractedComment":'',"flags":flags}]

            textflow = {'id': textflowId, 'lang':'en-US', 'content':entry.msgid, 'extensions':extensions, 'revision':1}
            textflows.append(textflow)
        return textflows
    
    def create_txtflowtarget(self, pofile):
        """
        Convert the content of the po file to a list of textflowtarget.
        @return: the dictionary object of textflow
        """
        obs_list=pofile.obsolete_entries()
        textflowtargets = []
        
        for entry in pofile:
            if entry in obs_list:
                continue
            m = hashlib.md5()
            m.update(entry.msgid.encode('utf-8'))
            textflowId = m.hexdigest()
            comment = entry.comment
            
            if entry.msgstr:
                state = "Approved"
            else:
                state = "New"
            #need judge for fuzzy state
            if "fuzzy" in entry.flags:
                state = "NeedReview"
            
            #create extensions
            extensions = [{"object-type":"comment","value":comment,"space":"preserve"}]
            
            # {"resId":"782f49c4e93c32403ba0b51821b38b90","state":"Approved","translator":{"email":"id","name":"name"},"content":"title:
            # ttff","extensions":[{"object-type":"comment","value":"testcomment","space":"preserve"}]}
            # Diable the translator to avoid issues on server side
            textflowtarget = {'resId': textflowId, 'state': state, 'content':entry.msgstr,'extensions':extensions}
            
            #Temporary fill in the admin info for translator to pass the validation, waiting for server side change
            textflowtargets.append(textflowtarget)
        
        return textflowtargets

    def create_extensions(self, pofile, object_type):
        """
        "extensions":[{"object-type":"po-header","comment":"comment_value", "entries":[{"key":"h1","value":"v1"}]}]
        "extensions":[{"object-type":"po-target-header", "comment":"comment_value", "entries":[{"key":"ht","value":"vt1"}]}]
        """
        entries = []
        metadatas = pofile.ordered_metadata()
        for item in metadatas:
            entry = {"key":item[0], "value":item[1]}
            entries.append(entry)
       
        extensions = [{"object-type":object_type,"comment":pofile.header, "entries":entries}]
        return extensions

    def create_pofile(self, path):
        """
        Convert the po file to a pofile object in polib.
        @return: pofile object
        """
        try:
            po = polib.pofile(path)
        except Exception:
            self.log.error("Can not processing the po file")
            sys.exit()

        return po

    def get_file_list(self, path, file_type):
        final_file_list = []
        root_list = os.listdir(path)
        for item in root_list:
            if item == '.svn':
                continue
            full_path = os.path.join(path, item)
            if full_path.endswith(file_type):
                final_file_list.append(full_path)
            if os.path.isdir(full_path):
                final_file_list+=self.get_file_list(full_path, file_type)

        return final_file_list

    def hash_match(self, message, msgid):
        m = hashlib.md5()
        m.update(message.msgid.encode('utf-8'))
        if m.hexdigest() == msgid:
            return True
        else:
            return False 

    def strip_path(self, full_path, root_path):
        if root_path[-1] != "/":
            root_path = root_path+'/'

        filename = full_path.split(root_path)[1]

        if '.' in filename:
            # Strip the file name
            filename = filename.split('.')[0]

        return filename

    def potfile_to_json(self, filepath, root_path):
        """
        Parse the pot file, create the request body
        @param filepath: the path of the pot file
        """
        filename = self.strip_path(filepath, root_path)
        pofile = self.create_pofile(filepath)
        textflows = self.create_txtflow(pofile)
        extensions = self.create_extensions(pofile, "po-header")
        items = {'name':filename, 'contentType':'application/x-gettext', 'lang':'en-US', 'extensions':extensions, 'textFlows':textflows}
        
        return json.dumps(items), filename

    def pofile_to_json(self, filepath):
        """
        Parse the po file, create the request body
        @param filepath: the path of the po file
        """
        pofile = self.create_pofile(filepath)
        textflowtargets = self.create_txtflowtarget(pofile)
        #the function for extensions have not implemented yet
        extensions = self.create_extensions(pofile, "po-target-header")
        items = {'links':[],'extensions':extensions, 'textFlowTargets':textflowtargets}
        
        return json.dumps(items)

    def save_to_pofile(self, path, translations, pot):
        """
        Save PO file to path, based on json objects of pot and translations 
        @param translations: the json object of the content retrieved from server
        @param path: the po folder for output
        @param pot: the json object of the pot retrieved from server
        """
        po = polib.POFile(fpath=path)
        
        potcontent = json.loads(pot)
        # pylint: disable-msg=E1103
        textflows = potcontent.get('textFlows')
                
        if potcontent.get('extensions'):
            extensions = potcontent.get('extensions')[0]
            po.header = extensions.get('comment')     
            for item in extensions.get('entries'):
                po.metadata[item['key']]=item['value']

        for textflow in textflows:
            if textflow.get('extensions'):
                poentry = polib.POEntry(occurrences=None)
                entry_list = textflow.get('extensions')
                for entry in entry_list:
                    if entry.get('object-type') == 'pot-entry-header':
                        #PotEntryHeader
                        #Check the references is not empty
                        if entry.get('references')!=[u'']:
                            for item in entry.get('references'):
                                #in some cases, entry contains more than one reference
                                if ' ' in item:
                                    reference = item.split(' ')
                                    ref_list = []
                                    for i in reference:
                                        ref = tuple(i.split(':'))
                                        ref_list.append(ref)
                                    poentry.occurrences= ref_list 
                                else:
                                    poentry.occurrences = [tuple(item.split(':'))]
                        else:
                            poentry.occurrences = None
                        #print poentry.occurrences
                        poentry.flags = entry.get('flags')  
                    
                    if entry.get('object-type') == 'comment':
                        #SimpleComment
                        poentry.comment = entry.get('value')
                         
                poentry.msgid = textflow.get('content')
                po.append(poentry)
          
        #If the translation is exist, read the content of the po file
        if translations:
            content = json.loads(translations)
            """            
            "extensions":[{"object-type":"po-target-header", "comment":"comment_value", "entries":[{"key":"ht","value":"vt1"}]}]
            """
            if content.get('extensions'):
                ext = content.get('extensions')[0]
                header_comment = ext.get('comment')
                if header_comment:
                    po.header = header_comment
                for item in ext.get('entries'):
                    po.metadata[item['key']]=item['value']  
            
            targets = content.get('textFlowTargets')
                            
            """
            "extensions":[{"object-type":"comment","value":"testcomment","space":"preserve"}]
            """ 
            # copy any other stuff you need to transfer
            for message in po:
                for translation in targets:
                    if translation.get('extensions'):
                        extensions=translation.get('extensions')[0]
                        #if extensions:
                        #    ext_type = extensions.get('object-type')
                        #    comment = extensions.get('comment')
                        #    entries = extensions.get('value')
                    if self.hash_match(message, translation.get('resId')):
                        message.msgstr = translation.get('content')
                   
        # finally save resulting po to outpath as lang/myfile.po
       
        po.save()
        # pylint: disable-msg=E1103
        self.log.info("Writing po file to %s"%(path))
        
        
