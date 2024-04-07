# -*- coding: utf-8 -*-

from fish_ai import engine
from sys import argv


def get_instructions(commandline, cursor_position):
    return [
        {
            'role': 'system',
            'content': '''
            Autocomplete a fish shell command given by the user.
            The █ character in the command marks the position of the cursor
            where the user is typing. The completion must contain at least one
            word. The completion must not contain more than three words.
            '''
        },
        {
            'role': 'user',
            'content': '''
            Autocomplete the fish shell command:

            openssl s_client█google.com:443
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

            {}█{}
            '''.format(commandline[:cursor_position],
                       commandline[cursor_position:])
        },
    ]


def get_messages(commandline, cursor_position):
    return [engine.get_system_prompt()] + get_instructions(commandline,
                                                           cursor_position)


def autocomplete():
    commandline = argv[1]
    cursor_position = int(argv[2])

    try:
        engine.get_logger().debug('Autocompleting commandline: {}'.format(
            commandline[:cursor_position] + '█' +
            commandline[cursor_position:]))
        response = engine.get_response(messages=get_messages(commandline,
                                                             cursor_position))
        print(response)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        engine.get_logger().exception(e)
