#!/usr/bin/env python
#
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

import getopt, sys
import json
import os.path
from parseconfig import FliesConfig
from flieslib.client import FliesClient
from flieslib.client import NoSuchFileException
from flieslib.client import NoSuchProjectException
from flieslib.client import UnAuthorizedException

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
        self.options = {
                        'server' : server,
                        'project_id':project_id,
                        'iteration_id':iteration_id,
                        'user':user,
                        'apikey':apikey
                        }
     
    def _PrintUsage(self):
        print ('\nClient for talking to a Flies Server\n\n'
               'basic commands:\n\n'
               'list             List all available projects\n'
               'projectinfo      Retrieve a project\n'
               'iterationinfo    Retrieve a iteration\n\n'
               "Use 'flies help' for the full list of commands")

    def _print_help_info(self, args):
        if not args:
            print ('Client for talking to a Flies Server:\n\n'
                  'list of commands:\n\n'
                  ' list                List all available projects\n'
                  ' projectinfo         Retrieve a project\n'
                  ' iterationinfo       Retrieve a iteration\n'
                  ' create project      Create a project\n'
                  ' create iteration    Create a iteration of a project\n'   
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican to Flies Server\n')
        else:
            if args[0] == 'list':
                self._print_list_help()
    
    def _print_list_help(self):
       	print ('flies list [OPTIONS]\n\n'
               'list all available projects\n\n'
               'options:\n\n'
               ' --server url address of the Flies server')
    
    def _PrintProjectInfoHelp(self):
	    print ('flies project info [OPTIONS]')

    def _PrintProjectCreateHelp(self):
        print ('flies project create [PROJECT_ID] [OPTIONS]') 

    def _PrintIterationInfoHelp(self):
	    print ('flies iterationinfo [OPTIONS]')

    def _PrintIterationCreateHelp(self):
        print ('flies create iteration [ITERATION_ID] [OPTIONS]')
           
               
    def _list_projects(self):
        if not self.options['server']:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        
        flies = FliesClient(self.options['server'])
        res, content = flies.list_projects()
        print 'Status: '+res['status']
        if res.get('status') == '200':
            projects = json.loads(content)
            for project in projects:
                print "*"*40
                print project
        else:
            print 'Flies REST service not available at %s' % self.server
        
    def _get_project(self):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()

        if not self.project_id:
            print 'Please use flies project info --project=project_id to retrieve the project info'
            sys.exit()
        
        flies = FliesClient(self.server)
        res, content = flies.get_project_info(project_id)
        print 'Status: '+res['status']
        print content
        
    def _get_iteration(self):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        
        if not self.iteration_id or not self.project_id:
            print 'Please use flies iterationinfo|info --project=project_id --iteration=iteration_id to retrieve the iteration'
        
        flies = FliesClient(self.server)
        res, content = flies.get_iteration_info(self.project_id, self.iteration_id)
        print 'Status: '+res['status']
        print content
                
    def _create_project(self, args):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
    
        if self.user and self.apikey:
            flies = FliesClient(self.server, self.user, self.apikey)
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
        
        try:
            result = flies.create_project(project_id, self.name, self.desc)
        except NoSuchProjectException as e:
            print "No Such Project on the server" 
        except UnAuthorizedException as e:
            print "Unauthorized Operation"

    def _create_iteration(self, args):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()

        if self.user and self.apikey:
            flies = FliesClient(self.server, self.user, self.apikey)
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
        
        if not self.project_id:
            print "Please provide PROJECT_ID for creating iteration"
            sys.exit()
        
        try:
            result = flies.create_iteration(self.project_id, self.args[0], self.name, self.desc)
        except NoSuchProjectException as e:
            print "No Such Project on the server"

    def _push_publican(self, filename):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        
        if self.user and self.apikey:
            flies = FliesClient(self.server, self.user, self.apikey)
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()

        if not self.project_id:
            print "Please provide PROJECT_ID for creating iteration"
            sys.exit()

        try:
       	    result = flies.push_publican(filename, self.project_id, self.iteration_id)
        except NoSuchFileException as e:
       	    print "Can not find file"
        except NoSuchProjectException as e:
            print "No Such Project on the server"

    def _pull_publican(self):
        pass

    def _remove_project(self):
        pass

    def _remove_iteration(self):
        pass

    def _project_status(self):
        pass
    
    def _process_command_line(self):
        try:
            opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["server=", "project=", "iteration=", "name=", "description="])
        except getopt.GetoptError, err:
            print str(err)
            sys.exit(2)

        if args:
            command = args[0]
            sub = args[1:]            
            if sub_command[command]:
                if sub[0]:
                    if sub[0] in sub_command[command]:
                        command = command+'_'+sub[0]
                        command_args = sub[2:]
                    else:
                        print "Can not find such command"
                else:
                    print "Please complete the command!"      
            else: 
                command_args = sub           
        else:
            self._PrintUsage()
            sys.exit(2)
                         
        if opts:
            for o, a in opts:
                if o in ("--server"):
                    self.options[server] = a
                elif o in ("--name"):
                    self.options[name] = a
                elif o in ("--description"):
                    self.options[desc] = a
                elif o in ("--project"):
                    self.options[project_id] = a
                elif o in ("--iteration"):
                    self.options[iteration_id] = a
    
        return command, command_args
 
    def run(self):
        command, command_args = self._process_command_line()        
        
        if command == 'help':
            self._print_help_info(command_args)
        elif command == 'list':
            self._list_projects()
        elif command == 'status':
            self._poject_status()
        elif command == 'project_info':
            self._GetProject()
        elif command == 'project_create':
            self._create_project(command_args)
        elif command == 'project_remove':
            self._remove_project(command_args)
        elif command == 'iteration_info':
            self._GetIteration(options)
        elif command == 'iteration_create':
            self._create_iteration(command_args)
        elif command == 'iteration_remove':
            self._remove_iteration(command_args)
        elif command == 'publican_push':
            self._push_publican(comand_args)
        elif command == 'publican_pull':
            self._push_publican(comand_args)      
        else:
            self._PrintUsage()
            sys.exit(2)

def main():
    client = FliesConsole()
    client.run()

if __name__ == "__main__":
    main()       
