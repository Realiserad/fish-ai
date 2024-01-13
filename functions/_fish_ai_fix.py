#!/usr/bin/env python3

from sys import argv
import _fish_ai_engine as engine

def get_instructions(command, error_message):
    return [
        {
            'role': 'system',
            'content': '''
            Provide a fix for the user's error message.

            Output only the fish shell command that fixes the problem.
            '''
        },
        {
            'role': 'user',
            'content': '''
            Command:

            ./foo.sh

            Error message:

            fish: Unknown command. './foo.sh' exists but is not an executable file.
            '''
        },
        {
            'role': 'assistant',
            'content': 'sh ./foo.sh'
        },
        {
            'role': 'user',
            'content': '''
            Command:

            tree -d 1 .

            Error message:

            Command 'tree' not found, but can be installed with:
            sudo apt install tree
            '''
        },
        {
            'role': 'assistant',
            'content': 'sudo apt install tree'
        },
        {
            'role': 'user',
            'content': '''
            Command:

            {}

            Error message:

            {}
            '''.format(command, error_message)
        }
    ]

def get_messages(command, error_message):
    return [ engine.get_system_prompt() ] + get_instructions(command, error_message)

command = argv[1]
# Cut lines in the error output exceeding 200 characters
error_message = '\n'.join([line[:200] for line in argv[2].split('\n')])

try:
    engine.get_logger().debug('Fixing command: ' + command)
    engine.get_logger().debug('Command output: ' + error_message)
    response = engine.get_response(messages = get_messages(command, error_message))
    print(response)
except Exception as e:
    engine.get_logger().exception(e)