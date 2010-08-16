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

import getopt, sys
import json
import os.path
import hashlib
import shutil
from parseconfig import FliesConfig
from publican import Publican
from flieslib.client import FliesResource
from flieslib.project import Project
from flieslib.project import Iteration
from flieslib.error import *

sub_command = {
                'help':[],
                'list':[],
                'status':[],
                'project':['info','create', 'remove'],
                'iteration':['info', 'create', 'remove'],
                'publican':['push', 'pull']
                }

class FliesConsole:

    def __init__(self):
        config = FliesConfig()
    	server = config.get_config_value("server")
    	project_id = config.get_config_value("project.id")
    	iteration_id = config.get_config_value("project.iteration.id") 
    	user = config.get_config_value("user")
    	apikey = config.get_config_value("apikey")
        potfolder = config.get_config_value("potfolder")
        pofolder = config.get_config_value("pofolder")
        self.options = {
                        'server' : server,
                        'project_id':project_id,
                        'iteration_id':iteration_id,
                        'user':user,
                        'apikey':apikey,
                        'potfolder':potfolder,
                        'pofolder':pofolder,
                        'name':'',
                        'desc':'',
                        'lang':''
                       }
     
    def _print_usage(self):
        print ('\nClient for talking to a Flies Server\n\n'
               'basic commands:\n\n'
               'list             List all available projects\n'
               'project info      Retrieve a project\n'
               'iteration info    Retrieve a iteration\n\n'
               "Use 'flies help' for the full list of commands")

    def _print_help_info(self, args):
        if not args:
            print ('Client for talking to a Flies Server:\n\n'
                  'list of commands:\n\n'
                  ' list                List all available projects\n'
                  ' project info         Retrieve a project\n'
                  ' iteration info       Retrieve a iteration\n'
                  ' project create      Create a project\n'
                  ' iteration create    Create a iteration of a project\n'   
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican to Flies Server\n')
        else:
            command = args[0]
            sub = args[1:]
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                        else:
                            print "Can not find such command"
                            sys.exit()
                    else:
                        print "Please complete the command!"
                        sys.exit()
            else:
                print "Can not find such command"
                sys.exit()

            self._command_help(command)

    def _command_help(self, command):      
        if command == 'list':
            self._list_help()
        elif command == 'project_info':
            self._projec_info_help()
        elif command == 'project_create':
            self._project_create_help()
        elif command == 'iteration_info':
            self._iteration_info_help()
        elif command == 'iteration_create':
            self._iteration_create_help()
        elif command == 'publican_push':
            self._publican_push_help()
        elif command == 'publican_pull':
            self._publican_pull_help()
                

    def _list_help(self):
       	print ('flies list [OPTIONS]\n\n'
               'list all available projects\n\n'
               'options:\n\n'
               ' --server url address of the Flies server')
    
    def _projec_info_help(self):
	    print ('flies project info [OPTIONS]')

    def _project_create_help(self):
        print ('flies project create [PROJECT_ID] [OPTIONS]') 

    def _iteration_info_help(self):
	    print ('flies iteration info [OPTIONS]')

    def _iteration_create_help(self):
        print ('flies iteration create [ITERATION_ID] [OPTIONS]')

    def _publican_push_help(self):
        print ('flies publican push [OPTIONS] {document}')

    def _publican_pull_help(self):
        print ('flies publican pull [OPTIONS] {document}')
              
    def _list_projects(self):
        """
        """
        flies = FliesResource(self.options['server'])
        projects = flies.projects.list()
        for project in projects:
            print ("Id:          %s")%project.id
            print ("Name:        %s")%project.name
            print ("Type:        %s")%project.type
            for link in project.links:
                print ("Links:       %s\n")%[link.href, link.type, link.rel]
        
    def _get_project(self):
        """
        """
        if not self.options['project_id']:
            print 'Please use flies project info --project=project_id to retrieve the project info'
            sys.exit()
        
        flies = FliesResource(self.options['server'])
        try:
            p = flies.projects.get(self.options['project_id'])
            print ("Id:          %s")%p.id 
            print ("Name:        %s")%p.name 
            print ("Type:        %s")%p.type
            print ("Description: %s")%p.desc
        except NoSuchProjectException as e:
            print "No Such Project on the server"
        except InvalidOptionException as e:
            print "Options are not valid"
               
    def _get_iteration(self):
        """
        """
        if not self.options['iteration_id'] or not self.options['project_id']:
            print 'Please use flies iteration info --project=project_id --iteration=iteration_id to retrieve the iteration'
            sys.exit()
        
        flies = FliesResource(self.options['server'])
        try:
            project = flies.projects.get(self.options['project_id'])
            iteration = project.get_iteration(self.options['iteration_id'])
            print ("Id:          %s")%iteration.id
            print ("Name:        %s")%iteration.name
            print ("Description: %s")%iteration.desc
        except NoSuchProjectException as e:
            print "No Such Project on the server"

    def _create_project(self, args):
        """
        Create project with project id
        """
        if self.options['user'] and self.options['apikey']:
            flies = FliesResource(self.options['server'], self.options['user'], self.options['apikey'])
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()

        if not args:
            print "Please provide PROJECT_ID for creating project"
            sys.exit()

        if not self.options['name']:
            print "Please provide Project name by '--name' option"
            sys.exit()
        
        try:
            p = Project(id = args[0], name = self.options['name'], desc = self.options['desc'])
            result = flies.projects.create(p)
            if result == "Success":
                print "Success create the project"
        except NoSuchProjectException as e:
            print "No Such Project on the server" 
        except UnAuthorizedException as e:
            print "Unauthorized Operation"
        except ProjectExistException as e:
            print "The project is alreasy exist on the server"

    def _create_iteration(self, args):
        """
        Create iteration with iteration id
        """
        if self.options['user'] and self.options['apikey']:
            flies = FliesResource(self.options['server'], self.options['user'], self.options['apikey'])
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
        
        if not args:
            print "Please provide ITERATION_ID for creating iteration"
            sys.exit()

        if not self.options['name']:
            print "Please provide Iteration name by '--name' option"
            sys.exit()
         
        try:
            iteration = Iteration()
            iteration.id = args[0]
            iteration.name = self.options['name']
            iteration.desc = self.options['desc']
            result = flies.projects.iterations.create(self.options['project_id'], iteration)
            if result == "Success":
                print "Success create the itearion"
        except NoSuchProjectException as e:
            print "No Such Project on the server"
        except UnAuthorizedException as e:
            print "Unauthorized Operation"
        except InvalidOptionException as e:
            print "Options are not valid"

    def list_folder(self, tmlpath):
        """
        Search POT file in POT folder
        """
        if os.path.isdir(tmlpath):
            filelist = os.listdir(tmlpath)
            return filelist
        else:
            return None

    def create_resource(self, filepath):
        if '/' in filepath:
            file = filepath.split('/')[-1]
            path = filepath
        else:
            file = filepath
            path = os.path.join(os.getcwd(), file)

        if '.' in file:
            # Strip the file name
            filename = file.split('.')[0]
        else:
            filename = file
                
        if not os.path.isfile(path):
            raise NoSuchFileException('Error', 'The file %s does not exist'%file)
        
        publican = Publican(path)
        textflows = publican.read_po()
        items = {'name':filename, 'contentType':'application/x-gettext', 'lang':'en', 'extensions':[], 'textFlows':textflows}
        return json.dumps(items)

    def _push_publican(self, args):
        """
        Push the documents to Project on Flies server
        """
        if self.options['user'] and self.options['apikey']:
            flies = FliesResource(self.options['server'], self.options['user'], self.options['apikey'])
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()

        if not self.options['project_id']:
            print "Please provide valid project id by '--project' option"
            sys.exit()
        
        if not self.options['iteration_id']:
            print "Please provide valid iteration id by fliesrc or by '--iteration' option"
            sys.exit()

        tmlfolder = self.options['potfolder'] 
        #if file not specified, push all the files in pot folder to flies server
        if not args:
            if not tmlfolder:
                print "Please provide template folder for processing in fliesrc"
                sys.exit()

            #check the pot folder to find all the pot file
            filelist = self.list_folder(tmlfolder)
            if filelist:                
                for pot in filelist:
                    print "\nPush the content of %s to Flies server: "%pot
                    
                    try: 
                        body = self.create_resource(tmlfolder+'/'+pot)
                    except NoSuchFileException as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue 
                    
                    try:
                        result = flies.resources.commit_translation(self.options['project_id'], self.options['iteration_id'], body)
                        if result:
                            print "Successfully push %s to the Flies server"%pot    
                    except UnAuthorizedException as e:
                        print "%s :%s"%(e.expr, e.msg)                                            
                        break
                    except (BadRequestBodyException, SameNameDocumentException) as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue
            else:
                raise NoSuchFileException('Error', 'The template folder is empty')
        else:
            print "\nPush the content of %s to Flies server: "%args[0]
            try:
                body = self.create_resource(args[0])
            except NoSuchFileException as e:
                print "%s :%s"%(e.expr, e.msg)
                sys.exit()                                            
            try:
                result = flies.resources.commit_translation(self.options['project_id'], self.options['iteration_id'], body)
                if result:
                    print "Successfully push %s to the Flies server"%args[0]
            except (UnAuthorizedException, BadRequestBodyException, SameNameDocumentException) as e:
                print "%s :%s"%(e.expr, e.msg)  

    def hash_matches(self, message, id):
        m = hashlib.md5()
        m.update(message.msgid)
        if m.hexdigest() == id:
            return True
        else:
            return False     

    def create_pofile(self, lang, file, translations, tmlpath, outpath):
        """
        Create PO file based on the POT file in POT folder
        Args:
            lang: language 
            projectid: Id of project
            iterationid: Id of iteration
            file: name of PO file
            
        """
        if '.' in file:        
            filename = file.split('.')[0]
        else:
            filename = file
        
        pofilename = filename+'_%s.po'%lang.replace('-', '_')
        pofile = os.path.join(outpath, pofilename)        
        potfile = os.path.join(tmlpath, filename+'.pot')

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
        
        content = json.loads(translations)
        targets = content.get('textFlowTargets')    
        
        for message in po:
            for translation in targets:
                if self.hash_matches(message, translation.get('resId')):
                    message.msgstr = translation.get('content')
              
        # copy any other stuff you need to transfer
        # finally save resulting pot to outpath as myfile_lang.po
        po.save()
        print "Successfully create %s in %s"%(pofilename, outpath)
    
    def _pull_publican(self, args):
        """
        Retrieve the content of documents in a Project on Flies server
        """
        if not self.options['lang']:
            print "Please specify the language by '--lang' option"
            sys.exit()

        if not self.options['project_id']:
            print "Please provide valid project id by '--project' option"
            sys.exit()
        
        if not self.options['iteration_id']:
            print "Please provide valid iteration id by fliesrc or by '--iteration' option"
            sys.exit()
        
        if not self.options['potfolder']:
            print "Please provide folder for storting the template files in fliesrc"
            sys.exit()

        if not self.options['pofolder']:
            print "Please provide folder for storting the output files in fliesrc"
            sys.exit()

        flies = FliesResource(self.options['server'])
        
        #if file no specified, retrieve all the files of project
        if not args:
            #list the files in project
            filelist = flies.resources.get_file_list(self.options['project_id'], self.options['iteration_id'])
            if filelist:
                for file in filelist:
                    print "\nFetch the content of %s from Flies server: "%file                    
                    try:    
                        result = flies.resources.retrieve_translation(self.options['lang'], self.options['project_id'], self.options['iteration_id'], file)
                        self.create_pofile(self.options['lang'], file, result, self.options['potfolder'], self.options['pofolder'])
                    except UnAuthorizedException as e:
                        print "%s :%s"%(e.expr, e.msg)                        
                        break
                    except UnAvaliableResourceException as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue
        else:
            print "\nFetch the content of %s from Flies server: "%args[0]
            try:            
                result = flies.resources.retrieve_translation(self.options['lang'], self.options['project_id'], self.options['iteration_id'], args[0])
                self.create_pofile(self.options['lang'], args[0], result, self.options['potfolder'], self.options['pofolder'])
            except (UnAuthorizedException, UnAvaliableResourceException) as e:
                print "%s :%s"%(e.expr, e.msg)                        

    def _remove_project(self):
        pass

    def _remove_iteration(self):
        pass

    def _project_status(self):
        pass
    
    def _process_command_line(self):
        """
        """
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["server=", "project=", "iteration=", "name=", "description=", "lang="])
        except getopt.GetoptError, err:
            print str(err)
            sys.exit(2)

        if args:
            command = args[0]
            sub = args[1:]            
            if sub_command.has_key(command):
                if sub_command[command]:
                    if sub[0]:
                        if sub[0] in sub_command[command]:
                            command = command+'_'+sub[0]
                            command_args = sub[1:]
                        else:
                            print "Can not find such command"
                            sys.exit()
                    else:
                        print "Please complete the command!"
                        sys.exit()
                else: 
                    command_args = sub
            else:
                print "Can not find such command"
                sys.exit()
        else:
            self._print_usage()
            sys.exit()
                         
        if opts:
            for o, a in opts:
                if o in ("--server"):
                    self.options['server'] = a
                elif o in ("--name"):
                    self.options['name'] = a
                elif o in ("--description"):
                    self.options['desc'] = a
                elif o in ("--project"):
                    self.options['project_id'] = a
                elif o in ("--iteration"):
                    self.options['iteration_id'] = a
                elif o in ("--lang"):
                    self.options['lang'] = a
    
        return command, command_args
 
    def run(self):
        command, command_args = self._process_command_line()        
        
        if command == 'help':
            self._print_help_info(command_args)
        else:
            if not self.options['server']:
                print "Please provide valid server url by fliesrc or by '--server' option"
                sys.exit()
            
            if command == 'list':
                self._list_projects()
            elif command == 'status':
                self._poject_status()
            elif command == 'project_info':
                self._get_project()
            elif command == 'project_create':
                self._create_project(command_args)
            elif command == 'project_remove':
                self._remove_project(command_args)
            elif command == 'iteration_info':
                self._get_iteration()
            elif command == 'iteration_create':
                self._create_iteration(command_args)
            elif command == 'iteration_remove':
                self._remove_iteration(command_args)
            elif command == 'publican_push':
                self._push_publican(command_args)
            elif command == 'publican_pull':
                self._pull_publican(command_args)      
        

def main():
    client = FliesConsole()
    client.run()

if __name__ == "__main__":
    main()       
