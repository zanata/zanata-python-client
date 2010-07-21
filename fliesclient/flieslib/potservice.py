#vim:set et sts=4 sw=4: 
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
    def __init__(self, projects):
        self.projects = projects
    
    def get_translations_from_flies(self, projectid, iterationid, filename, lang):
        res, content = self.projects.restclient.request_get('/projects/p/%s/iterations/i/%s/r/%s/translations/%s'%(projectid, iterationid, filename, lang))

        if res['status'] == '200':
            return content
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 'The requested resource is not available')
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
                
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

    def get_file_list(self, projectid, iterationid):
        res, content = self.projects.restclient.request_get('/projects/p/%s/iterations/i/%s/r'%(projectid, iterationid))
        
        if res['status'] == '200':
            list = json.loads(content)
            filelist = [file.get('name') for file in list]
            return filelist
    
    def create_pofile(self, lang, file, projectid, iterationid):
        if '.' in file:        
            filename = file.split('.')[0]
        else:
            filename = file
        poname = filename+'_%s.po'%lang.replace('-','_')
        pofile = os.path.join(os.getcwd(), poname)        
        potfile = os.path.join(os.getcwd(), 'pot/'+filename+'.pot')

        if not os.path.isfile(potfile):
            raise UnAvaliablePOTException('Error', 'The requested POT file is not available')                                    
                   
        # If the PO file doesn't exist
        # create a PO file based on POT and language        
        if not os.path.isfile(pofile): 
            #copy the content of pot file to po file
            shutil.copy(potfile, pofile)
        
        #read the content of the po file
        publican = Publican(pofile)
        po = publican.load_po()
        
        #retrieve the content from the flies server
        try:        
            translations = self.get_translations_from_flies(projectid, iterationid, filename, lang)
        except Exception as e:
            raise

        content = json.loads(translations)
        targets = content.get('textFlowTargets')    
        
        for message in po:
            for translation in targets:
                if self.hash_matches(message, translation.get('resId')):
                    message.msgstr = translation.get('content')
              
        # copy any other stuff you need to transfer
        # finally save resulting pot as as myfile_lang.po
        po.save()
        print "Successfully create %s"%poname

    def _post_server(self, projectid, iterationid, file):
        if '.' in file:
            # Strip the file name        
            filename = file.split('.')[0]
        else:
            filename = file        
    
        headers = {}
        headers['X-Auth-User'] = self.projects.username
        headers['X-Auth-Token'] = self.projects.apikey        
        filepath = os.path.join(os.getcwd(), file)        
        
        if not os.path.isfile(filepath):
            raise NoSuchFileException('Error', 'No Such File')
        
        publican = Publican(filepath) 
        textflows = publican.read_po()
      
        items = [('name', filename), ('contentType','application/x-gettext'), ('lang', 'en'), ('extensions', []), ('textFlows',textflows)]
        body = json.dumps(OrderedDict(items))
      
        res, content = self.projects.restclient.request_post('/projects/p/%s/iterations/i/%s/r'%(projectid,iterationid), args=body, headers=headers)

        if res['status'] == '201':
            print "Successfully push %s to the Flies server"%file
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 'UnAuthorized Operation')
            
    def list(self, projectid, iterationid):
        pass
        
    def push(self, projectid, iterationid, file = None):
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException as e:
                print "%s :%s"%(e.expr, e.msg)
        
        #if file not specified, push all the files in pot folder to flies server
        if not file:
            #check the pot folder to find all the pot file
            filelist = self.search_pot()
            if filelist:                
                for pot in filelist:
                    print "\nPush the content of %s to Flies server: "%pot
                    try:
                        self._post_server(projectid, iterationid, pot)
                    except UnAuthorizedException:
                        print "%s :%s"%(e.expr, e.msg)                                            
                        break
                    else:
                        continue
            else:
                raise NoSuchFileException('Error', 'No Such File')
        else:
            print "\nPush the content of %s to Flies server: "%file
            try:
                self._post_server(projectid, iterationid, file)
            except UnAuthorizedException:            
                print "%s :%s"%(e.expr, e.msg)                    

    def pull(self, lang, projectid, iterationid, file = None):
        if projectid and iterationid:
            try:
                self.projects.iterations.get(projectid, iterationid)
            except NoSuchProjectException as e:
                print "%s :%s"%(e.expr, e.msg)

        #if file no specified, retrieve all the file in project
        if not file:
            #list the files in project
            filelist = self.get_file_list(projectid, iterationid)
            if filelist:
                for file in filelist:
                    print "\nFetch the content of %s from Flies server: "%file                    
                    try:    
                        self.create_pofile(lang, file, projectid, iterationid)
                    except UnAuthorizedException:
                        print "%s :%s"%(e.expr, e.msg)                        
                        break
                    except UnAvaliableResourceException as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue
                    except UnAvaliablePOTException as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue                   
                    else:
                        continue
        else:
            print "\nFetch the content of %s from Flies server: "%file
            try:            
                self.create_pofile(lang, file, projectid, iterationid)
            except UnAuthorizedException as e:
                print "%s :%s"%(e.expr, e.msg)                        
            except UnAvaliableResourceException as e:
                print "%s :%s"%(e.expr, e.msg)
            except UnAvaliablePOTException as e:
                print "%s :%s"%(e.expr, e.msg)
            

