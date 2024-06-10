# -*- coding: utf-8 -*-

from fish_ai import engine
from sys import argv
from iterfzf import iterfzf
import textwrap


def get_instructions(commandline, cursor_position):
    return [
        {
            'role': 'system',
            'content': textwrap.dedent('''\
            Autocomplete a fish shell command given by the user.
            The █ character in the command marks the position of the cursor
            where the user is typing. Respond with only the autocompleted
            command.

            You may use the following manpage to assist with autocompletion:

            {manpage}

            You may use the following commandline history to personalise
            the output:

            {commandline_history}''').format(
                manpage=engine.get_manpage(commandline.split()[0]),
                commandline_history=engine.get_commandline_history(
                    commandline))
        },
        {
            'role': 'user',
            'content': textwrap.dedent('''\
            Autocomplete the fish shell command:

            openssl s_client█google.com:443
            ''')
        },
        {
            'role': 'assistant',
            'content': 'openssl s_client -connect google.com:443'
        },
        {
            'role': 'user',
            'content': textwrap.dedent('''\
            Autocomplete the fish shell command:

            {}█{}''').format(commandline[:cursor_position],
                             commandline[cursor_position:])
        },
    ]


def get_another_completion_message(commandline, cursor_position):
    return {
        'role': 'user',
        'content': 'Provide a different completion of the command: {}█{}'
        .format(commandline[:cursor_position],
                commandline[cursor_position:])
    }


def get_messages(commandline, cursor_position):
    return [engine.get_system_prompt()] + get_instructions(commandline,
                                                           cursor_position)


def yield_completions(commandline, cursor_position, completions_count):
    yield commandline
    messages = get_messages(commandline, cursor_position)
    for _ in range(completions_count):
        response = engine.get_response(
            messages=messages)
        engine.get_logger().debug('Created completion: ' + response)
        yield response
        messages.append({
            'role': 'assistant',
            'content': response
        })
        messages.append(get_another_completion_message(
            commandline, cursor_position))


def autocomplete():
    commandline = argv[1]
    cursor_position = int(argv[2])

    try:
        engine.get_logger().debug('Autocompleting commandline: {}'.format(
            commandline[:cursor_position] + '█' +
            commandline[cursor_position:]))
        completions_count = int(engine.get_config('completions') or '5')
        engine.get_logger().debug('Creating {} completions'
                                  .format(completions_count))

        completions_generator = yield_completions(
            commandline, cursor_position, completions_count)

        selected_completion = iterfzf(
            completions_generator,
            prompt='🤖 ',
            cycle=True,
            __extra__=['--height=20%', '--layout=reverse', '--margin=1,1'])
        if selected_completion:
            print(selected_completion)
        else:
            print(commandline)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        engine.get_logger().exception(e)
