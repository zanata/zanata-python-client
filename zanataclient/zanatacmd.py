# vim: set et sts=4 sw=4:
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

import os
import sys

from .csvconverter import CSVConverter
from .publicanutil import PublicanUtility
from .zanatalib.error import (
    BadRequestBodyException,
    InternalServerError,
    InvalidOptionException,
    NoSuchProjectException,
    SameNameDocumentException,
    UnAuthorizedException,
    UnAvaliableResourceException,
    UnavailableServiceError,
    UnexpectedStatusException,
    ZanataException,
)
from .zanatalib.logger import Logger
from .zanatalib.projectutils import FileMappingRule, Iteration, Project, Stats
from .zanatalib.resource import ZanataResource


try:
    input = raw_input
except NameError:
    pass


class ZanataCommand:
    def __init__(self, url, http_headers):
        self.log = Logger()
        self.zanata_resource = ZanataResource(url, http_headers)

    def disable_ssl_cert_validation(self):
        self.zanata_resource.disable_ssl_cert_validation()

    ##############################################
    #
    # Commands for interaction with zanata server
    #
    ##############################################
    def get_file_list(self, projectid, iterationid):
        return self.zanata_resource.documents.get_file_list(projectid, iterationid)

    def get_server_version(self, url):
        try:
            content = self.zanata_resource.version.get_server_version()
            if content:
                server_version = content['versionNo']
                return server_version
        except UnAvaliableResourceException:
            self.log.error("Can not retrieve the server version, server may not support the version service")
        except UnavailableServiceError:
            self.log.error("Service Temporarily Unavailable, stop processing!")
            sys.exit(1)

    """
    def check_project(self, command_options, project_config):
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
        self.verify_project(project_id, iteration_id)
    """

    def verify_project(self, project_id, version_id):
        try:
            self.zanata_resource.projects.get(project_id)
        except NoSuchProjectException as e:
            self.log.error(str(e))
            sys.exit(1)

        try:
            self.zanata_resource.projects.iterations.get(project_id, version_id)
        except NoSuchProjectException as e:
            self.log.error(str(e))
            sys.exit(1)
        except ZanataException as e:
            self.log.error(str(e))

    def update_template(self, project_id, iteration_id, filename, body, copytrans):
        if '/' in filename:
            request_name = filename.replace('/', ',')
        else:
            request_name = filename

        try:
            result = self.zanata_resource.documents.update_template(project_id, iteration_id, request_name, body, copytrans)
            if result:
                self.log.success("Successfully updated template %s on the server" % filename)
        except ZanataException as e:
            self.log.error(str(e))

    def commit_translation(self, project_id, iteration_id, request_name, pofile, lang, body, merge):
        try:
            result = self.zanata_resource.documents.commit_translation(project_id, iteration_id, request_name, lang, body, merge)
            if result:
                self.log.warn(result)
            self.log.success("Successfully pushed translation %s to the Zanata server" % pofile)
        except ZanataException as e:
            self.log.error(str(e))

    def del_server_content(self, tmlfolder, project_id, iteration_id, push_files, force, project_type):
        # Get the file list of this version of project
        try:
            filelist = self.zanata_resource.documents.get_file_list(project_id, iteration_id)
        except Exception as e:
            self.log.error(str(e))
            sys.exit(1)

        if filelist:
            self.log.warn("This will overwrite/delete any existing documents on the server.")
            if not force:
                while True:
                    option = input("Are you sure (y/n)?")
                    if option.lower() == "yes" or option.lower() == "y":
                        break
                    elif option.lower() == "no" or option.lower() == "n":
                        self.log.info("Processing stopped, keeping existing content on the server")
                        sys.exit(1)
                    else:
                        self.log.error("Please enter yes(y) or no(n)")

            for name in filelist:
                delete = False
                request = name.replace(',', '\,').replace('/', ',')

                if ".pot" in name:
                    path = os.path.join(tmlfolder, name)
                else:
                    path = os.path.join(tmlfolder, name + ".pot")

                if project_type == "gettext":
                    if push_files:
                        if path not in push_files:
                            delete = True
                elif project_type == "podir":
                    if not os.path.exists(path):
                        delete = True

                if delete:
                    self.log.info("Deleting the %s" % name)

                    try:
                        self.zanata_resource.documents.delete_template(project_id, iteration_id, request)
                    except ZanataException as e:
                        self.log.error(str(e))
                        sys.exit(1)

    def get_projects(self):
        return self.zanata_resource.projects.list()

    def list_projects(self):
        """
        List the information of all the project on the zanata server
        """
        projects = self.get_projects()

        if not projects:
            # As we are catching exceptions related to reaching server,
            # we may be certain that there is NO project created.
            self.log.info("There are no projects on this server.")
            sys.exit(1)

        for project in projects:
            print("\nProject ID:          {0}".format(project.id))
            print("Project Name:        {0}".format(project.name))
            if hasattr(project, 'defaultType') and project.defaultType.strip():
                print("Project Type:        {0}".format(project.defaultType))
            print("Project Links:       {0}".format([{'href': link.href, 'type': link.type, 'rel': link.rel} for link in project.links]))
            if hasattr(project, 'status'):
                print("Project Status:      {0}".format(project.status))

    def project_info(self, project_id):
        """
        Retrieve the information of a project
        """
        try:
            p = self.zanata_resource.projects.get(project_id)
            print("\nProject ID:        {0}".format(p.id))
            print("Project Name:      {0}".format(p.name))
            if hasattr(p, 'defaultType') and p.defaultType.strip():
                print("Project Type:      {0}".format(p.defaultType))
            if hasattr(p, 'description') and p.description.strip():
                print("Project Desc:      {0}".format(p.description))
            if hasattr(p, 'status'):
                print("Project Status:    {0}".format(p.status))
            versions = self.get_project_versions(project_id)
            if versions:
                print("{0} Version(s):     [ {1} ]".format(len(versions), ", ".join(versions)))
            print("\n")
        except NoSuchProjectException as e:
            self.log.error(str(e))
        except InvalidOptionException:
            self.log.error("Options are not valid")

    def get_project_versions(self, project_id):
        try:
            p = self.zanata_resource.projects.get(project_id)
            project_versions = []
            if hasattr(p, 'iterations'):
                for iteration in p.iterations:
                    project_versions.append(iteration.get('id'))
            return project_versions
        except NoSuchProjectException as e:
            self.log.error(str(e))
        except InvalidOptionException:
            self.log.error("Options are not valid")

    def version_info(self, project_id, iteration_id):
        """
        Retrieve the information of a project iteration.
        """
        try:
            project = self.zanata_resource.projects.get(project_id)
            iteration = project.get_iteration(iteration_id)
            print("\nVersion ID:          {0}".format(iteration.id))
            if hasattr(iteration, 'name'):
                print("Version Name:        {0}".format(iteration.name))
            if hasattr(iteration, 'description'):
                print("Version Description:  {0}".format(iteration.description))
            if hasattr(iteration, 'projectType') and iteration.projectType.strip():
                print("Version Type:        {0}".format(iteration.projectType))
            if hasattr(iteration, 'status'):
                print("Version Status:      {0}".format(iteration.status))
            # This can be implemented with some flag etc.
            # filelist = self.zanata_resource.documents.get_file_list(project_id, iteration_id)
            # if filelist:
            #     print(" %s Document(s): [%s]") % (len(filelist), ", ".join(filelist))
            print("\n")
        except NoSuchProjectException as e:
            self.log.error(str(e))

    def create_project(self, project_id, project_name, project_desc, project_type):
        """
        Create project with the project id, project name and project description
        @param args: project id
        """
        try:
            item = {'id': project_id, 'name': project_name,
                    'desc': project_desc, 'type': project_type}
            p = Project(item)
            result = self.zanata_resource.projects.create(p)
            if result:
                self.log.success("Successfully created project: %s" % project_id)
                return True
        except ZanataException as e:
            self.log.error(str(e))

    def create_version(self, project_id, version_id, version_name=None, version_desc=None):
        """
        Create version with the version id, version name and version description
        @param args: version id
        """
        try:
            item = {'id': version_id, 'name': version_name, 'desc': version_desc}
            iteration = Iteration(item)
            result = self.zanata_resource.projects.iterations.create(project_id, iteration)
            if result:
                self.log.success("Successfully created version: %s" % version_id)
                return True
        except ZanataException as e:
            self.log.error(str(e))

    def import_po(self, potfile, trans_folder, project_id, iteration_id, lang_list, locale_map,
                  merge, project_type, file_mapping_rules):
        sub_dir = ""
        publicanutil = PublicanUtility()

        for local_lang in lang_list:
            if not locale_map:
                remote_lang = local_lang
            else:
                if local_lang in locale_map:
                    remote_lang = locale_map[local_lang]
                else:
                    remote_lang = local_lang

            if '/' in potfile:
                name = potfile.split('/')[-1]
                request_name = potfile.replace('/', ',')
                sub_dir = potfile[0:potfile.rfind('/')]
            else:
                name = request_name = potfile

            self.log.info("Pushing %s translation for %s to server:" % (local_lang, potfile))

            pofile = FileMappingRule(
                project_type, local_lang, 'po', file_mapping_rules, **{
                    'trans_folder': trans_folder, 'path': sub_dir, 'filename': name, 'remote_filepath': potfile,
                }
            ).translation_path

            if not os.path.isfile(pofile):
                self.log.error("Can not find the %s translation for %s" % (local_lang, potfile))
                continue

            body = publicanutil.pofile_to_json(pofile)

            if not body:
                self.log.error("No content or all entries are obsolete in %s" % pofile)
                sys.exit(1)

            self.commit_translation(project_id, iteration_id, request_name, pofile, remote_lang, body, merge)

    def push_trans_command(self, transfolder, project_id, iteration_id, lang_list, locale_map,
                           project_type, merge, file_mapping_rules):
        filelist = ""
        publicanutil = PublicanUtility()

        try:
            filelist = self.zanata_resource.documents.get_file_list(project_id, iteration_id)
        except ZanataException as e:
            self.log.error(str(e))

        if not filelist:
            self.log.error("There is no source files on the server, please push source files first")
            sys.exit(1)

        for local_lang in lang_list:
            if not locale_map:
                remote_lang = local_lang
            else:
                if local_lang in locale_map:
                    remote_lang = locale_map[local_lang]
                else:
                    remote_lang = local_lang

            self.log.info("Pushing %s translation for %s to server:" % (local_lang, project_id))

            for filename in filelist:
                sub_dir = ''
                if '/' in filename:
                    name = filename.split('/')[-1]
                    sub_dir = filename[0:filename.rfind('/')]
                else:
                    name = filename

                pofile = FileMappingRule(
                    project_type, local_lang, 'po', file_mapping_rules, **{
                        'trans_folder': transfolder, 'path': sub_dir, 'filename': name, 'remote_filepath': filename,
                    }
                ).translation_path

                if not pofile or not os.path.isfile(pofile):
                    self.log.error("Can not find the %s translation for %s" % (local_lang, filename))
                    continue
                else:
                    self.log.info("Pushing the %s translation of %s to server:" % (local_lang, filename))

                request_name = filename.replace('/', ',')

                body = publicanutil.pofile_to_json(pofile)

                if not body:
                    self.log.error("No content or all entries are obsolete in %s" % sub_dir)
                    sys.exit(1)

                self.commit_translation(project_id, iteration_id, request_name, pofile, remote_lang, body, merge)

    def push_command(self, file_list, srcfolder, project_id, iteration_id, copytrans, plural_support=False,
                     import_param=None, file_mapping_rules=None):
        """
        Push the content of publican files to a Project version on Zanata server
        @param args: name of the publican file
        """
        publicanutil = PublicanUtility()

        for filepath in file_list:
            self.log.info("Pushing the content of %s to server:" % filepath)
            plural_exist = publicanutil.check_plural(filepath)
            if plural_exist and not plural_support:
                self.log.error("The plural is only supported in zanata server >= 1.6, this file will be ignored")
                break
            body, filename = publicanutil.potfile_to_json(filepath, srcfolder)
            try:
                result = self.update_template(project_id, iteration_id, filename, body, copytrans)
                if result:
                    self.log.success("Successfully pushed %s to the server" % filepath)
            except UnAuthorizedException as e:
                self.log.error(str(e))
                break
            except BadRequestBodyException as e:
                self.log.error(str(e))
                continue
            except UnexpectedStatusException as e:
                self.log.error(str(e))
                continue
            except InternalServerError as e:
                self.log.error(str(e))
                sys.exit(1)

            if import_param:
                merge = import_param['merge']
                lang_list = import_param['lang_list']
                project_type = import_param['project_type']
                transdir = import_param['transdir']
                locale_map = import_param['locale_map']

                self.import_po(filename, transdir, project_id, iteration_id, lang_list, locale_map,
                               merge, project_type, file_mapping_rules)

    def pull_command(self, locale_map, project_id, iteration_id, filedict, output, project_type, skeletons, mapping_rules):
        """
        Retrieve the content of documents in a Project version from Zanata server. If the name of publican
        file is specified, the content of that file will be pulled from server. Otherwise, all the document of that
        Project iteration will be pulled from server.
        @param args: the name of publican file
        """
        publicanutil = PublicanUtility()
        # if file no specified, retrieve all the files of project
        for file_item, lang_list in filedict.items():
            pot = ""
            result = ""
            folder = ""

            if '/' in file_item:
                name = file_item.split('/')[-1]
                folder = file_item[0:file_item.rfind('/')]
                request_name = file_item.replace('/', ',')
            else:
                name = request_name = file_item

            self.log.info("Fetching the content of %s from Zanata server" % name)

            try:
                pot = self.zanata_resource.documents.retrieve_template(project_id, iteration_id, request_name)
            except UnAuthorizedException as e:
                self.log.error(str(e))
                break
            except UnAvaliableResourceException as e:
                self.log.error("Can't find pot file for %s on server" % name)
                break
            except UnexpectedStatusException as e:
                self.log.error(str(e))
                break
            except InternalServerError as e:
                self.log.error(str(e))
                sys.exit(1)

            for local_lang in lang_list:
                if not locale_map:
                    remote_lang = local_lang
                else:
                    if local_lang in locale_map:
                        remote_lang = locale_map[local_lang]
                    else:
                        remote_lang = local_lang

                file_mapped_path = FileMappingRule(
                    project_type, local_lang, 'po', mapping_rules, **{
                        'trans_folder': output, 'path': folder, 'filename': name, 'remote_filepath': file_item,
                    }
                ).translation_path

                self.log.info("Retrieving %s translation from server: " % local_lang)

                try:
                    result = self.zanata_resource.documents.retrieve_translation(
                        remote_lang, project_id, iteration_id, request_name, skeletons
                    )
                    publicanutil.save_to_pofile(file_mapped_path, result, pot, skeletons, local_lang, name)
                except UnAuthorizedException as e:
                    self.log.error(str(e))
                    break
                except UnAvaliableResourceException as e:
                    self.log.warn("There is no %s translation for %s" % (local_lang, name))
                except BadRequestBodyException as e:
                    self.log.error(str(e))
                    continue
                except UnexpectedStatusException as e:
                    self.log.error(str(e))
                except InternalServerError as e:
                    self.log.error(str(e))
                    sys.exit(1)

    def poglossary_push(self, path, lang, sourcecomments):
        i = 0
        jsons = []
        publicanutil = PublicanUtility()
        jsons = publicanutil.glossary_to_json(path, lang, sourcecomments)
        size = len(jsons)
        if size > 1:
            self.log.warn("The file is big, try to divide it to small parts. It may take a long time to push!")

        while i < size:
            if size > 1:
                self.log.info("Push part %s of glossary file" % i)
            try:
                self.zanata_resource.glossary.commit_glossary(jsons[i])
            except ZanataException as e:
                self.log.error(str(e))
                sys.exit(1)
            i += 1
        self.log.info("Successfully pushed glossary to the server")

    def csvglossary_push(self, path, locale_map, comments_header):
        csvconverter = CSVConverter()
        json = csvconverter.convert_to_json(path, locale_map, comments_header)

        try:
            content = self.zanata_resource.glossary.commit_glossary(json)
            if content:
                self.log.info("Successfully pushed glossary to the server")
        except ZanataException as e:
            self.log.error(str(e))

    def delete_glossary(self, lang=None):
        try:
            self.zanata_resource.glossary.delete(lang)
        except ZanataException as e:
            self.log.error(str(e))
        else:
            self.log.info("Successfully delete the glossary terms on the server")

    def get_project_translation_stats(self, project_id, project_version, min_doc_percent, lang_list, locale_map):
        doc_locales_dict = {}
        try:
            server_return = self.zanata_resource.stats.get_project_stats(project_id, project_version)
        except ZanataException as e:
            self.log.error(str(e))
        else:
            percent_dict = Stats(server_return).trans_percent_dict
            for doc, stat in percent_dict.items():
                disqualify_locales = []
                for locale, trans_percent in stat.items():
                    if trans_percent < int(min_doc_percent):
                        disqualify_locales.append(locale)
                disqualify_locales = [alias for alias, locale in locale_map.items()
                                      for lang in disqualify_locales if lang == locale]
                if disqualify_locales:
                    self.log.info('Translation file for document %s for locales [%s] are skipped '
                                  'because they are less than %s%% translated (--min-doc-percent setting)' %
                                  (doc, ', '.join(map(str, disqualify_locales)), min_doc_percent))
                qualify_lang_set = set(lang_list) - set(disqualify_locales)
                doc_locales_dict.update({doc: list(qualify_lang_set)})
        finally:
            return doc_locales_dict

    def _print_double_line(self, length):
        print('=' * length)

    def _print_new_line_row(self, sequence, header=None):
        pattern = (
            " %-10s %-8s %-4s %5s %10s %14s %25s"
            if header else
            " %-10s %-8s %-4s %5s %10s %14s %32s"
        )
        print(pattern % sequence)

    def _display_stats(self, collection, locale_map):
        self._print_double_line(90)
        headers = ('Locale', 'Unit', 'Total', 'Translated', 'Need Review',
                   'Untranslated', 'Last Translated')
        self._print_new_line_row(headers, True)
        self._print_double_line(90)
        for stat in collection:
            values = (
                [alias if lang == stat.get('locale') else stat.get('locale')
                 for alias, lang in locale_map.items()][0],
                stat.get('unit', 'MESSAGE'), stat.get('total', '0'),
                stat.get('translated', '0'), stat.get('needReview', '0'),
                stat.get('untranslated', '0'), stat.get('lastTranslated', '')
            )
            self._print_new_line_row(values)
        self._print_double_line(90)
        print('\n')

    def _display_doc_stats(self, doc_name, stats_dict, locale_map):
        print('Document: %s' % doc_name)
        self._display_stats(stats_dict, locale_map)

    def display_translation_stats(self, *args, **kwargs):
        try:
            project_id, project_version = args
            server_return = self.zanata_resource.stats.get_project_stats(
                project_id, project_version, 'wordstats' in kwargs, kwargs.get('lang')
            ) if not kwargs.get('docid') else \
                self.zanata_resource.stats.get_doc_stats(
                    project_id, project_version, kwargs['docid'],
                    'wordstats' in kwargs, kwargs.get('lang')
            )
        except ZanataException as e:
            self.log.error(str(e))
        else:
            trans_stats = Stats(server_return)
            locale_map = kwargs.get('locale_map')
            if kwargs.get('docid'):
                self.log.info('Document: %s' % trans_stats.stats_id)
            if 'detailstats' in kwargs:
                self._display_stats(trans_stats.trans_stats_dict, locale_map)
                for doc, stats in trans_stats.trans_stats_detail_dict.items():
                    self._display_doc_stats(doc, stats, locale_map)
            else:
                self._display_stats(trans_stats.trans_stats_dict, locale_map)
