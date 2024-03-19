#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv
import _fish_ai_engine as engine


def get_instructions(commandline):
    return [
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
        }

    ]


def get_messages():
    return [engine.get_system_prompt()] + get_instructions(commandline)


commandline = argv[1]
if commandline.startswith('# '):
    commandline = commandline[2:]

try:
    engine.get_logger().debug('Codifying commandline: ' + commandline)
    response = engine.get_response(messages=get_messages())
    print(response)
except KeyboardInterrupt:
    pass
except Exception as e:
    engine.get_logger().exception(e)
    # Leave the commandline untouched
    print('# ' + commandline)
