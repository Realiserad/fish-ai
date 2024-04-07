# -*- coding: utf-8 -*-

from sys import argv
from os.path import isfile
from os import access, R_OK
from re import match
from fish_ai import engine


def get_instructions(commandline):
    instructions = [
        {
            'role': 'system',
            'content': '''
            Respond with a fish shell command which carries out the user's
            task. Do not explain. Only respond with a single line.
            '''
        },
        {
            'role': 'user',
            'content': 'List all disks on the system'
        },
        {
            'role': 'assistant',
            'content': 'df -h'
        },
        {
            'role': 'user',
            'content': 'Pull the Alpine 3 container from DockerHub'
        },
        {
            'role': 'assistant',
            'content': 'docker pull alpine:3'
        },
        {
            'role': 'user',
            'content': 'Substitute all occurrences of the string "foo" with ' +
            'the string "bar" in the file "docker-compose.yml"'
        },
        {
            'role': 'assistant',
            'content': 'sed -i "s/foo/bar/g" docker-compose.yml'
        },
        {
            'role': 'user',
            'content': commandline
        },
    ]
    (filename, file_contents) = get_file_info(commandline)
    if filename:
        instructions.append({
            'role': 'user',
            'content': '''
            The content of the file {} is'

            {}
            '''.format(filename, '\n'.join(file_contents))
        })
    return instructions


def get_file_info(commandline):
    """
    If the user is mentioning a file in the instructions, return the
    filename and its file contents.
    """
    for word in commandline.split():
        filename = word.rstrip(',.!').strip('"\'')
        if not match(r'[A-Za-z0-9_\-]+\.[a-z]+', filename.split('/')[-1]):
            continue
        if not isfile(filename):
            continue
        if not access(filename, R_OK):
            continue
        with open(filename, 'r') as file:
            engine.get_logger().debug('Loading file: ' + filename)
            return filename, file.readlines(3072)
    return None, None


def get_messages(commandline):
    return [engine.get_system_prompt()] + get_instructions(commandline)


def codify():
    commandline = argv[1]
    if commandline.startswith('# '):
        commandline = commandline[2:]

    try:
        engine.get_logger().debug('Codifying commandline: ' + commandline)
        response = engine.get_response(messages=get_messages(commandline))
        print(response)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        engine.get_logger().exception(e)
        # Leave the commandline untouched
        print('# ' + commandline)
