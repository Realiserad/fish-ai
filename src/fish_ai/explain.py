# -*- coding: utf-8 -*-

from sys import argv
from fish_ai import engine
import subprocess


def get_instructions(commandline):
    return [
        {
            'role': 'system',
            'content': '''
            Respond with a maximum of three sentences which explain the fish
            shell command given by the user.

            The response must begin with a verb. The sentences should be
            written in {language}.

            You may use the following manpage to help explain the command:

            {manpage}
            '''.format(language=engine.get_config('language') or 'English',
                       manpage=get_manpage(commandline.split()[0]))
        },
        {
            'role': 'user',
            'content': 'df -h'
        },
        {
            'role': 'assistant',
            'content': 'List all disks on the system'
        },
        {
            'role': 'user',
            'content': 'docker pull alpine:3'
        },
        {
            'role': 'assistant',
            'content': 'Pull the Alpine 3 container from DockerHub'
        },
        {
            'role': 'user',
            'content': 'sed -i "s/foo/bar/g" docker-compose.yml'
        },
        {
            'role': 'assistant',
            'content': 'Substitute all occurrences of the string "foo" with ' +
                    'the string "bar" in the file "docker-compose.yml"'
        },
        {
            'role': 'user',
            'content': commandline
        }
    ]


def get_manpage(command):
    manpage = subprocess.run(['man', command], stdout=subprocess.PIPE)
    if manpage.returncode == 0:
        return manpage.stdout.decode('utf-8')
    helppage = subprocess.run([command, '--help'], stdout=subprocess.PIPE)
    if helppage.returncode == 0:
        return helppage.stdout.decode('utf-8')
    return 'No manpage available.'


def get_messages(commandline):
    return [engine.get_system_prompt()] + get_instructions(commandline)


def explain():
    commandline = argv[1]

    try:
        engine.get_logger().debug('Explaining commandline: ' + commandline)
        response = engine.get_response(messages=get_messages(commandline))
        print('# ' + response.replace('\n', ' '))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        engine.get_logger().exception(e)
        # Leave the commandline untouched
        print(commandline)
