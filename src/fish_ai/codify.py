# -*- coding: utf-8 -*-

from fish_ai import engine
import textwrap


def get_instructions(commandline):
    instructions = [
        {
            'role': 'system',
            'content': textwrap.dedent('''\
            Respond with a fish shell command which carries out the user's
            task. Do not explain. Only respond with a single line.''')
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
    (filename, file_contents) = engine.get_file_info(commandline)
    if filename:
        instructions[-1]['content'] += textwrap.dedent('''\
            The content of the file {filename} is'

            {file_contents}''').format(
                filename=filename,
                file_contents=file_contents)
    return instructions


def get_messages(commandline):
    return [engine.get_system_prompt()] + get_instructions(commandline)


def codify():
    engine.get_logger().info('----- BEGIN SESSION -----')

    commandline = engine.get_args()[0]
    if commandline.startswith('# '):
        commandline = commandline[2:]

    try:
        engine.get_logger().debug('Codifying commandline: ' + commandline)
        response = engine.get_response(messages=get_messages(commandline))
        print(response, end='')
    except Exception as e:
        engine.get_logger().exception(e)
        print('# An error occurred when running fish-ai. More info: ' +
              str(e.args), end='')
    finally:
        engine.get_logger().info('----- END SESSION -----')
