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

from publicanutil import PublicanUtility
from csvconverter import CSVConverter
from zanatalib.glossaryservice import GlossaryService
from zanatalib.project import Project
from zanatalib.project import Iteration
from zanatalib.logger import Logger 
from zanatalib.error import NoSuchProjectException
from zanatalib.error import UnAuthorizedException
from zanatalib.error import UnAvaliableResourceException
from zanatalib.error import BadRequestBodyException
from zanatalib.error import SameNameDocumentException
from zanatalib.error import InvalidOptionException
from zanatalib.error import NotAllowedException
from zanatalib.error import ProjectExistException
from zanatalib.error import UnexpectedStatusException
from zanatalib.error import UnavailableServiceError

class ZanataCommand:
    def __init__(self):
        self.log = Logger()

    ##############################################
    ##
    ## Commands for interaction with zanata server 
    ##
    ############################################## 
    def check_project(self, zanataclient, command_options, project_config):
        project_id = ''
        iteration_id = ''
        if command_options.has_key('project_id'):
            project_id =  command_options['project_id'][0]['value'] 
        else:
            if project_config.has_key('project_id'):
                project_id = project_config['project_id']
        
        if command_options.has_key('project_version'):
            iteration_id = command_options['project_version'][0]['value'] 
        else:
            if project_config.has_key('project_version'):
                iteration_id = project_config['project_version']
        
        if not project_id:
            self.log.error("Please specify a valid project id in zanata.xml or with '--project-id' option")
            sys.exit(1)
        
        if not iteration_id:
            self.log.error("Please specify a valid version id in zanata.xml or with '--project-version' option")
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
        except UnexpectedStatusException, e:
            self.log.error(e.msg)

    def update_template(self, zanata, project_id, iteration_id, filename, body, copytrans):
        if '/' in filename:
            request_name = filename.replace('/', ',')
        else:
            request_name = filename
        
        try:
            result = zanata.documents.update_template(project_id, iteration_id, request_name, body, copytrans)
            if result:
                self.log.info("Successfully updated template %s on the server"%filename)
        except BadRequestBodyException, e:
            self.log.error(e.msg)
        except UnexpectedStatusException, e:
            self.log.error(e.msg)

    def commit_translation(self, zanata, project_id, iteration_id, request_name, pofile, lang, body, merge):
        try:
            result = zanata.documents.commit_translation(project_id, iteration_id, request_name, lang, body, merge)
            if result:
                self.log.warn(result)   
            self.log.info("Successfully pushed translation %s to the Zanata server"%pofile)
        except UnAuthorizedException, e:
            self.log.error(e.msg)                                            
        except BadRequestBodyException, e:
            self.log.error(e.msg)
        except UnexpectedStatusException, e:
            self.log.error(e.msg)

    def del_server_content(self, zanata, tmlfolder, project_id, iteration_id, push_files, force, project_type):
        #Get the file list of this version of project
        try:
            filelist = zanata.documents.get_file_list(project_id, iteration_id)
        except Exception, e:
            self.log.error(str(e))
            sys.exit(1)

        if filelist:
            self.log.info("This will overwrite/delete any existing documents on the server.")
            if not force:
                while True:
                    option = raw_input("Are you sure (y/n)?")
                    if option.lower() == "yes" or option.lower() == "y":
                        break    
                    elif option.lower() == "no" or option.lower() == "n":
                        self.log.info("Processing stopped, keeping existing content on the server")
                        sys.exit(1)
                    else:
                        self.log.error("Please enter yes(y) or no(n)")

            for name in filelist:
                delete = False
                if ',' in name: 
                    request = name.replace(',', '\,')
                elif '/' in name:
                    request = name.replace('/', ',')
                else:
                    request = name

                if ".pot" in name:
                    path = os.path.join(tmlfolder, name)
                else:
                    path = os.path.join(tmlfolder, name+".pot")

                if project_type== "gettext":
                    if push_files:
                        if path not in push_files:
                            delete = True
                elif project_type=="podir":
                    if not os.path.exists(path):
                        delete = True

                if delete:
                    self.log.info("Delete the %s"%name)

                    try:
                        zanata.documents.delete_template(project_id, iteration_id, request)
                    except Exception, e:
                        self.log.error(str(e))
                        sys.exit(1)
  
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

        return projects
        
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
        except NoSuchProjectException:
            self.log.error("There is no Such Project on the server")
        except InvalidOptionException:
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
        except NoSuchProjectException:
            self.log.error("There is no such project or version on the server")

    def create_project(self, zanata, project_id, project_name, project_desc):
        """
        Create project with the project id, project name and project description
        @param args: project id
        """
        try:
            item = {'id':project_id, 'name':project_name, 'desc':project_desc}
            p = Project(item)
            result = zanata.projects.create(p)
            if result == "Success":
                self.log.info("Successfully created project: %s"%project_id)
        except NoSuchProjectException, e:
            self.log.error(e.msg) 
        except UnAuthorizedException, e:
            self.log.error(e.msg)
        except ProjectExistException, e:
            self.log.error(e.msg)

    def create_version(self, zanata, project_id, version_id, version_name=None, version_desc=None):
        """
        Create version with the version id, version name and version description 
        @param args: version id
        """
        try:
            item = {'id':version_id, 'name':version_name, 'desc':version_desc}
            iteration = Iteration(item)
            result = zanata.projects.iterations.create(project_id, iteration)
            if result == "Success":
                self.log.info("Successfully created version: %s"%version_id)
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

    def import_po(self, zanata, potfile, trans_folder, project_id, iteration_id, lang_list, locale_map, merge, project_type):
        sub_dir = ""        
        publicanutil = PublicanUtility()        
        for item in lang_list:
            if not locale_map:
                lang = item
            else:
                if item in locale_map:
                    lang = locale_map[item]
                else:
                    lang = item
            
            if '/' in potfile:
                request_name = potfile.replace('/', ',')
                sub_dir = potfile.split('/')[0]
            else:
                request_name = potfile

            self.log.info("Pushing %s translation for %s to server:"%(item, potfile))

            if project_type == "podir":
                folder = os.path.join(trans_folder, item)
                    
                if not os.path.isdir(folder):
                    self.log.error("Can not find translation, please specify path of the translation folder")
                    continue  

                pofile = os.path.join(folder, potfile+'.po') 

            elif project_type == "gettext":
                filename = item.replace('-','_')+'.po'
                if sub_dir:
                    path = os.path.join(trans_folder, sub_dir)
                else:
                    path = trans_folder
                pofile = os.path.join(path, filename)  
                
            if not os.path.isfile(pofile):
                self.log.error("Can not find the %s translation for %s"%(item, potfile))
                continue
                        
            body = publicanutil.pofile_to_json(pofile)           
    
            if not body:
                self.log.error("No content or all entries are obsolete in %s"%pofile)
                sys.exit(1)
            
            self.commit_translation(zanata, project_id, iteration_id, request_name, pofile, lang, body, merge)

    def push_command(self, zanata, file_list, srcfolder, project_id, iteration_id, copytrans, import_param = None):
        """
        Push the content of publican files to a Project version on Zanata server
        @param args: name of the publican file
        """
        publicanutil = PublicanUtility()

        for filepath in file_list:
            self.log.info("\nPushing the content of %s to server:"%filepath)
            body, filename = publicanutil.potfile_to_json(filepath, srcfolder)
                                          
            try:
                result = zanata.documents.commit_template(project_id, iteration_id, body, copytrans)
                if result:
                    self.log.info("Successfully pushed %s to the server"%filepath)
            except UnAuthorizedException, e:
                self.log.error(e.msg)
                break                             
            except BadRequestBodyException, e:
                self.log.error(e.msg)
                continue
            except SameNameDocumentException, e:
                self.update_template(zanata, project_id, iteration_id, filename, body, copytrans)
            except UnexpectedStatusException, e:
                self.log.error(e.msg)
                continue
            
            if import_param:
                merge = import_param['merge']
                lang_list = import_param['lang_list']
                project_type = import_param['project_type']
                transdir = import_param['transdir']
                locale_map = import_param['locale_map']
      
                self.import_po(zanata, filename, transdir, project_id, iteration_id, lang_list, locale_map, merge, project_type)

    def pull_command(self, zanata, locale_map, project_id, iteration_id, filelist, lang_list, output, project_type):
        """
        Retrieve the content of documents in a Project version from Zanata server. If the name of publican
        file is specified, the content of that file will be pulled from server. Otherwise, all the document of that
        Project iteration will be pulled from server.
        @param args: the name of publican file
        """
        publicanutil = PublicanUtility()
        #if file no specified, retrieve all the files of project
        for file_item in filelist:
            pot = ""
            result = ""
            folder = ""

            if '/' in file_item: 
                name = file_item.split('/')[-1]
                folder = file_item.split('/')[0]
                request_name = file_item.replace('/', ',')
            else:
                name = file_item
                request_name = file_item

            self.log.info("\nFetching the content of %s from Zanata server: "%name)                    
                    
            for item in lang_list:
                if not locale_map:
                    lang = item
                else:
                    if item in locale_map:
                        lang = locale_map[item]
                    else:
                        lang = item
                    
                if project_type == "podir":
                    outpath = os.path.join(output, item) 
                    if not os.path.isdir(outpath):
                        os.mkdir(outpath)  
                    save_name = name
                elif project_type == "gettext":
                    outpath = output
                    save_name = item.replace('-','_')
                                        
                if folder:
                    subdirectory = os.path.join(outpath, folder)
                    if not os.path.isdir(subdirectory):
                        os.makedirs(subdirectory)
                    pofile = os.path.join(subdirectory, save_name+'.po') 
                else:
                    pofile = os.path.join(outpath, save_name+'.po')

                self.log.info("Retrieving %s translation from server:"%item)

                try:
                    pot = zanata.documents.retrieve_template(project_id, iteration_id, request_name)                    
                except UnAuthorizedException, e:
                    self.log.error(e.msg)
                    break
                except UnAvaliableResourceException, e:
                    self.log.error("Can't find pot file for %s on server"%name)
                    break
                except UnexpectedStatusException, e:
                    self.log.error(e.msg)
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
                except UnexpectedStatusException, e:
                    self.log.error(e.msg)
     
                publicanutil.save_to_pofile(pofile, result, pot)
    
    def poglossary_push(self, path, url, username, apikey, lang, sourcecomments):
        publicanutil = PublicanUtility()
        json = publicanutil.glossary_to_json(path, lang, sourcecomments)
        glossary = GlossaryService(url)

        try:
            content = glossary.commit_glossary(username, apikey, json)
            if content:
                self.log.info("Successfully pushed glossary to the server")
        except UnAvaliableResourceException:
            self.log.error("Can not push")
        except UnavailableServiceError:
            self.log.error("Service Temporarily Unavailable, stop processing!")
        except BadRequestBodyException, e:
            self.log.error(e.msg)
        except UnexpectedStatusException, e:
            self.log.error(e.msg)
        except UnAuthorizedException,e:
            self.log.error(e.msg)

    def csvglossary_push(self, path, url, username, apikey, locale_map, comments_header):
        csvconverter = CSVConverter()
        json = csvconverter.convert_to_json(path, locale_map, comments_header)        
        glossary = GlossaryService(url)

        try:
            content = glossary.commit_glossary(username, apikey, json)
            if content:
                self.log.info("Successfully pushed glossary to the server")
        except UnAvaliableResourceException:
            self.log.error("Can not push")
        except UnavailableServiceError:
            self.log.error("Service Temporarily Unavailable, stop processing!")
        except BadRequestBodyException, e:
            self.log.error(e.msg)
        except UnexpectedStatusException, e:
            self.log.error(e.msg)
        except UnAuthorizedException,e:
            self.log.error(e.msg)
