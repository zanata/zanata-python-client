#!/usr/bin/env python
import getopt, sys
import ConfigParser
import json
import os.path
from flieslib import Flies 

def usage():
    print '''Client for talking to a Flies Server
    basic command:
    flies list        List all available projects
    Use 'flies help' for the full list of commands'''

def helpmessage():
    print '''Usage:
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

def get_config_var():
    projectconfig = "./.fliesrc"
    config = ConfigParser.ConfigParser()
    configfile = config.read([projectconfig, os.path.expanduser("~/.fliesrc")])
    if configfile:
       server = config.get('Config', 'server')
       projectid = config.get('Config', 'project.id')
       iterationid = config.get('Config', 'project.iteration.id')
       user = config.get('Config', 'user')
       apikey = config.get('Config', 'apikey')
       return server, projectid, iterationid, user, apikey
    else:
       print "Can not find valid fliesrc file on the system"  
       sys.exit()  
 
def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "v", ["server=", "project=", "iteration=", "name=", "description="])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    serverurl, projectid, iterationid, user, apikey = get_config_var() 
    
    if len(args) == 0:
       if len(opts) == 0:
          usage()
          sys.exit()
    elif len(args) > 0:
       if args[0] == 'help':
          helpmessage()
          sys.exit()
       else: 
          serveroption = ''
          projectname = ''
          desc = ''
          
          for o, a in opts:
              if o == "--server":
                 serveroption = a
              elif o == "--name":
                 name = a
              elif o == "--description":
                 desc = a
              elif o == '--project':
                 id = a
              elif o == '--iteration':
                 iteration = a
          
          server = serverurl or serveroption
                    
          if args[0] == 'list':
              if server:
                flies = Flies(server, None, None)
              else:
                "Please use --server option to set server url"
                sys.exit()
              res, content = flies.get_projects()
              print 'Status: '+res['status']
              if res.get('status') == '200':
                projects = json.loads(content)
              for project in projects:
                 print "*"*40
                 print project
          elif args[0] == 'projectinfo':
              if server:
                flies = Flies(server, None, None)
              else:
                "Please use --server option to set server url"
                sys.exit()
              if len(opts) < 1:
                 print 'Please use flies projectinfo --project=project_id to retrieve the project info'
              else:
                 res, content = flies.get_project_info(id)
                 print 'Status: '+res['status']
                 print content
          elif args[0] == 'iterationinfo' or args[0] == 'info' :
              if server:
                 flies = Flies(server, None, None)
              else:
                 "Please use --server option to set server url"
                 sys.exit()
              if len(opts) < 2:
                 print 'Please use flies iterationinfo|info --project=project_id --iteration=iteration_id to retrieve the iteration'
              else:
                 res, content = flies.get_iteration_info(id, iteration)
                 print 'Status: '+res['status']
                 print content
          elif args[0] == 'create':
               if server and user and apikey :
                  flies = Flies(server, user, apikey)
               else:
                  print "Please provide username and apikey in .fliesrc"
                  sys.exit()
 
               if len(args) == 3:
                  if args[1] == 'project':
                     if len(opts) < 2:
                       print "Please provide valid options: '--name=project_name --desc=project_description'"             
                     else:   
                        try:
                           result = flies.create_project(args[2], name, desc)
                           if result:
                              "Create project success"
                        except Exception as detail:
                           print "Error:", detail
                  elif args[1] == 'iteration':
                     if len(opts) < 3:
                        print "Please provide valid options: '--project=project_id --name=iteration_name --desc=iteration_description'"
                     else:
                        try:
                           result = flies.create_iteration(id, args[2], name, desc)
                           if result:
                              print "Create iteration of project success"
                        except Exception as detail:
                           print "Error:", detail   
                  else:
                     print "Error: No such command"
               else:
                     print "Error: Not enough arguments for executing command"
          elif args[0] == 'po':
               if args[1] == 'pull': 
       	          print "Pull the content of PO"
               elif args[1] == 'push':
                  print "Push the content of PO"
          elif args[0] == 'publican': 
               if args[1] == 'pull':
	          print "Pull the content of publican"
               elif args[1] == 'push':
                  print "Push the content of publican"
          else:
              helpmessage()
              sys.exit()           

if __name__ == "__main__":
        main()       
