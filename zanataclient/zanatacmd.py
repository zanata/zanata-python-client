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

import sys
import os

from zanatalib import *
from zanatalib.error import *
from parseconfig import ZanataConfig
from publicanutil import PublicanUtility

class ZanataCommand:
    def __init__(self):
        self.log = Logger()

    def _check_project(self, zanataclient, command_options, project_config):
        if command_options.has_key('project_id'):
            project_id =  command_options['project_id'][0]['value'] 
        else:
            project_id = project_config['project_id']
        
        if command_options.has_key('project_version'):
            iteration_id = command_options['project_version'][0]['value'] 
        else:
            iteration_id = project_config['project_version']

        if not project_id:
            self.log.error("Please specify a valid project id in zanata.xml/flies.xml or with '--project-id' option")
            sys.exit(1)
        
        if not iteration_id:
            self.log.error("Please specify a valid version id in zanata.xml/flies.xml or with '--project-version' option")
            sys.exit(1)
        
        self.log.info("Project: %s"%project_id)
        self.log.info("Version: %s"%iteration_id)

        try:
            zanataclient.projects.get(project_id)
        except NoSuchProjectException, e:
            self.log.error(e.msg)
            sys.exit(1)
   
        try:
            zanataclient.projects.iterations.get(project_id, iteration_id)
            return project_id, iteration_id
        except NoSuchProjectException, e:
            self.log.error(e.msg)
            sys.exit(1)

    def _search_file(self, path, filename):
        for root, dirs, names in os.walk(path):
            if filename in names:
                return os.path.join(root, filename)
        raise NoSuchFileException('Error 404', 'File %s not found'%filename)

    def _update_template(self, zanata, project_id, iteration_id, filename, body):
        if '/' in filename:
            request_name = filename.replace('/', ',')
        else:
            request_name = filename
        
        try:
            result = zanata.documents.update_template(project_id, iteration_id, request_name, body, options['copytrans'])
            if result:
                self.log.info("Successfully updated template %s on the server"%filename)
        except BadRequestBodyException, e:
            self.log.error(e.msg) 
    
    def _convert_softwarepo(self):
        if not os.path.isdir(trans_folder):
            self.log.error("Can not find translation, please specify path of the translation folder")
            sys.exit(1)

        pofile_name = item.replace('-','_')+'.po'                

        pofile_full_path = os.path.join(trans_folder, pofile_name)
                        
        if not os.path.isfile(pofile_full_path):
            self.log.error("Can not find the translation for %s"%item)
       
        body = publicanutil.pofile_to_json(pofile_full_path)

    def _convert_docbookpo(self):
        if not os.path.isdir(locale_folder):
            self.log.error("Can not find translation, please specify path of the translation folder")

        if '/' not in filename:
            pofile_name = filename+'.po'
            request_name = filename
        else:
            name = filename.split('/')[1]
            pofile_name = name+'.po'
            request_name = filename.replace('/', ',')

        try:
            pofile_full_path = self.search_file(locale_folder, pofile_name)
        except NoSuchFileException, e:
            self.log.error(e.msg)
             
        body = publicanutil.pofile_to_json(pofile_full_path)

    def _commit_translation(self, filename, project_config, lang, body):
        if not body:
            self.log.error("No content or all entries are obsolete in %s"%pofile_name)

        try:
            result = zanata.documents.commit_translation(project_id, iteration_id, request_name, lang, body, merge)
            if result:
                self.log.info("Successfully pushed translation %s to the Zanata/Flies server"%filename) 
            else:
                self.log.error("Failed to push translation")
        except UnAuthorizedException, e:
            self.log.error(e.msg)                                            
        except BadRequestBodyException, e:
            self.log.error(e.msg)

    def _del_server_content(self, zanata, tmlfolder, project_id, iteration_id, push_files):
        #Get the file list of this version of project
        try:
            filelist = zanata.documents.get_file_list(project_id, iteration_id)
        except Exception, e:
            self.log.error(str(e))
            sys.exit(1)

        if filelist:
            for name in filelist:
                if ',' in filename: 
                    filename = name.replace(',', '\,')
                elif '/' in filename:
                    filename = name.replace('/', ',')
                else:
                    filename = name

                if ".pot" in file:
                    name = os.path.join(tmlfolder, name)
                else:
                    name = os.path.join(tmlfolder, name+".pot")

                if push_files:
                    for filename in push_files: 
                        if name!= os.path.join(tmlfolder, filename):
                            self.log.info("Delete the %s"%name)
                    
                        try:
                            zanata.documents.delete_template(project_id, iteration_id, name)
                        except Exception, e:
                            self.log.error(str(e))
                            sys.exit(1)

    ##############################################
    ##
    ## Commands for interaction with zanata server 
    ##
    ##############################################   
    def list_projects(self, zanata):
        """
        List the information of all the project on the zanata server
        """
        projects = zanata.projects.list()
        
        if not projects:
            self.log.error("There is no projects on the server or the server not working")
            sys.exit(1)
        for project in projects:
            print ("\nProject ID:          %s")%project.id
            print ("Project Name:        %s")%project.name
            print ("Project Type:        %s")%project.type
            print ("Project Links:       %s\n")%[{'href':link.href, 'type':link.type, 'rel':link.rel} for link in project.links]
        
    def project_info(self, zanata, project_id):
        """
        Retrieve the information of a project
        """
        try:
            p = zanata.projects.get(project_id)
            print ("Project ID:          %s")%p.id
            print ("Project Name:        %s")%p.name 
            print ("Project Type:        %s")%p.type
            print ("Project Description: %s")%p.description
        except NoSuchProjectException, e:
            self.log.error("There is no Such Project on the server")
        except InvalidOptionException, e:
            self.log.error("Options are not valid")
               
    def version_info(self, zanata, project_id, iteration_id):
        """
        Retrieve the information of a project iteration.
        """
        try:
            project = zanata.projects.get(project_id)
            iteration = project.get_iteration(iteration_id)
            print ("Version ID:          %s")%iteration.id
            if hasattr(iteration, 'name'):
                print ("Version Name:        %s")%iteration.name
            if hasattr(iteration, 'description'):
                print ("Version Description: %s")%iteration.description
        except NoSuchProjectException, e:
            self.log.error("There is no such project or version on the server")

    def create_project(self, args):
        """
        Create project with the project id, project name and project description
        @param args: project id
        """
        try:
            item = {'id':args[0], 'name':options['project_name'], 'desc':options['project_desc']}
            p = Project(item)
            result = zanata.projects.create(p)
            if result == "Success":
                self.log.info("Successfully created project: %s"%args[0])
        except NoSuchProjectException, e:
            self.log.error(e.msg) 
        except UnAuthorizedException, e:
            self.log.error(e.msg)
        except ProjectExistException, e:
            self.log.error(e.msg)

    def create_version(self, version_id, version_name, version_desc):
        """
        Create version with the version id, version name and version description 
        @param args: version id
        """
        try:
            item = {'id':version_id, 'name':version_name, 'desc':version_desc}
            iteration = Iteration(item)
            result = zanata.projects.iterations.create(project_id, iteration)
            if result == "Success":
                self.log.info("Successfully created version: %s"%args[0])
        except ProjectExistException, e:
            self.log.error(e.msg)
        except NoSuchProjectException, e:
            self.log.error(e.msg)
        except UnAuthorizedException, e:
            self.log.error(e.msg)
        except InvalidOptionException, e:
            self.log.error(e.msg)
        except NotAllowedException, e:
            self.log.error(e.msg)

    def import_po(self, trans_folder, lang_list, project_config, merge, project_type):
        for item in lang_list:
            self.log.info("Pushing translation for %s to server:"%item)
            if item in project_config['locale_map']:
                lang = project_config['locale_map'][item]
            else:
                lang = item

        locale_folder = os.path.join(trans_folder, item)
        body = self._convert_docbookpo()
            
        self._commit_translation()

    def push_command(self, srcfolder, zanata, project_type):
        """
        Push the content of publican files to a Project version on Zanata/Flies server
        @param args: name of the publican file
        """
        copytrans = True
        project_id, iteration_id = self._check_project(zanata, command_options, project_config)

        self.log.info("Source language: en-US")

        if command_options.has_key('nocopytrans'):
            copytrans = False
            self.log.info("Copy previous translations:%s"%copytrans)
        
        """
        if command_options.has_key('importpo'):        
            self.log.info("Importing translation")
            if command_options.has_key('dir'):
                trans_folder = options['dir']
            elif command_options.has_key('transdir'):
                trans_folder = options['transdir']
            else:
                trans_folder = os.getcwd()
            self.log.info("Reading locale folders from %s"%trans_folder)
        else:
            self.log.info("Importing source documents only")
        
        if command_options.has_key('dir'):
            tmlfolder = os.path.join(command_options['dir'][0]['value'], 'pot')
        elif command_options.has_key('srcdir'):
            tmlfolder = command_options['srcdir'][0]['value']
        else:
            tmlfolder = os.path.join(os.getcwd(), 'pot')
        
        if not os.path.isdir(tmlfolder):
            self.log.error("Can not find source folder, please specify the source folder with '--srcdir' or '--dir' option")
            sys.exit(1)

        self.log.info("POT directory (originals):%s"%tmlfolder)
        """

        #get all the pot files from the template folder 
        publicanutil = PublicanUtility()
        pot_list = publicanutil.get_file_list(srcfolder, ".pot")

        if not pot_list:
            self.log.error("The template folder is empty")
            sys.exit(1)

        self._del_server_content(zanata, project_id, iteration_id, pot_list)

        #if file not specified, push all the files in pot folder to zanata server
        if not args:
            for pot in pot_list:
                self.log.info("\nPushing the content of %s to server:"%pot)
                    
                body, filename = publicanutil.potfile_to_json(pot, srcfolder)
                                          
                try:
                    result = zanata.documents.commit_template(project_id, iteration_id, body, copytrans)
                    if result:
                        self.log.info("Successfully pushed %s to the server"%pot)
                except UnAuthorizedException, e:
                    self.log.error(e.msg)
                    break                                            
                except BadRequestBodyException, e:
                    self.log.error(e.msg)
                    continue
                except SameNameDocumentException, e:
                    self.update_template(zanata, project_id, iteration_id, filename, body)
        else:
            self.log.info("\nPushing the content of %s to server:"%args[0])

            try:
                full_path = self.search_file(tmlfolder, args[0])
            except NoSuchFileException, e:
                self.log.error(e.msg)
                sys.exit(1)
                        
            body, filename = publicanutil.potfile_to_json(full_path, srcfolder)
            
            try:
                result = zanata.documents.commit_template(project_id, iteration_id, body, copytrans)                
                if result:
                    self.log.info("Successfully pushed %s to the server"%args[0])
            except UnAuthorizedException, e:
                self.log.error(e.msg)    
            except BadRequestBodyException, e:
                self.log.error(e.msg)
            except SameNameDocumentException, e:
                self.update_template(project_id, iteration_id, filename, body)   

    def pull_command(self, args):
        """
        Retrieve the content of documents in a Project version from Zanata/Flies server. If the name of publican
        file is specified, the content of that file will be pulled from server. Otherwise, all the document of that
        Project iteration will be pulled from server.
        @param args: the name of publican file
        """
        zanata = self._generate_zanataresource(url, user_name, apikey)
        project_id, iteration_id = self.check_project(zanata, command_options, project_config)

        lang_list = self.get_lang_list()
        
        #list the files in project
        try:
            filelist = zanata.documents.get_file_list(project_id, iteration_id)
        except Exception, e:
            self.log.error(str(e))
            sys.exit(1)

        publicanutil = PublicanUtility()
        
        #if file no specified, retrieve all the files of project
        if not args:
            if filelist:
                for file in filelist:
                    pot = ''
                    result = ''
                    folder = ''

                    if '/' in file: 
                        name = file.split('/')[-1]
                        folder = file.split('/')[0]
                        request_name = file.replace('/', ',')
                    else:
                        name = file
                        request_name = file

                    self.log.info("\nFetching the content of %s from Zanata/Flies server: "%name)                    
                    
                    for item in lang_list:
                        if item in self.project_config['locale_map']:
                            lang = self.project_config['locale_map'][item]
                        else:
                            lang = item
                    
                        create_outpath
                        """                        
                        if options['dir']:
                            if os.path.isdir(options['dir']):
                                outpath = os.path.join(options['dir'], item)
                            else:
                                self.log.error("The destination folder does not exist, please create it")
                                sys.exit(1)
                        elif options['dstdir']:
                            if os.path.isdir(options['dstdir']):
                                outpath = os.path.join(options['dstdir'], item)
                            else:
                                self.log.error("The destination folder does not exist, please create it")
                                sys.exit(1)
                        else:
                            outpath = os.path.join(os.getcwd(), item)
                        
                        if not os.path.isdir(outpath):
                            os.mkdir(outpath) 
                        """                       

                        self.log.info("Retrieving %s translation from server:"%item)

                        try:
                            pot = zanata.documents.retrieve_template(project_id, iteration_id, request_name)                    
                        except UnAuthorizedException, e:
                            self.log.error(e.msg)
                            break
                        except UnAvaliableResourceException, e:
                            self.log.error("Can't find pot file for %s on server"%name)
                            break
                
                        try:
                            result = zanata.documents.retrieve_translation(lang, project_id, iteration_id, request_name)
                        except UnAuthorizedException, e:
                            self.log.error(e.msg)                        
                            break
                        except UnAvaliableResourceException, e:
                            self.log.info("There is no %s translation for %s"%(item, name))
                        except BadRequestBodyException, e:
                            self.log.error(e.msg)
                            continue 
                        
                        if folder:
                            subdirectory = os.path.join(outpath, folder)
                            if not os.path.isdir(subdirectory):
                                os.makedirs(subdirectory)
                            pofile = os.path.join(subdirectory, name+'.po') 
                        else:
                            pofile = os.path.join(outpath, name+'.po')
  
                        try:
                            publicanutil.save_to_pofile(pofile, result, pot)
                        except InvalidPOTFileException, e:
                            self.log.error("Can't generate po file for %s,"%name+e.msg)
        else:
            self.log.info("\nFetching the content of %s from server: "%args[0])
            for item in lang_list:
                result = ''
                pot = ''
                folder = ''

                if item in self.project_config['locale_map']:
                    lang = self.project_config['locale_map'][item]
                else:
                    lang = item
                
                """        
                if options['dir']:
                    if os.path.isdir(options['dir']):
                        outpath = os.path.join(options['dir'], item)
                    else:
                        self.log.error("The destination folder does not exist, please create it")
                elif options['dstdir']:
                    if os.path.isdir(options['dstdir']):
                        outpath = os.path.join(options['dstdir'], item)
                    else:
                        self.log.error("The destination folder does not exist, please create it")
                        sys.exit(1)
                else:
                    outpath = os.path.join(os.getcwd(), item)

                if not os.path.isdir(outpath):
                    os.mkdir(outpath)
                """

                self.log.info("Retrieve %s translation from server:"%item)
                """
                request_name = ''
                for file in filelist:
                    if '/' in file: 
                        name = file.split('/')[-1]
                        folder = file.split('/')[0]
                        if args[0] == name:
                            request_name = file.replace('/', ',')
                            outpath = os.path.join(outpath, folder)   
                            if not os.path.isdir(outpath):
                                os.makedirs(outpath)
                            break
                    else:
                        if args[0] == file:
                            request_name = file
                            break
                
                if not request_name:
                    self.log.error("Can't find pot file for %s on server"%args[0])
                    sys.exit(1)
                """
                pofile = os.path.join(outpath, args[0]+'.po')
                                          
                try:
                    pot = zanata.documents.retrieve_template(project_id, iteration_id, request_name)                    
                except UnAuthorizedException, e:
                    self.log.error(e.msg)
                    sys.exit(1)
                except UnAvaliableResourceException, e:
                    self.log.error("Can't find pot file for %s on server"%args[0])
                    sys.exit(1)

                try:            
                    result = zanata.documents.retrieve_translation(lang, project_id, iteration_id, request_name)
                except UnAuthorizedException, e:
                    self.log.error(e.msg)
                    sys.exit(1)
                except UnAvaliableResourceException, e:
                    self.log.info("There is no %s translation for %s"%(item, args[0]))
                except BadRequestBodyException, e:
                    self.log.error(e.msg)
                    continue 
      
                try:
                    publicanutil.save_to_pofile(pofile, result, pot)                    
                except InvalidPOTFileException, e:
                    self.log.error("Can't generate po file for %s,"%args[0]+e.msg)   
            
