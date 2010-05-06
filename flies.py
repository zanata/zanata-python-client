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
from flieslib import Flies 
from flieslib import InvalidOptionException
from parseconfig import FliesConfig

def usage():
    print 
    '''Client for talking to a Flies Server
    basic command:
    flies list        List all available projects
    Use 'flies help' for the full list of commands'''

def help_message():
    print '''
    Usage:
    flies list                                  list all available projects
    flies projectinfo --project=project_id      Retrieve a project
    flies iterationinfo|info --project=project_id --iteration=iteration_id 
                                                      Retrieve a iteration
    flies create project project_id --name=project_name --description=project_desc
                                                      Create a project
    flies create iteration iteration_id --project=project_id --name=itertation_name
                                                      Create a iteration of a project   
    flies publican pull                         Pull the content of publican file
    flies publican push                         Push the content of publican to Flies Server'''
          
def list_projects(server):
    flies = Flies(server)
    res, content = flies.get_projects()
    print 'Status: '+res['status']
    if res.get('status') == '200':
        projects = json.loads(content)
    for project in projects:
        print "*"*40
        print project
        
def project_info(server, project_id):
    flies = Flies(server)
    res, content = flies.get_project_info(project_id)
    print 'Status: '+res['status']
    print content
        
def iteration_info(server, project_id, iteration_id):
    flies = Flies(server)
    res, content = flies.get_iteration_info(project_id, iteration_id)
    print 'Status: '+res['status']
    print content
                
def create_project(server, id, name, user, apikey, desc = None):
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

def create_iteration(server, id, name, user, apikey, project_id, desc = None):
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

def process_po():
    pass

def process_publican():
    pass

def main():
    config = FliesConfig()
    server = config.get_config_value("server")
    project_id = config.get_config_value("project.id")
    iteration_id = config.get_config_value("project.iteration.id") 
    user = config.get_config_value("user")
    apikey = config.get_config_value("apikey")
    name = ''
    desc = ''
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["server=", "project=", "iteration=", "name=", "description="])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    
    for o, a in opts:
        if o in ("--server"):
            server = a
        elif o in ("--name"):
            name = a
        elif o in ("--description"):
            desc = a
        elif o in ("--project"):
            project_id = a
        elif o in ("--iteration"):
            iteration_id = a
        else:
            assert False
            
    if not server:
        print "Please provide valid server url by fliesrc or by '--server' option"
        sys.exit()
    
    if len(args) == 0:
       usage()
       sys.exit()
    
    command, args = args[0], args[1:]
    
    if command == 'help':
        help_message()
    elif command == 'list':
        list_projects(server)
    elif command == 'projectinfo':
        if not project_id:
            print 'Please use flies projectinfo --project=project_id to retrieve the project info'
            sys.exit()
        project_info(server, project_id)
    elif command == 'iterationinfo' or command == 'info':
        if not iteration_id or not project_id:
            print 'Please use flies iterationinfo|info --project=project_id --iteration=iteration_id to retrieve the iteration'
        iteration_info(server, project_id, iteration_id) 
    elif command == 'create':
        if len(args) < 2:
            print "Error: Not enough arguments for executing command"
            sys.exit()  
        #if not name or not desc:
        #    print "Please provide name and description"
        #    sys.exit()
        if args[0] == 'project':
            create_project(server, args[1], name, user, apikey, desc)
        elif args[0] == 'iteration':
            create_iteration(server, args[1], name, user, apikey, project_id, desc)
        else:
            print "Error: No such command"
    elif command == 'po':
        process_po(args) 
    elif command == 'publican': 
        process_publican(args)
    else:
        help_message()
        sys.exit(2)

if __name__ == "__main__":
        main()       
