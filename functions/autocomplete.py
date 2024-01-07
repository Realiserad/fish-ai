#!/usr/bin/env python3

from sys import stdin
import engine as ai
from sys import argv

def strip(output, prefix, postfix):
    """
    If the LLM is instructed to interpolate a command, it returns the whole
    command instead of the interpolated value. For example, if instructed
    to autocomplete "docker run --interactive █--rm purefish/docker-fish"
    (where █ denotes the cursor position) it may return something like
    "docker run --interactive --tty --rm purefish/docker-fish" instead of
    just "--tty".

    We could instruct the model not to do that, but it's probably more reliable
    to just fix it here.
    """
    if len(postfix) == 0:
        return output
    else:
        return output[len(prefix):len(output) - len(postfix)]

def get_user_prompt(commandline, cursor_position):
    if cursor_position < len(commandline):
        return {
            'role': 'user',
            'content': '''
            Autocomplete a shell command. It must begin with:

            [INST] {} [/INST]

            and end with:

            [INST] {} [/INST]

            Only output the command.
            '''.format(commandline[:cursor_position], commandline[cursor_position:])
        }
    else:
        return {
            'role': 'user',
            'content': '''
            Autocomplete the shell command:

            [INST] {} [/INST]

            Only output one word.
            '''.format(commandline)
        }

commandline = stdin.read()
cursor_position = int(argv[1])

try:
    ai.get_logger().debug('Autocompleting commandline: {}'
        .format(commandline[:cursor_position] + '█' + commandline[cursor_position:]))
    response = ai.get_response(messages = [ai.get_system_prompt(), get_user_prompt(commandline, cursor_position)])
    print(strip(output =
        response, prefix = commandline[:cursor_position],
        postfix = commandline[cursor_position:]))
except Exception as e:
    ai.get_logger().exception(e)