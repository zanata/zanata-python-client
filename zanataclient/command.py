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

# Base on James Gardner's CommandTool v0.3.2, modified for python client requirement
# http://jimmyg.org/blog/2009/python-command-line-interface-%28cli%29-with-sub-commands.html
# Copyright (C) 2009 James Gardner - http://jimmyg.org/

import getopt
import sys
import os


class OptionConfigurationError(Exception):
    pass


def makeHandler(handler):
    def make(state=None):
        return handler
    return make


def option_names_from_option_list(option_list):
    names = []
    for option in option_list:
        for name in option['short']:
            names.append(name)
        for name in option['long']:
            names.append(name)
    return names


def strip_docstring(docstring, tabstop=4):
    docstring = docstring.replace('\r', '\n')
    minimum = len(docstring)
    lines = docstring.split('\n')
    for line in lines:
        if line:
            chars = 0
            i = 0
            while line[i:]:
                if line[i] == ' ':
                    i += 1
                    chars += 1
                elif line[i] == '\t':
                    i += 1
                    chars += tabstop
                else:
                    break
            if chars < minimum:
                minimum = chars
    # Now we know the amount of whitespace for the line with the least
    # we can regenerate the final docstring whitespace
    final = []
    for line in lines:
        if not line:
            final.append('')
        else:
            final.append(line[minimum:])
    return '\n'.join(final)


def extract_metavars(list_of_option_sets):
    metavars = {}
    for option_set in list_of_option_sets:
        for internal_name, option_list in option_set.items():
            for option in option_list:
                if 'metavar' in option:
                    metavar = option['metavar']
                    if metavar in metavars:
                        if metavars[metavar][1] != option['value']:
                            raise getopt.GetoptError(
                                'The options %r and %r must have the same '
                                'value if specified together' % (
                                    metavars[metavar][1],
                                    option['name'],
                                )
                            )
                        else:
                            metavars[metavar] = (option['name'], option['value'])
    return metavars


def parse_command_line(option_sets, subcmds=None, sys_args=None):
    program_opts, command_opts, command, args = _parse_command_line(
        option_sets,
        subcmds,
        sys_args,
    )
    # Now check that the results haven't ended up with conflicting metavars
    # but ignore the extracted value
    metavars = extract_metavars([program_opts, command_opts])
    return program_opts, command_opts, command, args


def _parse_command_line(option_sets, subcmds=None, sys_args=None):
    if sys_args is not None:
        sys_args = sys_args[1:]
    elif sys.argv and len(sys.argv) > 1:
        sys_args = sys.argv[1:]
    else:
        sys_args = []

    short_options = ''
    long_options = []
    by_option = {}
    used_internal = []
    # Check the options are valid and generate the get_opt options
    for internal_name, option_list in option_sets.items():
        if internal_name in used_internal:
            raise OptionConfigurationError(
                'The internal option %r has already been configured' % (
                    internal_name,
                )
            )
        else:
            used_internal.append(internal_name)

        for option in option_list:
            option['internal'] = internal_name
            if option['type'] not in ['shared', 'program', 'command']:
                raise OptionConfigurationError(
                    'Unknown type %r for option %r' % (
                        option['type'],
                        option['internal']
                    )
                )
            # Now set up the long and short options
            if 'short' in option:
                for short in option['short']:
                    if 'metavar' in option:
                        short_options += short.strip(':-') + ':'
                    else:
                        short_options += short.strip(':-')
                    if short.strip(':') in by_option:
                        raise OptionConfigurationError(
                            'The short option %r is already being used' % short
                        )
                    else:
                        new = option.copy()
                        new['name'] = short.strip(':')
                        by_option[short.strip(':')] = new
            for longopt in option['long']:
                if 'metavar' in option:
                    long_options.append(longopt.strip('-=') + '=')
                else:
                    long_options.append(longopt.strip('-='))
                if longopt.strip('=') in by_option:
                    raise OptionConfigurationError(
                        'The long option %r is already being used' % longopt
                    )
                else:
                    new = option.copy()
                    new['name'] = longopt.strip('=')
                    by_option[longopt.strip('=')] = new

    # Now we know the options are valid, parse them
    opts, args = getopt.gnu_getopt(sys_args, short_options, long_options)
    if not args:
        # If we have only use shared or program options then that's fine
        program_options = {}
        for opt in opts:
            if by_option[opt[0]]['type'] == 'command':
                raise getopt.GetoptError("No command specified.")
            else:
                internal = by_option[opt[0]]['internal']
                new = by_option[opt[0]].copy()
                new['value'] = opt[1]
                if internal in program_options:
                    program_options[internal].append(new)
                else:
                    program_options[internal] = [new]

        return (
            program_options,
            {},
            None,
            None,
        )
    else:
        orig_command = args[0]
        command = None
        sub = args[1:]
        for name, subcmd in subcmds.items():
            if orig_command == name and subcmd:
                if sub:
                    if sub[0] in subcmd:
                        command = orig_command + '_' + sub[0]
                        args = sub[1:]
                    else:
                        print("Unknown command!")
                        sys.exit(1)
                else:
                    print("Please complete the command!")
                    sys.exit(1)

            if orig_command == name and not subcmd:
                command = orig_command
                args = sub

        if not command:
            print("Unknown command!")
            sys.exit(1)

        # Get the extra data about the options used this time:
        option_types = {
            'program': {},
            'command': {},
            'shared': {},
        }

        for opt in opts:
            all_options = option_types[by_option[opt[0]]['type']]
            internal = by_option[opt[0]]['internal']
            new = by_option[opt[0]].copy()
            new['value'] = opt[1]
            if internal in all_options:
                all_options[internal].append(new)
            else:
                all_options[internal] = [new]

        if option_types['shared']:
            for k, vs in option_types['shared'].items():
                for v in vs:
                    if k in option_types['command']:
                        option_types['command'][k].append(v)
                    else:
                        option_types['command'][k] = [v]
                del option_types['shared']
                break

        result = (
            option_types['program'],
            option_types['command'],
            command,
            args,
        )
        return result


