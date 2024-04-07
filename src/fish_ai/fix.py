# -*- coding: utf-8 -*-

from sys import argv
import subprocess
from fish_ai import engine


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

            fish: Unknown command. './foo.sh' exists but is not executable.
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
    return [engine.get_system_prompt()] + get_instructions(
        command, error_message)


def get_error_message(previous_command):
    """
    There is no way to get the output of the previous command in fish, so
    let's rerun the previous command and capture the output.
    """
    try:
        subprocess.check_output(previous_command,
                                stderr=subprocess.STDOUT,
                                shell=True)
    except subprocess.CalledProcessError as e:
        # Get the last 10 lines of the output and truncate lines exceeding
        # 200 characters
        return '\n'.join([line[:200] for line in e.output.decode('utf-8')
                          .split('\n')[-10:]])


def fix():
    previous_command = argv[1]
    error_message = get_error_message(previous_command)

    try:
        engine.get_logger().debug('Fixing command: ' + previous_command)
        engine.get_logger().debug('Command output: ' + error_message)
        response = engine.get_response(
            messages=get_messages(previous_command, error_message))
        print(response)
    except Exception as e:
        engine.get_logger().exception(e)
