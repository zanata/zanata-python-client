# vim: set et sts=4 sw=4:
#
#  Zanata Python Client
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
    "PublicanUtility",
)

import hashlib
import os
import re
import sys

import polib

from .zanatalib.logger import Logger

try:
    import json
except ImportError:
    import simplejson as json


class PublicanUtility:
    def __init__(self):
        self.log = Logger()

    def create_txtflow(self, pofile):
        """
        Convert the content of the pot file to a list of text flow.
        @return: the dictionary object of textflow
        """
        textflows = []
        for entry in pofile:
            context = None
            reflist = []
            content = ""

            if entry.msgctxt is not None:
                hashbase = entry.msgctxt + u"\u0000" + entry.msgid
                context = entry.msgctxt
            else:
                hashbase = entry.msgid
            # pylint: disable=E1101
            m = hashlib.md5()
            m.update(hashbase.encode('utf-8'))
            textflowId = m.hexdigest()
            """
            "extensions":[{"object-type":"pot-entry-header","context":"context",
            "references":["fff"],"extractedComment":"extractedComment",
            "flags":["java-format"]}]
            """
            extracted_comment = entry.comment
            references = entry.occurrences
            for ref in references:
                node = ref[0] + ":" + ref[1]
                reflist.append(node)
            flags = entry.flags

            if entry.msgid_plural:
                content = [entry.msgid, entry.msgid_plural]
            else:
                content = entry.msgid

            if context is not None:
                extensions = [{'object-type': 'comment', 'value': extracted_comment, 'space': 'preserve'},
                              {"object-type": "pot-entry-header", "context": context, "references": reflist,
                               "extractedComment": '', "flags": flags}]
            else:
                extensions = [{'object-type': 'comment', 'value': extracted_comment, 'space': 'preserve'},
                              {"object-type": "pot-entry-header", "references": reflist, "extractedComment": '',
                               "flags": flags}]

            if entry.msgid_plural:
                textflow = {'id': textflowId, 'lang': 'en-US', 'contents': content, 'plural': 'true', 'extensions': extensions}
            else:
                textflow = {'id': textflowId, 'lang': 'en-US', 'content': content, 'plural': 'false', 'extensions': extensions}

            textflows.append(textflow)
        return textflows

    def check_empty(self, contents):
        for string in contents:
            if string != u'':
                return False
        return True

    def check_nonempty(self, contents):
        for string in contents:
            if string == u'':
                return False
        return True

    def get_contentstate(self, entry):
        """
        Determine the ContentState for a PO entry, based on contents and fuzzy flag
        @return: the state
        """
        fuzzy = False
        contents = []

        if "fuzzy" in entry.flags:
            fuzzy = True

        if entry.msgid_plural:
            keys = entry.msgstr_plural.keys()
            keys.sort()
            for key in keys:
                contents.append(entry.msgstr_plural[key])
        else:
            contents.append(entry.msgstr)

        if self.check_empty(contents):
            fuzzy = False

        if fuzzy:
            return "NeedReview"

        if self.check_nonempty(contents):
            return "Approved"
        else:
            return "New"

    def create_txtflowtarget(self, pofile):
        """
        Convert the content of the po file to a list of textflowtarget.
        @return: the dictionary object of textflow
        """
        obs_list = pofile.obsolete_entries()
        textflowtargets = []
        content = ""

        for entry in pofile:
            if entry in obs_list:
                continue

            if entry.msgctxt is not None:
                hashbase = entry.msgctxt + u"\u0000" + entry.msgid
            else:
                hashbase = entry.msgid
            # pylint: disable=E1101
            m = hashlib.md5()
            m.update(hashbase.encode('utf-8'))
            textflowId = m.hexdigest()
            translator_comment = entry.tcomment

            state = self.get_contentstate(entry)

            # create extensions
            extensions = [{"object-type": "comment", "value": translator_comment, "space": "preserve"}]

            if entry.msgid_plural:
                content = []
                keys = entry.msgstr_plural.keys()
                keys.sort()
                for key in keys:
                    content.append(entry.msgstr_plural[key])
                textflowtarget = {'resId': textflowId, 'state': state, 'contents': content, 'extensions': extensions}
            else:
                content = entry.msgstr
                textflowtarget = {'resId': textflowId, 'state': state, 'content': content, 'extensions': extensions}

            textflowtargets.append(textflowtarget)

        return textflowtargets

    def validate_content_type(self, content_type, object_type):
        PATTERN = r'.+? charset=([\w_\-:\.]+)'
        rxt = re.compile(PATTERN)

        match = rxt.search(content_type)
        if match:
            enc = match.group(1).strip()
            if enc not in ["UTF-8", "utf-8", "utf8", "ascii", "UTF8", "ASCII"]:
                if enc == 'CHARSET':
                    if object_type == 'po-target-header':
                        self.log.error("Invalid encoding CHARSET; please correct the Content-Type charset (UTF-8 recommended)")
                        sys.exit(1)
                else:
                    self.log.error("Unsupported encoding; please change the Content-Type charset (UTF-8 recommended)")
                    sys.exit(1)

    def create_extensions(self, pofile, object_type):
        """
        "extensions":[{"object-type":"po-header","comment":"comment_value", "entries":[{"key":"h1","value":"v1"}]}]
        "extensions":[{"object-type":"po-target-header", "comment":"comment_value", "entries":[{"key":"ht","value":"vt1"}]}]
        """
        entries = []
        metadatas = pofile.ordered_metadata()
        for item in metadatas:
            entry = {"key": item[0], "value": item[1]}
            entries.append(entry)

        if 'Content-Type' in pofile.metadata:
            self.validate_content_type(pofile.metadata['Content-Type'], object_type)

        extensions = [{"object-type": object_type, "comment": pofile.header, "entries": entries}]
        return extensions

    def create_pofile(self, path):
        """
        Convert the po file to a pofile object in polib.
        @return: pofile object
        """
        try:
            po = polib.pofile(path)
        except Exception as e:
            self.log.error(str(e))
            sys.exit(1)

        return po

    def get_file_list(self, path, file_type):
        final_file_list = []
        root_list = os.listdir(path)
        for item in root_list:
            if item == '.svn':
                continue
            full_path = os.path.join(path, item)
            if full_path.endswith(file_type):
                final_file_list.append(full_path)
            if os.path.isdir(full_path):
                final_file_list += self.get_file_list(full_path, file_type)

        return final_file_list

    def get_pofile_path(self, folder, file_name):
        pofile_path = ""
        root_list = os.listdir(folder)
        for item in root_list:
            if item == '.svn':
                continue
            full_path = os.path.join(folder, item)
            if item == file_name:
                return full_path
            if os.path.isdir(full_path):
                pofile_path = self.get_pofile_path(full_path, file_name)
                if pofile_path:
                    return pofile_path

    def get_resId(self, message):
        """
        Calculate the hash of msgid and msgctxt
        @return: resId
        """
        if message.msgctxt:
            hashbase = message.msgctxt + u"\u0000" + message.msgid
        else:
            hashbase = message.msgid
        # pylint: disable=E1101
        m = hashlib.md5()
        m.update(hashbase.encode('utf-8'))

        return m.hexdigest()

    def strip_path(self, full_path, root_path, suffix):
        if root_path[-1] != "/":
            root_path += '/'

        # strip root path from the front of full_path
        filename = full_path[len(root_path):]

        if suffix in filename:
            # remove suffix from file name
            filename = filename[0:-len(suffix)]

        return filename

    def check_plural(self, filepath):
        pofile = self.create_pofile(filepath)
        for entry in pofile:
            if entry.msgid_plural:
                return True
        return False

    def potfile_to_json(self, filepath, root_path):
        """
        Parse the pot file, create the request body
        @param filepath: the path of the pot file
        """
        filename = self.strip_path(filepath, root_path, '.pot')
        pofile = self.create_pofile(filepath)
        textflows = self.create_txtflow(pofile)
        extensions = self.create_extensions(pofile, "po-header")
        items = {'name': filename, 'contentType': 'application/x-gettext', 'lang': 'en-US', 'extensions': extensions, 'textFlows': textflows}

        return json.dumps(items), filename

    def pofile_to_json(self, filepath):
        """
        Parse the po file, create the request body
        @param filepath: the path of the po file
        """
        pofile = self.create_pofile(filepath)
        textflowtargets = self.create_txtflowtarget(pofile)
        # the function for extensions have not implemented yet
        extensions = self.create_extensions(pofile, "po-target-header")
        items = {'links': [], 'extensions': extensions, 'textFlowTargets': textflowtargets}

        return json.dumps(items)

    def glossary_to_json(self, filepath, lang, sourcecomments):
        pofile = self.create_pofile(filepath)
        entries = []
        jsons = []
        targetlocales = []
        targetlocales.append(lang)
        srclocales = []
        srclocales.append('en-US')
        i = 0

        while i < len(pofile):
            entry = {'srcLang': 'en-US', 'glossaryTerms': '', 'sourcereference': ''}
            target_comments = []
            source_comments = []
            comments = ''
            reflist = []
            item = pofile[i]
            references = item.occurrences

            for ref in references:
                node = ref[0] + ":" + ref[1]
                reflist.append(node)

            if sourcecomments:
                target_comments = target_comments + reflist
                target_comments.append(item.comment)
            else:
                if entry['sourcereference']:
                    comments = comments + entry['sourcereference']
                if reflist:
                    ref = '\n'.join(str(n) for n in reflist)
                    comments = comments + ref
                entry['sourcereference'] = comments
                source_comments.append(item.comment)

            terms = [{'locale': lang, 'content': item.msgstr, 'comments': target_comments}, {'locale': 'en-US', 'content': item.msgid, 'comments': source_comments}]
            entry['glossaryTerms'] = terms
            entries.append(entry)

            if len(entries) == 300 or i == len(pofile) - 1:
                glossary = {'sourceLocales': srclocales, 'glossaryEntries': entries, 'targetLocales': targetlocales}
                jsons.append(json.dumps(glossary))
                entries = []

            i += 1

        return jsons

    def save_to_pofile(self, path, translations, potcontent, create_skeletons, locale, doc_name):
        """
        Save PO file to path, based on json objects of pot and translations
        @param translations: the json object of the content retrieved from server
        @param path: the po folder for output
        @param pot: the json object of the pot retrieved from server
        """
        po = polib.POFile(fpath=path)
        # potcontent = json.loads(pot)
        # pylint: disable=E1103
        textflows = potcontent.get('textFlows')

        if potcontent.get('extensions'):
            extensions = potcontent.get('extensions')[0]
            po.header = extensions.get('comment')
            for item in extensions.get('entries'):
                po.metadata[item['key']] = item['value']
            # specify Content-Type charset to UTF-8
            pattern = r'charset=[^;]*'
            if 'Content-Type' in po.metadata:
                re.sub(pattern, "charset=UTF-8", po.metadata['Content-Type'])
            else:
                po.metadata['Content-Type'] = "text/plain; charset=UTF-8"

        for textflow in textflows:
            poentry = polib.POEntry(occurrences=None)
            poentry.msgid = textflow.get('content')
            if textflow.get('extensions'):
                entry_list = textflow.get('extensions')
                for entry in entry_list:
                    if entry.get('object-type') == 'pot-entry-header':
                        # PotEntryHeader
                        # Check the references is not empty
                        if entry.get('references') != [u'']:
                            ref_list = []
                            for item in entry.get('references'):
                                # in some cases, entry contains more than one reference
                                if ' ' in item:
                                    reference = item.split(' ')
                                    for i in reference:
                                        ref_list.append(tuple(i.rsplit(':', 1)))
                                else:
                                    ref_list.append(tuple(item.rsplit(':', 1)))
                            poentry.occurrences = ref_list
                        else:
                            poentry.occurrences = None

                        if entry.get('flags'):
                            poentry.flags = [flag for flag in entry.get('flags')]

                        if entry.get('context') is not None:
                            poentry.msgctxt = entry.get('context')

                    if entry.get('object-type') == 'comment':
                        # SimpleComment
                        poentry.comment = entry.get('value')

            if textflow.get('contents'):
                poentry.msgid = textflow.get('contents')[0]
                poentry.msgid_plural = textflow.get('contents')[1]
                poentry.msgstr_plural[0] = ''
            else:
                poentry.msgstr = ''
            po.append(poentry)

        # If the translation is exist, read the content of the po file
        if translations:
            content = translations
            # "extensions":[{"object-type":"po-target-header", "comment":"comment_value", "entries":
            # [{"key":"ht","value":"vt1"}]}]

            if content.get('extensions'):
                ext = content.get('extensions')[0]
                header_comment = ext.get('comment')
                if header_comment:
                    po.header = header_comment
                for item in ext.get('entries'):
                    po.metadata[item['key']] = item['value']

            targets = content.get('textFlowTargets')

            if not create_skeletons:
                if not targets:
                    self.log.warn("No translations found in %s for document %s" % (locale, doc_name))
                    return

            translationsByResId = {}
            for translation in targets:
                resId = translation.get('resId')
                translationsByResId[resId] = translation

            # "extensions":[{"object-type":"comment","value":"testcomment","space":"preserve"}]
            # copy any other stuff you need to transfer
            for poentry in po:
                resId = self.get_resId(poentry)
                translation = translationsByResId.get(resId)
                if translation:
                    if translation.get('extensions'):
                        extensions = translation.get('extensions')
                        for entry in extensions:
                            if entry.get('object-type') == 'comment':
                                if entry.get('value'):
                                    poentry.tcomment = entry.get('value')

                    content = translation.get('content')
                    if poentry.msgid_plural:
                        contents = translation.get('contents')
                        if contents:
                            i = 0
                            for msg in contents:
                                poentry.msgstr_plural[i] = msg
                                i = i + 1
                        elif content:
                            poentry.msgstr_plural[0] = content
                    else:
                        if content:
                            poentry.msgstr = content

                    if translation.get('state') == 'NeedReview':
                        if poentry.flags == [u'']:
                            poentry.flags = ['fuzzy']
                        else:
                            poentry.flags.insert(0, 'fuzzy')
                    else:
                        if poentry.flags == [u'']:
                            poentry.flags = None

            # finally save resulting po to outpath
            subdirectory = path[:path.rfind('/')]
            if subdirectory and not os.path.isdir(subdirectory):
                os.makedirs(subdirectory)
            po.save()
            # pylint: disable=E1103
            self.log.success("Writing po file to %s" % (path))

        else:
            self.log.warn("No translations found in %s for document %s" % (locale, doc_name))
