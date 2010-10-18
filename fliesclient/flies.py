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
            "FliesConsole",
        )

import getopt, sys
import json
import os.path
import hashlib
import shutil
from parseconfig import FliesConfig
from publican import Publican
from xml.dom import minidom 
from flieslib import *

sub_command = {
                'help':[],
                'list':[],
                'status':[],
                'project':['info','create', 'remove'],
                'iteration':['info', 'create', 'remove'],
                'publican':['push', 'pull', 'update']
                }

options = {
            'url' : '',
            'user_name':'',
            'key':'',
            'user_config':'',
            'project_config':'',
            'project_id':'',
            'project_version':'',
            'potfolder':'',
            'pofolder':'',
            'project_name':'',
            'project_desc':'',
            'version_name':'',
            'version_desc':'',
            'lang':''
            }

project_config = {'project_id':'', 'project_version':'', 'locale_map':{}}

class FliesConsole:

    def __init__(self):
        self.url = ''
        self.user_name = ''
        self.apikey = ''
        self.user_config = ''
        self.project_config = ''
        
    def _print_usage(self):
        print ('\nClient for talking to a Flies Server\n\n'
               'basic commands:\n\n'
               'list             List all available projects\n'
               'project info      Retrieve a project\n'
               'version info    Retrieve a iteration\n\n'
               "Use 'flies help' for the full list of commands")

    def _print_help_info(self, args):
        """
        Output the general help information or the help information for each command
        @param args: the name of command and sub command
        """
        if not args:
            print ('Client for talking to a Flies Server:\n\n'
                  'Usage: flies <command> [COMMANDOPTION]...\n\n'
                  'list of commands:\n'
                  ' help                Display this help and exit\n'
                  ' list                List all available projects\n'
                  ' project info         Retrieve a project\n'
                  ' version info       Retrieve a iteration\n'
                  ' project create      Create a project\n'
                  ' version create    Create a iteration of a project\n'   
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican file to Flies Server\n'
                  ' publican update     Update the translation of publican file to Flies Server\n')
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
        List the information of all the project on the flies server
        """
        
        flies = FliesResource(self.url)
        projects = flies.projects.list()
        
        if not projects:
            print "There is no projects on the server or the server not working"
            sys.exit()
        for project in projects:
            print ("Id:          %s")%project.id
            print ("Name:        %s")%project.name
            print ("Type:        %s")%project.type
            for link in project.links:
                print ("Links:       %s\n")%[link.href, link.type, link.rel]
        
    def _get_project(self):
        """
        Retrieve the information of a project
        """
        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = project_config['project_id']        
        
        if not project_id:
            print 'Please use flies project info --project-id=project_id or flies.xml to retrieve the project info'
            sys.exit()
        
        flies = FliesResource(self.url)
        try:
            p = flies.projects.get(project_id)
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
        Retrieve the information of a project iteration.
        """
        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = project_config['project_id']
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = project_config['project_version']

        if not iteration_id or not project_id:
            print 'Please use flies iteration info --project=project_id --project-version=project_version to retrieve the iteration'
            sys.exit()
        
        flies = FliesResource(self.url)
        try:
            project = flies.projects.get(project_id)
            iteration = project.get_iteration(iteration_id)
            print ("Id:          %s")%iteration.id
            print ("Name:        %s")%iteration.name
            print ("Description: %s")%iteration.desc
        except NoSuchProjectException as e:
            print "No Such Project on the server"

    def _create_project(self, args):
        """
        Create project with the project id
        @param args: project id
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "Please provide username and apikey in flies.ini"
            sys.exit()

        if not args:
            print "Please provide PROJECT_ID for creating project"
            sys.exit()

        if not options['name']:
            print "Please provide Project name by '--name' option"
            sys.exit()
        
        try:
            p = Project(id = args[0], name = options['project_name'], desc = options['project_desc'])
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
        Create iteration with the iteration id
        @param args: iteration id
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "Please provide username and apikey in flies.ini or by --username and --apikey options"
            sys.exit()
        
        if options['project_id']:
            project_id =  options['project_id'] 
        elif project_config['project_id']:
            project_id = project_config['project_id']
        else:
            print "Please provide PROJECT_ID by --project-id option or using flies.xml"
        
        if not args:
            print "Please provide ITERATION_ID for creating iteration"
            sys.exit()

        if not options['version_name']:
            print "Please provide Iteration name by '--version-name' option"
            sys.exit()
         
        try:
            iteration = Iteration()
            iteration.id = args[0]
            iteration.name = options['version_name']
            iteration.desc = options['version_desc']
            result = flies.projects.iterations.create(project_id, iteration)
            if result == "Success":
                print "Success create the itearion"
        except ProjectExistException as e:
            print "The iteration is already exist on the server"
        except NoSuchProjectException as e:
            print "No Such Project on the server"
        except UnAuthorizedException as e:
            print "Unauthorized Operation"
        except InvalidOptionException as e:
            print "Options are not valid"

    def _list_folder(self, tmlpath):
        if os.path.isdir(tmlpath):
            filelist = os.listdir(tmlpath)
            return filelist
        else:
            return None

    def _create_resource(self, filepath):
        """
        Parse the pot file and create the request body
        @param filepath: the path of the pot file
        """
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
        textflows = publican.covert_txtflow()
        items = {'name':filename, 'contentType':'application/x-gettext', 'lang':'en', 'extensions':[], 'textFlows':textflows}
        return json.dumps(items)

    def _create_translation(self, filepath):
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
        textflowtargets = publican.covert_txtflowtarget()
        #this functions have not implemented yet
        extensions = publican.extract_potheader()

        items = {'links':[],'extensions':[], 'textFlowsTargets':textflowtargets}
        
        return json.dumps(items)

    def _push_publican(self, args):
        """
        Push the content of publican files to a Project iteration on Flies server
        @param args: name of the publican file
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "Please provide username and apikey in flies.ini or by '--username' and '--apikey' options"
            sys.exit()

        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = read_project_config('project_id')
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = read_project_config('project_version')

        if not project_id:
            print "Please provide valid project id by flies.xml or by '--project' option"
            sys.exit()
        
        if not iteration_id:
            print "Please provide valid iteration id by flies.xml or by '--project-version' option"
            sys.exit()

        #if file not specified, push all the files in pot folder to flies server
        if not args:
            if options['potfolder']:
                tmlfolder = options['potfolder']
            else:
                tmlfolder = os.getcwd()+'/pot'
                       
            #check the pot folder to find all the pot file
            filelist = self._list_folder(tmlfolder)
            if filelist:                
                for pot in filelist:
                    print "\nPush the content of %s to Flies server:"%pot
                    
                    try: 
                        body = self._create_resource(tmlfolder+'/'+pot)
                    except NoSuchFileException as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue 
                    
                    try:
                        result = flies.documents.commit_translation(project_id, iteration_id, body)
                        if result:
                            print "Successfully push %s to the Flies server"%pot    
                    except UnAuthorizedException as e:
                        print "%s :%s"%(e.expr, e.msg)                                            
                        break
                    except (BadRequestBodyException, SameNameDocumentException) as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue
            else:
                print "Error, The template folder is empty or not exist"
        else:
            print "\nPush the content of %s to Flies server:"%args[0]
            try:
                body = self._create_resource(args[0])
            except NoSuchFileException as e:
                print "%s :%s"%(e.expr, e.msg)
                sys.exit()                                            
            try:
                result = flies.documents.commit_translation(project_id, iteration_id, body)
                if result:
                    print "Successfully push %s to the Flies server"%args[0]
            except (UnAuthorizedException, BadRequestBodyException, SameNameDocumentException) as e:
                print "%s :%s"%(e.expr, e.msg)  

    def _update_publican(self, args):
        """
        Update the content of publican files to a Project iteration on Flies server
        @param args: name of the publican file
        """
        if self.user_name and self.apikey:
            flies = FliesResource(self.url, self.user_name, self.apikey)
        else:
            print "Please provide username and apikey in flies.ini or by '--username' and '--apikey' options"
            sys.exit()

        if options['project_id']:
            project_id =  options['project_id'] 
        else:
            project_id = read_project_config('project_id')
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = read_project_config('project_version')

        if not project_id:
            print "Please provide valid project id by flies.xml or by '--project' option"
            sys.exit()
        
        if not iteration_id:
            print "Please provide valid iteration id by flies.xml or by '--project-version' option"
            sys.exit()

        #if file not specified, update all the files in po folder to flies server
        if not args:
            if options['pofolder']:
                upfolder = options['pofolder']
            else:
                upfolder = os.getcwd()+'/po'
                       
            #check the po folder to find all the po file
            filelist = self._list_folder(upfolder)
            if filelist:                
                for po in filelist:
                    print "\nUpdate the content of %s to Flies server: "%po
                    
                    try: 
                        body = self._create_translation(upfolder+'/'+po)
                    except NoSuchFileException as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue 
                    
                    try:
                        #result = flies.documents.update_translation(project_id, iteration_id, body)
                        #if result:
                            print "Successfully update %s to the Flies server"%po 
                        #else:
                        #    print "Error"
                    except UnAuthorizedException as e:
                        print "%s :%s"%(e.expr, e.msg)                                            
                        break
                    except (BadRequestBodyException) as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue
            else:
                print "Error, The update folder is empty or not exist"
        else:
            print "\nUpdate the content of %s to Flies server:"%args[0]
            try:
                body = self._create_translation(args[0])
            except NoSuchFileException as e:
                print "%s :%s"%(e.expr, e.msg)
                sys.exit()                                            
            try:
                result = flies.documents.update_translation(project_id, iteration_id, body)
                
                if result:
                    print "Successfully update %s to the Flies server"%args[0]
                else:
                    print "Error"
            except (UnAuthorizedException, BadRequestBodyException) as e:
                print "%s :%s"%(e.expr, e.msg) 

    def _hash_matches(self, message, id):
        m = hashlib.md5()
        m.update(message.msgid.encode('utf-8'))
        if m.hexdigest() == id:
            return True
        else:
            return False     

    def _create_pofile(self, lang, file, translations):
        """
        Create PO file based on the POT file in POT folder
        @param lang: language 
        @param translations: the json object of the content retrieved from server
        @param tmlpath: the pot folder 
        @param outpath: the po folder for output
        """
        if options['potfolder']:
            tmlpath = options['potfolder']
        else:
            tmlpath = os.getcwd()+'/pot'

        if options['pofolder']:
            outpath = options['pofolder']
        else:
            outpath = os.getcwd()+'/po'    
        
        if not os.path.isdir(tmlpath):
            print "Please provide folder for storing the template files by '--template' option "
            sys.exit()

        if not os.path.isdir(outpath):
            print "Please provide folder for storing the output files by '--output' option"
            sys.exit()
        
        #Check the pot file
        if '.' in file:        
            filename = file.split('.')[0]
        else:
            filename = file
        
        potfile = os.path.join(tmlpath, filename+'.pot')
       
        if not os.path.isfile(potfile):
            raise UnAvaliablePOTException('Error', 'The requested POT file is not available') 

        # Create a PO file based on POT and language  
        pofilename = filename+'_%s.po'%lang.replace('-', '_')
        pofile = os.path.join(outpath, pofilename)         
                   
        # If the PO file doesn't exist
        if not os.path.isfile(pofile): 
            #copy the content of pot file to po file
            shutil.copy(potfile, pofile)
        
        #If the PO file is already exist, read the content of the po file
        publican = Publican(pofile)
        po = publican.load_po()
               
        content = json.loads(translations)
        targets = content.get('textFlowTargets')    
        
        for message in po:
            for translation in targets:
                if self._hash_matches(message, translation.get('resId')):
                    message.msgstr = translation.get('content')
              
        # copy any other stuff you need to transfer
        # finally save resulting pot to outpath as myfile_lang.po
        po.save()
        print "Successfully create %s in %s"%(pofilename, outpath)
    
    def _pull_publican(self, args):
        """
        Retrieve the content of documents in a Project iteration from Flies server. If the name of publican
        file is specified, the content of that file will be pulled from server. Otherwise, all the document of that
        Project iteration will be pulled from server.
        @param args: the name of publican file
        """
        if options['lang']:
            if options['lang'] in self.localemap:
                lang = self.localemap[options['lang']]
            else:
                lang = options['lang']
        else:
            print "Please specify the language by '--lang' option"
            sys.exit()

        if project:
            project_id =  options['project_id'] 
        else:
            project_id = read_project_config('project_id')
        
        if options['project_version']:
            iteration_id = options['project_version'] 
        else:
            iteration_id = read_project_config('project_version')

        if not project_id:
            print "Please provide valid project id by flies.xml or by '--project' option"
            sys.exit()
        
        if not iteration_id:
            print "Please provide valid iteration id by flies.xml or by '--iteration' option"
            sys.exit()

        flies = FliesResource(self.url)
        
        #if file no specified, retrieve all the files of project
        if not args:
            #list the files in project
            filelist = flies.documents.get_file_list(project_id, iteration_id)
            print filelist            
            if filelist:
                for file in filelist:
                    print "\nFetch the content of %s from Flies server: "%file                    
                    try:    
                        result = flies.documents.retrieve_translation(lang, project_id, iteration_id, file)
                        self._create_pofile(lang, file, result)
                    except UnAuthorizedException as e:
                        print "%s :%s"%(e.expr, e.msg)                        
                        break
                    except UnAvaliableResourceException as e:
                        print "%s :%s"%(e.expr, e.msg)
                        continue
        else:
            print "\nFetch the content of %s from Flies server: "%args[0]
            try:            
                result = flies.documents.retrieve_translation(lang, project_id, iteration_id, args[0])
                self._create_pofile(lang, args[0], result)
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
        Parse the command line to generate command options and sub_command
        """
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["url=", "project-id=", "project-version=", "project-name=",
            "project-desc=", "version-name=", "version-desc=", "lang=",  "user-config=", "project-config=", "apikey=", "username=", "template=", "output="])
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
                if o in ("--user-config"):
                    options['user_config'] = a                     
                elif o in ("--url"):
                    options['url'] = a
                elif o in ("--project-name"):
                    options['project_name'] = a
                elif o in ("--project-desc"):
                    options['project_desc'] = a
                elif o in ("--project-id"):
                    options['project_id'] = a
                elif o in ("--version-name"):
                    options['version_name'] = a
                elif o in ("--version-desc"):
                    options['version_desc'] = a
                elif o in ("--lang"):
                    options['lang'] = a
                elif o in ("--username"):
                    options['user_name'] = a
                elif o in ("--apikey"):
                    options['key'] = a
                elif o in ("--project-config"):
                    options['project_config'] = a
                elif o in ("--project-version"): 
                    options['project_version'] = a
                elif o in ("--template"):
                    options['potfolder'] = a
                elif o in ("--output"):
                    options['pofolder'] = a
                   
        return command, command_args
 
    def _read_project_config(self, filename):
        xmldoc = minidom.parse(filename)
        
        #Read the project id
        node = xmldoc.getElementsByTagName("project")[0]
        rc = ""

        for node in node.childNodes:
            if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
                rc = rc + node.data
        project_config['project_id'] = rc
        
        #Read the project-version
        node = xmldoc.getElementsByTagName("project-version")[0]
        rc = ""
        
        for node in node.childNodes:
            if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
                rc = rc + node.data
        project_config['project_version'] = rc

        #Read the locale map
        locale = xmldoc.getElementsByTagName("locales")[0]
        rc = ""
        
        localelist = locales.getElementByTagName("locale")
        for locale in localelist
            if locale.getAttribute("map-from")
                for node in locale:
                    if node.nodeType == node.TEXT_NODE:
                        rc = rc+node.data
                        map = {locale.getAttribute("map-from"):rc}
                        project_config['locale_map'].update(map)

    def run(self):
        command, command_args = self._process_command_line()        
        
        if command == 'help':
            self._print_help_info(command_args)
        else:
            #Try to find user-config file
            if options['user_config'] and os.path.isfile(options['user_config']):  
                user_config = options['user_config']
            elif os.path.isfile(os.path.expanduser("~")+'/.config/flies.ini'):
                user_config = os.path.expanduser("~")+'/.config/flies.ini'
            else:    
                print "Can not find user-config file in home folder or in 'user-config' option"
                sys.exit()

            #Read the user-config file    
            config = FliesConfig(user_config)
    	    self.url = config.get_config_value("url")
    	    self.user_name = config.get_config_value("username")
    	    self.apikey = config.get_config_value("key")
            
            #The value in options will override the value in user-config file 
            if options['url']:
                self.url = options['url']

            if options['user_name']:
                self.user_name = options['user_name']

            if options['key']:
                self.apikey = options['key']
            
            if not self.url:
                print "Please provide valid server url in flies.ini or by '--url' option"
                sys.exit()
            
            if command == 'list':
                self._list_projects()
            else:
                #Read the project configuration file using --project-config option
                if options['project_config']  and os.path.isfile(options['user_config']):
                    self._read_project_config(options['project_config'])
                elif os.path.isfile(os.getcwd()+'/flies.xml'):
                    #If the option is not valid, try to read the project configuration from current path
                    self._read_project_config(os.getcwd()+'/flies.xml')

                if command == 'status':
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
                elif command == 'publican_update':
                    self._update_publican(command_args)

def main():
    client = FliesConsole()
    client.run()

if __name__ == "__main__":
    main()       
