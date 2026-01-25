# -*- coding: utf-8 -*-

from fish_ai import engine
from iterfzf import iterfzf
import textwrap
from subprocess import getoutput
from fish_ai.config import get_config
from base64 import b64encode, b64decode


def get_instructions(commandline,
                     cursor_position,
                     completions_count,
                     additional_instructions):
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
            command should be separated by a blank line. Preserve any
            indentation. Do not explain. Only respond with the autocompleted
            commands.

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

    if additional_instructions is not None:
        instructions[-1]['content'] += textwrap.dedent('''\
            The following additional instructions were provided by the user:\
            {additional_instructions}
            ''').format(additional_instructions=additional_instructions)

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


def get_messages(commandline,
                 cursor_position,
                 completions_count,
                 additional_instructions):
    return [engine.get_system_prompt()] + get_instructions(
        commandline=commandline,
        cursor_position=cursor_position,
        completions_count=completions_count,
        additional_instructions=additional_instructions)


def yield_completions(commandline,
                      cursor_position,
                      completions_count,
                      additional_instructions=None):
    yield commandline
    messages = get_messages(
        commandline=commandline,
        cursor_position=cursor_position,
        completions_count=completions_count,
        additional_instructions=additional_instructions)

    try:
        response = engine.get_response(messages=messages)
        empty_line = '\n\n'
        for completion in response.split(empty_line):
            engine.get_logger().debug('Created completion: ' + completion)
            yield completion
    except Exception as e:
        engine.get_logger().exception(e)


def get_reload_command(commandline, cursor_position):
    return ('reload({install_dir}/bin/refine {commandline} '
            '{cursor_position} {completions_count} '
            '{instructions})+clear-query').format(
                install_dir=engine.get_install_dir(),
                # b64 encode commandline buffer to deal with single quotes
                commandline=b64encode(commandline.encode()).decode(),
                cursor_position=cursor_position,
                completions_count=engine.get_config(
                    'refined_completions') or '3',
                instructions='{q}'
            )


def autocomplete():
    engine.get_logger().info('----- BEGIN SESSION -----')

    commandline = engine.get_args()[0]
    if commandline.startswith('#'):
        engine.get_logger().debug(
            'Codifying commandline before completion using instructions: ' +
            commandline[1:].strip())
        from fish_ai.codify import get_messages
        commandline = engine.get_response(
            messages=get_messages(commandline[1:].strip()))
        cursor_position = len(commandline)
    else:
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

        fzf_preview_height = 100 if '\n' in commandline else 20
        fzf_extra = [
            f'--height={fzf_preview_height}%',
            '--layout=reverse',
            '--margin=1,1'
        ]
        if '\n' in commandline:
            fzf_extra.append('--highlight-line')
            fzf_extra.append('--gap')

        selected_completion = iterfzf(
            completions_generator,
            prompt='🤖 ',
            cycle=True,
            read0=True,
            bind={
                'ctrl-p': get_reload_command(commandline, cursor_position),
            },
            __extra__=fzf_extra)
        if selected_completion:
            print(selected_completion, end='')
        else:
            print(commandline, end='')
    except Exception as e:
        engine.get_logger().exception(e)
        print('# An error occurred when running fish-ai. More info: ' +
              str(e.args), end='')
    finally:
        engine.get_logger().info('----- END SESSION -----')


def refine_completions():
    commandline = b64decode(engine.get_args()[0]).decode()
    cursor_position = int(engine.get_args()[1])
    refined_completions_count = int(engine.get_args()[2])
    instructions = engine.get_args()[3]

    before_cursor = commandline[:cursor_position]
    after_cursor = commandline[cursor_position:]

    engine.get_logger().debug(('Refining {completions_count} completions '
                               'for "{before_cursor}█{after_cursor}" using '
                               'instructions "{instructions}".').format(
                                completions_count=refined_completions_count,
                                before_cursor=before_cursor,
                                after_cursor=after_cursor,
                                instructions=instructions
    ))

    for completion in yield_completions(commandline,
                                        cursor_position,
                                        refined_completions_count,
                                        instructions):
        print(completion)