def handle_program(
    command_handler_factories,
    option_sets,
    program_options,
    command_options,
    command,
    args,
    program_name,
    help=None,
    existing=None,
):
    """
    usage: %(program)s [PROGRAM_OPTIONS] COMMAND [OPTIONS] ARGS

    Try %(program)s COMMAND --help' for help on a specific command.

    The following are valid zanata commands:
    push
    pull
    list
    project info
    project create
    version info
    version create
    glossary push
    publican push   (deprecated: use "push" with project type "podir")
    publican pull   (deprecated: use "pull" with project type "podir")
    po push         (deprecated: use "push" with project type "gettext")
    po pull         (deprecated: use "pull" with project type "gettext")
    """
    if existing is None:
        existing = {}
    # First, are they asking for program help?
    if 'help' in program_options:
        # if so provide it no matter what other options are given
        if help and hasattr(help, '__program__'):
            print(strip_docstring(
                help.__program__ % {
                    'program': program_name,
                }
            ))
        else:
            print(strip_docstring(
                handle_program.__doc__ % {
                    'program': program_name,
                }
            ))
        sys.exit(0)
    elif 'client_version' in program_options:
        # Retrieve the version of client
        version_number = ""
        path = os.path.dirname(os.path.realpath(__file__))
        version_file = os.path.join(path, 'VERSION-FILE')
        try:
            version = open(version_file, 'rb')
            client_version = version.read()
            version.close()
            version_number = client_version.rstrip().strip('version: ')
        except IOError:
            print("Please run VERSION-GEN or 'make install' to generate VERSION-FILE")
            version_number = "UNKNOWN"

        print("zanata python client version: %s" % version_number)
    else:
        if not command:
            raise getopt.GetoptError("No command specified.")
        # Are they asking for command help:
        if 'help' in command_options:
            # if so provide it no matter what other options are given
            if command not in command_handler_factories:
                raise getopt.GetoptError('No such command %r' % command)
            if hasattr(help, command):
                print(strip_docstring(
                    getattr(help, command) % {
                        'program': program_name,
                    }
                ))
            else:
                fn = command_handler_factories[command]()
                print(strip_docstring(
                    (fn.__doc__ or 'No help') % {
                        'program': program_name,
                    }
                ))
            sys.exit(0)

        # Now handle the command options and arguments
        command = command_handler_factories[command]()
        command(command_options, args)
