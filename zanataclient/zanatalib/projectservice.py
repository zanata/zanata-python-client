# vim:set et sts=4 sw=4:
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
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

__all__ = (
    "ProjectService",
)


from .projectutils import Project
from .projectutils import Iteration
from .service import Service


class ProjectService(Service):
    """
    Provides services to interact with Project, handle operaions of list, create and retrieve Project Resources
    """
    _fields = ['base_url', 'http_headers']

    def __init__(self, *args, **kargs):
        super(ProjectService, self).__init__(*args, **kargs)
        self.iterations = IterationService(
            self.base_url, self.http_headers
        )

    def disable_ssl_cert_validation(self):
        self.restclient.disable_ssl_cert_validation()
        self.iterations.disable_ssl_cert_validation()

    def list(self):
        """
        List the Project Resources on the Zanata server
        @return: list of Project object
        """
        res, content = self.restclient.process_request('list_projects',
                                                       headers=self.http_headers)
        projects_json = self.messages(res, content)
        projects = [Project(p) for p in projects_json]
        return projects

    def get(self, projectid):
        """
        Retrieve a specified Project Resource on Zanata server
        @param projectid: Id of Project Resource
        @return: Project object
        @raise NoSuchProjectException:
        """
        res, content = self.restclient.process_request('list_project', projectid,
                                                       headers=self.http_headers)
        server_return = self.messages(res, content)
        if 'status' in server_return:
            if server_return['status'] == "Retired":
                print("Warning: The project %s is retired!" % projectid)
        project = Project(server_return)
        project.set_iteration(self.iterations)
        return project

    def create(self, project):
        """
        Create a Project Resource on Zanata Server
        @param project: Project object
        @return: Success if status of response is 201
        @raise ProjectExistException:
        @raise NoSuchProjectException:
        @raise UnAuthorizedException:
        @raise BadRequestException:
        """
        body = '''{"name":"%s","id":"%s","description":"%s","type":"%s"}''' % (
            project.name, project.id, project.desc, project.type
        )
        res, content = self.restclient.process_request(
            'create_project', project.id, body=body, headers=self.http_headers
        )
        return self.messages(res, content, "The project is already exist on server")

    def delete(self):
        pass

    def status(self):
        pass


class IterationService(Service):
    """
    Provides services to interact with Project iteration, handle operaions of list, create and retrieve iteration Resources
    """
    _fields = ['base_url', 'http_headers']

    def __init__(self, *args, **kargs):
        super(IterationService, self).__init__(*args, **kargs)

    def disable_ssl_cert_validation(self):
        self.restclient.disable_ssl_cert_validation()

    def get(self, projectid, iterationid):
        """
        Retrieve a specified Iteration Resource on Zanata server
        @param projectid: Id of Project Resource
        @param iterationid: Id of Iteration Resource
        @return: Iteration object
        @raise NoSuchProjectException:
        """
        res, content = self.restclient.process_request('get_iteration', projectid, iterationid,
                                                       headers=self.http_headers)
        server_return = self.messages(res, content)
        if 'status' in server_return:
            if server_return['status'] == "Retired":
                print("Warning: The project %s is retired!" % iterationid)
        return Iteration(server_return)

    def create(self, projectid, iteration):
        """
        Create a Iteration Resource on Zanata Server
        @param projectid: Id of Project Resource
        @param iteration: Iteration object
        @return: Success if status of response is 201
        @raise ProjectExistException:
        @raise NoSuchProjectException:
        @raise UnAuthorizedException:
        @raise BadRequestException:
        """
        body = '''{"name":"%s","id":"%s","description":"%s"}''' % (iteration.name, iteration.id, iteration.desc)
        res, content = self.restclient.process_request(
            'create_iteration', projectid, iteration.id, body=body, headers=self.http_headers
        )
        return self.messages(res, content, "The Version is already exist on server")

    def delete(self):
        pass

    def config(self, projectid, iterationid):
        """
        Retrieve project config from server
        @param projectid: Id of Project Resource
        @param iterationid: Id of Iteration Resource
        @return: Project Config
        @raise NoSuchProjectException
        """
        res, content = self.restclient.process_request('project_config', projectid, iterationid,
                                                       headers=self.http_headers)
        return self.messages(res, content)


class LocaleService(Service):
    """
    Provides services to interact with Project Locales.
    """
    _fields = ['base_url', 'http_headers']

    def __init__(self, *args, **kargs):
        super(LocaleService, self).__init__(*args, **kargs)

    def disable_ssl_cert_validation(self):
        self.restclient.disable_ssl_cert_validation()

    def get_locales(self, projectid, iterationid=None):
        """
        Retrieve a specified Project Locales on Zanata server
        @param projectid: Id of Project Resource
        @param iterationid: Id of Iteration Resource
        @return: service return content
        """
        service = 'iteration_locales' if iterationid else 'project_locales'
        res, content = self.restclient.process_request(
            service, projectid, iterationid, headers=self.http_headers
        )
        server_return = self.messages(res, content)
        return server_return
