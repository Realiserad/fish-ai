# -*- coding: utf-8 -*-

from fish_ai import engine
from iterfzf import iterfzf
import textwrap
from subprocess import getoutput
from fish_ai.config import get_config


def get_instructions(commandline, cursor_position, completions_count):
    before_cursor = commandline[:cursor_position]
    after_cursor = commandline[cursor_position:]
    instructions = [
        {
            'role': 'system',
            'content': textwrap.dedent('''\
            Provide autocompletion for a fish shell commandline given by the
            user. The █ character in the commandline marks the position of the
            cursor where the user is typing. Respond with the number of
            autocompleted commands given by the user. Each autocompleted
            command should be provided on a separate line. Do not explain.
            Only respond with the autocompleted commands.

            You may use the following commandline history to personalise
            the output:

            {commandline_history}''').format(
                commandline_history=engine.get_commandline_history(
                    commandline, cursor_position))
        },
        {
            'role': 'user',
            'content': textwrap.dedent('''\
            Provide 1 autocompleted commands for the commandline:

            openssl s_client█google.com:443''')
        },
        {
            'role': 'assistant',
            'content': 'openssl s_client -connect google.com:443'
        },
        {
            'role': 'user',
            'content': textwrap.dedent('''\
            Provide 2 autocompleted commands for the commandline:

            docker run -it█ python:3''')
        },
        {
            'role': 'assistant',
            'content': '''\
            docker run -it --rm python:3
            docker run -it --rm --entrypoint /bin/sh python:3'''
        },
        {
            'role': 'user',
            'content': textwrap.dedent('''\
            Provide {n} autocompleted commands for the commandline:

            {before_cursor}█{after_cursor}

            ''').format(
                n=completions_count,
                before_cursor=before_cursor,
                after_cursor=after_cursor)
        },
    ]

    if after_cursor.strip() == '':
        instructions[-1]['content'] += textwrap.dedent('''\
            The autocompleted command must begin with "{before_cursor}".
            ''').format(before_cursor=before_cursor)
    else:
        instructions[-1]['content'] += textwrap.dedent('''\
            The autocompleted command must begin with "{before_cursor}" and end
            with "{after_cursor}".
            ''').format(
                before_cursor=before_cursor,
                after_cursor=after_cursor)

    pipe = get_pipe(before_cursor)
    if (get_config('preview_pipe') == 'True' and pipe != ''):
        engine.get_logger().debug('Detected pipe: ' + pipe)
        output = getoutput(pipe)
        if len(output) > 2000:
            short_output = output[:2000] + ' [...]'
        else:
            short_output = output
        instructions[-1]['content'] = textwrap.dedent('''\
            The output from '{command}' is:

            {output}

            ''').format(
                command=pipe,
                output=short_output) + instructions[-1]['content']
        return instructions

    (filename, file_contents) = engine.get_file_info(commandline)
    if filename:
        instructions[-1]['content'] = textwrap.dedent('''\
            The content of the file {filename} is'

            {file_contents}

            ''').format(
                filename=filename,
                file_contents=file_contents) + instructions[-1]['content']

    return instructions


def get_pipe(buffer):
    opening_parens_pos = [-1]
    last_pipe_pos = -1
    processing_string = False
    for i, char in enumerate(buffer):
        escape_chars = 0
        j = i - 1
        while buffer[j] == '\\' and j >= 0:
            escape_chars += 1
            j -= 1
        escape = escape_chars % 2 == 1
        if not escape and (char == '"' or char == "'"):
            processing_string = not processing_string
        if not processing_string:
            if char == '(':
                opening_parens_pos.append(i)
            elif char == ')' and len(opening_parens_pos) > 1:
                opening_parens_pos.pop()
            elif char == '|':
                last_pipe_pos = i
    if last_pipe_pos > -1:
        return buffer[opening_parens_pos[-1] + 1:last_pipe_pos].strip(' ')
    else:
        return ''


def get_messages(commandline, cursor_position, completions_count):
    return [engine.get_system_prompt()] + get_instructions(
        commandline=commandline,
        cursor_position=cursor_position,
        completions_count=completions_count)


def yield_completions(commandline, cursor_position, completions_count):
    yield commandline
    messages = get_messages(
        commandline=commandline,
        cursor_position=cursor_position,
        completions_count=completions_count)

    try:
        response = engine.get_response(messages=messages)
        for completion in response.split('\n'):
            engine.get_logger().debug('Created completion: ' + completion)
            yield completion
    except Exception as e:
        engine.get_logger().exception(e)


def autocomplete():
    engine.get_logger().info('----- BEGIN SESSION -----')

    commandline = engine.get_args()[0]
    cursor_position = int(engine.get_args()[1])
    before_cursor = commandline[:cursor_position]
    after_cursor = commandline[cursor_position:]

    try:
        engine.get_logger().debug('Autocompleting commandline: {}'.format(
            before_cursor + '█' + after_cursor))
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
            print(selected_completion, end='')
        else:
            print(commandline, end='')
    except Exception as e:
        engine.get_logger().exception(e)
        print('# An error occurred when running fish-ai. More info: ' +
              str(e.args), end='')
        exit(1)
    finally:
        engine.get_logger().info('----- END SESSION -----')
