#!/usr/bin/env python3

import _fish_ai_engine as engine
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

def get_instructions(commandline, cursor_position):
    if cursor_position < len(commandline):
        # Interpolate
        return [
            {
                'role': 'system',
                'content': '''
                Autocomplete a fish shell command given by the user.
                '''
            },
            {
                'role': 'user',
                'content': '''
                Autocomplete the fish shell command:

                openssl s_client

                Output at least one word. Output no more than three words. The command must end with:

                google.com:443
                '''
            },
            {
                'role': 'assistant',
                'content': 'openssl s_client -connect google.com:443'
            },
            {
                'role': 'user',
                'content': '''
                Autocomplete the fish shell command:

                {}

                Output at least one word. Output a maximum of three words. The command must end with:

                {}
                '''.format(commandline[:cursor_position], commandline[cursor_position:])
            },
        ]
    else:
        # Extrapolate
        return [
            {
                'role': 'user',
                'content': '''
                Autocomplete the fish shell command:

                {}

                Output a maximum of three words.
                '''.format(commandline)
            }
        ]

def get_messages(commandline, cursor_position):
    return [ engine.get_system_prompt() ] + get_instructions(commandline, cursor_position)

commandline = argv[1]
cursor_position = int(argv[2])

try:
    engine.get_logger().debug('Autocompleting commandline: {}'
        .format(commandline[:cursor_position] + '█' + commandline[cursor_position:]))
    response = engine.get_response(messages = get_messages(commandline, cursor_position))
    print(strip(output =
        response, prefix = commandline[:cursor_position],
        postfix = commandline[cursor_position:]))
except KeyboardInterrupt:
    pass
except Exception as e:
    engine.get_logger().exception(e)