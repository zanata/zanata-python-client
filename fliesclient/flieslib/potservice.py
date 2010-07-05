#vim:set et sts=4 sw=4: 
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
        "PublicanService",
   )

import os
import json
import hashlib
import polib
import shutil
from ordereddict import OrderedDict
from rest.client import RestClient
from publican import Publican
from error import *

class PublicanService:    
    def __init__(self, base_url, usrname = None, apikey = None):
        self.restclient = RestClient(base_url)
        self.username = usrname
        self.apikey = apikey
    
    def get_translations_from_flies(self, projectid, iterationid, filename, lang):
        print projectid
        print iterationid
        print filename
        print lang
        if projectid and iterationid :
            res, content = self.restclient.request_get('/projects/p/%s/iterations/i/%s/r/%s/translations/%s'%(projectid,
            iterationid, filename, lang))
            if res['status'] == '201':
                return content
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        else:
            raise InvalidOptionException('Error', 'Invalid Options')     
        
    def hash_matches(self, message, id):
        m = hashlib.md5()
        m.update(message.msgid)
        if m.hexdigest() == id:
            return True
        else:
            return False
   
    def check_pot(self, file):
        #search pot folder in current folder
        potfolder = os.path.join(os.getcwd(), 'pot')    
        if file in os.listdir(potfolder):
            return True
        else:
            return False
    
    def search_pot(self):
        #search pot folder in current folder        
        potfolder = os.path.join(os.getcwd(), 'pot')
        if os.path.isdir(potfolder):
            filelist = os.listdir(potfolder)
            return filelist
        else:
            return None

    def create_pofile(self, lang, file, projectid, iterationid):
        filename = file[:-4]
        poname = filename+'_%s.po'%lang.replace('-','_')
        pofile = os.path.join(os.getcwd(), poname)        
        
        # If the PO file doesn't exist
        # create a PO file based on POT and language        
        if not os.path.isfile(pofile): 
            #copy the content of pot file to po file
            potfile = os.path.join(os.getcwd(), 'pot/'+file)
            shutil.copy(potfile, pofile)
        
        #read the content of the po file
        publican = Publican(pofile)
        po = publican.load_po()
        
        #retrieve the content from the flies server
        translations = self.get_translations_from_flies(projectid, iterationid, filename, lang)
        
        content = json.loads(translations)
        targets = content.get('textFlowTargets')    
        
        for message in po:
            for translation in targets:
                if self.hash_matches(message, translation.get('resId')):
                    message.msgstr = translation.get('content')
              
        # copy any other stuff you need to transfer
        # finally save resulting pot as as myfile_lang.po
        po.save()

    def post_server(self, projectid, iterationid, filename):
        print 'filename %s'%filename
        headers = {}
        headers['X-Auth-User'] = self.username
        headers['X-Auth-Token'] = self.apikey        
        filepath = os.path.join(os.getcwd(), filename)        
        if not os.path.isfile(filepath):
            raise NoSuchFileException('Error', 'No Such File')
        
        publican = Publican(filepath) 
        textflows = publican.read_po()
        items = [('name', filename), ('contentType','application/x-gettext'), ('lang', 'en'), ('extensions', []),
        ('textFlows',textflows)]
        body = json.dumps(OrderedDict(items))
               
        if projectid and iterationid :
            res, content = self.restclient.request_post('/projects/p/%s/iterations/i/%s/r'%(projectid,iterationid), args=body, headers=headers)
            
            print res['status'] 
            print content
            if res['status'] == '201':
                return "Success"
            elif res['status'] == '404':
                raise NoSuchProjectException('Error 404', 'No Such project')
            elif res['status'] == '401':
                raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
        else:
            raise InvalidOptionException('Error', 'Invalid Options')
    
    def push(self, projectid, iterationid, filename = None):
        #if file no specified, push all the files in pot folder to flies server
        if not file:
            #check the pot folder to find all the pot file
            filelist = self.search_pot()
            if filelist:
                for pot in filelist:
                    self.post_server(projectid, iterationid, pot)
            else:
                raise InvalidPOTFileException('Error', 'Can not find pot file')
        else:
            print "push filename%s"%filename
            self.post_server(projectid, iterationid, filename)
           
    def pull(self, lang, projectid, iterationid, file = None):
        #if file no specified, retrieving all the file in project
        if not file:
            #check the pot folder to find all the pot file
            filelist = self.search_pot()
            if filelist:
                for pot in filelist:
                    self.create_pofile(lang, pot, projectid, iterationid)
            else:
                raise InvalidPOTFileException('Error', 'Can not find pot file')
        else:
            if self.check_pot(file):            
                self.create_pofile(lang, file, projectid, iterationid)
            else:
                raise InvalidPOTFileException('Error', 'Can not find pot file')

