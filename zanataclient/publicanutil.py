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
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

__all__ = (
            "PublicanUtility",
          )

import polib
import hashlib
import os
import re

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
            context = ""
            reflist = []
            content = ""
            
            if entry.msgctxt:
                hashbase = entry.msgctxt + u"\u0000" + entry.msgid
                context = entry.msgctxt
            else:
                hashbase = entry.msgid
            # pylint: disable=E1101
            m = hashlib.md5()
            m.update(hashbase.encode('utf-8'))
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

            if entry.msgid_plural:
                content = [entry.msgid, entry.msgid_plural]
            else:
                content = entry.msgid

            extensions=[{'object-type':'comment','value':extracted_comment,'space':'preserve'}, {"object-type":"pot-entry-header", "context": context, "references":reflist,"extractedComment":'',"flags":flags}]

            if entry.msgid_plural:
                textflow = {'id': textflowId, 'lang':'en-US', 'contents': content, 'plural':'true', 'extensions':extensions}
            else:
                textflow = {'id': textflowId, 'lang':'en-US', 'content':content, 'plural':'false', 'extensions':extensions}
            
            textflows.append(textflow)
        return textflows
    
    def create_txtflowtarget(self, pofile):
        """
        Convert the content of the po file to a list of textflowtarget.
        @return: the dictionary object of textflow
        """
        obs_list=pofile.obsolete_entries()
        textflowtargets = []
        content = ""
        
        for entry in pofile:
            if entry in obs_list:
                continue

            if entry.msgctxt:
                hashbase = entry.msgctxt + u"\u0000" + entry.msgid
            else:
                hashbase = entry.msgid
            # pylint: disable=E1101
            m = hashlib.md5()
            m.update(hashbase.encode('utf-8'))
            textflowId = m.hexdigest()
            translator_comment = entry.tcomment
            
            if entry.msgstr:
                state = "Approved"
            else:
                state = "New"
            
            #need judge for fuzzy state
            if "fuzzy" in entry.flags:
                state = "NeedReview"
            
            #create extensions
            extensions = [{"object-type":"comment","value":translator_comment,"space":"preserve"}]
           
            if entry.msgid_plural:
                content = []
                keys = entry.msgstr_plural.keys()
                keys.sort()
                for key in keys:
                    content.append(entry.msgstr_plural[key])
                textflowtarget = {'resId': textflowId, 'state': state, 'contents':content,'extensions':extensions}
            else:
                content = entry.msgstr
                textflowtarget = {'resId': textflowId, 'state': state, 'content':content,'extensions':extensions}
            
            textflowtargets.append(textflowtarget)
        
        return textflowtargets

    def validate_content_type(self, content_type, object_type):
        PATTERN = r'.+? charset=([\w_\-:\.]+)'
        rxt = re.compile(unicode(PATTERN))

        match = rxt.search(content_type)
        if match:
            enc = match.group(1).strip()
            if enc not in ["UTF-8", "utf-8", "utf8", "ascii", "UTF8", "ASCII"]:
                if enc == 'CHARSET':
                    if object_type == 'po-target-header':
                        self.log.error("Invalid encoding CHARSET; please correct the Content-Type charset (UTF-8 recommended)")
                        sys.exit(1)
                else:
                    self.log.error("Unsupported encoding; please change the Content-Type charset (UTF-8 recommended)")
                    sys.exit(1)

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

        if pofile.metadata.has_key('Content-Type'):
            self.validate_content_type(pofile.metadata['Content-Type'], object_type)

        extensions = [{"object-type":object_type,"comment":pofile.header, "entries":entries}]
        return extensions

    def create_pofile(self, path):
        """
        Convert the po file to a pofile object in polib.
        @return: pofile object
        """
        try:
            po = polib.pofile(path)
        except Exception, e:
            self.log.error(str(e))
            sys.exit(1)

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

    def hash_match(self, message, resid):
        """
        Caculate the hash of msgid and msgctxt, then compare result with resId from server,
        return true if equal
        """
        if message.msgctxt:
            hashbase = message.msgctxt + u"\u0000" + message.msgid
        else:
            hashbase = message.msgid
        # pylint: disable=E1101
        m = hashlib.md5()
        m.update(hashbase.encode('utf-8'))

        if m.hexdigest() == resid:
            return True
        else:
            return False 

    def strip_path(self, full_path, root_path, suffix):
        if root_path[-1] != "/":
            root_path = root_path+'/'

        # strip root path from the front of full_path
        filename = full_path[len(root_path):]

        if suffix in filename:
            # remove suffix from file name
            filename = filename[0:-len(suffix)]

        return filename

    def check_plural(self, filepath):
        pofile = self.create_pofile(filepath)
        for entry in pofile:
            if entry.msgid_plural:
                return True
        return False

    def potfile_to_json(self, filepath, root_path):
        """
        Parse the pot file, create the request body
        @param filepath: the path of the pot file
        """
        filename = self.strip_path(filepath, root_path, '.pot')
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

    def glossary_to_json(self, filepath, lang, sourcecomments):
        pofile = self.create_pofile(filepath)
        entries = []
        targetlocales = []
        targetlocales.append(lang)
        srclocales = []
        srclocales.append('en-US')
        
        for item in pofile:
            entry= {'srcLang':'en-US','glossaryTerms':'', 'sourcereference':''}
            target_comments=[]
            source_comments=[]
            comments=''
            reflist = []
            references = item.occurrences
            
            for ref in references:
                node = ref[0]+":"+ref[1]
                reflist.append(node)

            if sourcecomments:
                target_comments = target_comments+reflist
                target_comments.append(item.comment)
            else:
                if entry['sourcereference']:
                    comments = comments+entry['sourcereference']
                if reflist:
                    ref = '\n'.join(str(n) for n in reflist)
                    comments = comments+ref
                entry['sourcereference'] = comments    
                source_comments.append(item.comment)

            terms = [{'locale':lang, 'content':item.msgstr, 'comments':target_comments}, {'locale':'en-US', 'content':item.msgid, 'comments':source_comments}]
            entry['glossaryTerms'] = terms 
 
            entries.append(entry)

        glossary = {'sourceLocales':srclocales, 'glossaryEntries':entries, 'targetLocales':targetlocales}
        
        return json.dumps(glossary)

    def save_to_pofile(self, path, translations, pot, create_skeletons, locale, doc_name):
        """
        Save PO file to path, based on json objects of pot and translations 
        @param translations: the json object of the content retrieved from server
        @param path: the po folder for output
        @param pot: the json object of the pot retrieved from server
        """
        po = polib.POFile(fpath=path)
        
        potcontent = json.loads(pot)
        # pylint: disable=E1103
        textflows = potcontent.get('textFlows')
                
        if potcontent.get('extensions'):
            extensions = potcontent.get('extensions')[0]
            po.header = extensions.get('comment')     
            for item in extensions.get('entries'):
                po.metadata[item['key']]=item['value']
            #specify Content-Type charset to UTF-8
            pattern = r'charset=[^;]*'
            if po.metadata.has_key('Content-Type'):
                re.sub(pattern, "charset=UTF-8", po.metadata['Content-Type'])
            else:
                po.metadata['Content-Type']="text/plain; charset=UTF-8"

        for textflow in textflows:
            if textflow.get('extensions'):
                poentry = polib.POEntry(occurrences=None)
                entry_list = textflow.get('extensions')
                for entry in entry_list:
                    if entry.get('object-type') == 'pot-entry-header':
                        #PotEntryHeader
                        #Check the references is not empty
                        if entry.get('references')!=[u'']:
                            ref_list = []
                            for item in entry.get('references'):
                                #in some cases, entry contains more than one reference
                                if ' ' in item:
                                    reference = item.split(' ')
                                    for i in reference:
                                        ref_list.append(tuple(i.rsplit(':', 1)))
                                else:
                                    ref_list.append(tuple(item.rsplit(':', 1)))
                            poentry.occurrences = ref_list
                        else:
                            poentry.occurrences = None
                    
                        if entry.get('flags'):
                            poentry.flags = entry.get('flags')

                        if entry.get('context'):
                            poentry.msgctxt = entry.get('context')
                                            
                    if entry.get('object-type') == 'comment':
                        #SimpleComment
                        poentry.comment = entry.get('value')
                         
                poentry.msgid = textflow.get('content')
                po.append(poentry)
          
        #If the translation is exist, read the content of the po file
        if translations:
            content = json.loads(translations)
            #"extensions":[{"object-type":"po-target-header", "comment":"comment_value", "entries":
            #[{"key":"ht","value":"vt1"}]}]
            
            if content.get('extensions'):
                ext = content.get('extensions')[0]
                header_comment = ext.get('comment')
                if header_comment:
                    po.header = header_comment
                for item in ext.get('entries'):
                    po.metadata[item['key']]=item['value']  
            
            targets = content.get('textFlowTargets')
            if not create_skeletons:
                if not targets:
                    self.log.warn("No translations found in %s for document %s"%(locale, doc_name))
                    return

            #"extensions":[{"object-type":"comment","value":"testcomment","space":"preserve"}]
             
            # copy any other stuff you need to transfer
            for message in po:
                for translation in targets:
                    if translation.get('extensions'):
                        extensions=translation.get('extensions')
                        if extensions:
                            for entry in extensions:
                                if entry.get('object-type') == 'comment':
                                    message.tcomment = entry.get('value')
               
                    if self.hash_match(message, translation.get('resId')):
                        message.msgstr = translation.get('content')
                        if translation.get('state') == 'NeedReview':
                            if message.flags == [u'']:
                                message.flags = ['fuzzy']
                            else:
                                message.flags.insert(0, 'fuzzy')
                        else:
                            if message.flags == [u'']:
                                message.flags = None

        # finally save resulting po to outpath as lang/myfile.po
        po.save()
        # pylint: disable=E1103
        self.log.info("Writing po file to %s"%(path))
