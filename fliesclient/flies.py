#!/usr/bin/env python
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

class FliesConsole:
    def __init__(self, opts, args):
    	config = FliesConfig()
    	self.server = config.get_config_value("server")
    	self.roject_id = config.get_config_value("project.id")
    	self.iteration_id = config.get_config_value("project.iteration.id") 
    	self.user = config.get_config_value("user")
    	self.apikey = config.get_config_value("apikey")
    	name = ''
    	desc = ''
        
        for o, a in opts:
           if o in ("--server"):
               self.server = a
           elif o in ("--name"):
               self.name = a
           elif o in ("--description"):
               self.desc = a
           elif o in ("--project"):
               self.project_id = a
           elif o in ("--iteration"):
               self.iteration_id = a
           else:
               assert False
    
    	self.command, self.args = args[0], args[1:]
    
    def _PrintUsage():
        print ('\nClient for talking to a Flies Server\n'
               'basic command:\n'
               'flies list        List all available projects\n'
               "Use 'flies help' for the full list of commands\n")

    def _PrintHelpInfo(self):
        print ('\nUsage:\n'
               'flies list                                                               List all available projects\n'
               'flies projectinfo --project=project_id                                            Retrieve a project\n'
               'flies iterationinfo|info --project=project_id --iteration=iteration_id            Retrieve a iteration\n'
               'flies create project project_id --name=project_name --description=project_desc    Create a project\n'
               'flies create iteration iteration_id --project=project_id --name=itertation_name   Create a iteration of a project\n'   
               'flies publican pull                                                               Pull the content of publican file\n'
               'flies publican push                                                      Push the content of publican to Flies Server\n')
          
    def _ListProjects(self):
        if not self.server:
           print "Please provide valid server url by fliesrc or by '--server' option"
           sys.exit()
        
        flies = FliesClient(self.server)
        res, content = flies.ListProjects()
        print 'Status: '+res['status']
        if res.get('status') == '200':
            projects = json.loads(content)
            for project in projects:
                print "*"*40
                print project
        else:
            print 'Flies REST service not available at %s' % server
        
    def _GetProject(self):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        if not self.project_id:
            print 'Please use flies projectinfo --project=project_id to retrieve the project info'
            sys.exit()
        flies = FliesClient(self.server)
        res, content = flies.GetProjectInfo(self.project_id)
        print 'Status: '+res['status']
        print content
        
    def _GetIteration(self):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        if not self.iteration_id or not self.project_id:
            print 'Please use flies iterationinfo|info --project=project_id --iteration=iteration_id to retrieve the iteration'
        flies = FliesClient(self.server)
        res, content = flies.GetIterationInfo(self.project_id, self.iteration_id)
        print 'Status: '+res['status']
        print content
                
    def _CreateProject(server, id, name, user, apikey, desc = None):
        if not server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        if len(args) < 2:
            print "Error: Not enough arguments for executing command"
            sys.exit()  
    
        if user and apikey :
            flies = Flies(server, user, apikey)
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
    
        try:
            result = flies.create_project(id, name, desc)
            print "Create project success"
        except InvalidOptionException, e:
            print "Error: Invalid Option",

    def _CreateIteration(server, id, name, user, apikey, project_id, desc = None):
        if user and apikey :
            flies = Flies(server, user, apikey)
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
    
        try:
            result = flies.create_iteration(project_id, id, name, desc)
            print "Create iteration of project success"
        except InvalidOptionException, e:
            print "Error: Invalid Option"     

    def Run(self):
        if self.command == 'help':
            self._PrintHelpInfo()
        elif self.command == 'list':
            self._ListProjects()
        elif self.command == 'projectinfo':
            self._GetProject()
        elif self.command == 'iterationinfo' or self.command == 'info':
            self._GetIteration() 
        elif self.command == 'create':
            if args[0] == 'project':
                self._CreateProject()
            elif self.args[0] == 'iteration':
                self._CreateIteration()
            else:
                print "Error: No such command"
        elif self.command == 'po':
            process_po(args) 
        elif self.command == 'publican': 
            process_publican(args)
        else:
            self._PrintHelpInfo()
            sys.exit(2)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["server=", "project=", "iteration=", "name=", "description="])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    
    client = FliesConsole(opts, args)
    client.Run()

if __name__ == "__main__":
      main()       
