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

class FliesConsole:

    def __init__(self, opts, args):
    	config = FliesConfig()
    	self.server = config.get_config_value("server")
    	self.project_id = config.get_config_value("project.id")
    	self.iteration_id = config.get_config_value("project.iteration.id") 
    	self.user = config.get_config_value("user")
    	self.apikey = config.get_config_value("apikey")
        self.name = '' 
    	self.desc = ''
        self.args = args      
         
        if opts:
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
     
    def _PrintUsage(self):
        print ('\nClient for talking to a Flies Server\n\n'
               'basic commands:\n\n'
               'list             List all available projects\n'
               'projectinfo      Retrieve a project\n'
               'iterationinfo    Retrieve a iteration\n\n'
               "Use 'flies help' for the full list of commands")

    def _PrintHelpInfo(self):
        print ('Client for talking to a Flies Server:\n\n'
                  'list of commands:\n\n'
                  ' list                List all available projects\n'
                  ' projectinfo         Retrieve a project\n'
                  ' iterationinfo       Retrieve a iteration\n'
                  ' create project      Create a project\n'
                  ' create iteration    Create a iteration of a project\n'   
                  ' publican pull       Pull the content of publican file\n'
                  ' publican push       Push the content of publican to Flies Server\n')
    def _PrintListHelp(self):
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
           
               
    def _ListProjects(self):
        if not self.server:
           print "Please provide valid server url by fliesrc or by '--server' option"
           sys.exit()
        
        flies = FliesClient(self.server)
        res, content = flies.list_projects()
        print 'Status: '+res['status']
        if res.get('status') == '200':
            projects = json.loads(content)
            for project in projects:
                print "*"*40
                print project
        else:
            print 'Flies REST service not available at %s' % self.server
        
    def _GetProject(self):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        if not self.project_id:
            print 'Please use flies project info --project=project_id to retrieve the project info'
            sys.exit()
        print self.project_id
        flies = FliesClient(self.server)
        res, content = flies.get_project_info(self.project_id)
        print 'Status: '+res['status']
        print content
        
    def _GetIteration(self):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
        if not self.iteration_id or not self.project_id:
            print 'Please use flies iterationinfo|info --project=project_id --iteration=iteration_id to retrieve the iteration'
        flies = FliesClient(self.server)
        res, content = flies.get_iteration_info(self.project_id, self.iteration_id)
        print 'Status: '+res['status']
        print content
                
    def _CreateProject(self, project_id):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()
    
        if self.user and self.apikey :
            flies = FliesClient(self.server, self.user, self.apikey)
        else:
            print "Please provide username and apikey in .fliesrc"
            sys.exit()
        
        try:
               result = flies.create_project(project_id, self.name, self.desc)
        except NoSuchProjectException as e:
               print "No Such Project on the server" 

    def _CreateIteration(self):
        if not self.server:
            print "Please provide valid server url by fliesrc or by '--server' option"
            sys.exit()

        if self.user and self.apikey :
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

    def _PushPublican(self):
	if not self.server:
        	print "Please provide valid server url by fliesrc or by '--server' option"
            	sys.exit()
        
        if self.user and self.apikey :
            	flies = FliesClient(self.server, self.user, self.apikey)
        else:
            	print "Please provide username and apikey in .fliesrc"
            	sys.exit()

        if not self.project_id:
           	print "Please provide PROJECT_ID for creating iteration"
            	sys.exit()

        if len(self.args) == 1:
                print "Please provide POT file name for pushing"
        else:
           try:
           	result = flies.push_publican(self.args[1], self.project_id, self.iteration_id)
           except NoSuchFileException as e:
           	print "Can not find file"
           except NoSuchProjectException as e:
                print "No Such Project on the server"

    def Run(self):
        size = len(self.args) 
       	if self.args[0] == 'help':
           if size ==1:
            	self._PrintHelpInfo()
           else:
                if self.args[1] == 'list':
                   self._PrintListHelpInfo()
        elif self.args[0] == 'list':
            		self._ListProjects()
        elif self.args[0] == 'project':
            		if self.args[1] == 'info':
                                print "oh"	
                   		self._GetProject()
                        elif self.args[1] == 'create':
                		self._CreateProject(self.args[2])

        elif self.args[0] == 'iteration':
                         if self.args[1] == 'info':
                                self._GetIteration()
                         elif self.args[1] == 'create':
                                self._CreateIteration()
                
        elif self.args[0] == 'publican':
                         if self.args[1] == 'push':
            	                self._PushPublican(self.args[2])           
        else:
            self._PrintUsage()
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
