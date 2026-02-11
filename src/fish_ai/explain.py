# -*- coding: utf-8 -*-

from fish_ai import engine
import textwrap


def get_instructions(commandline):
    return [
        {
            'role': 'system',
            'content': textwrap.dedent('''\
            Respond with a couple of sentences in a single paragraph which
            explain the fish shell command(s) given by the user. Try to keep
            it brief. Do not use markdown formatting or numbered lists.

            The response must begin with a verb. Use imperative mood (also
            known as instructional writing).

            The sentences should be written in {language}.

            You may use the following manpage to help explain the command:

            {manpage}''').format(
                language=engine.get_config('language') or 'English',
                manpage=engine.get_manpage(commandline.split()[0]))
        },
        {
            'role': 'user',
            'content': 'df -h'
        },
        {
            'role': 'assistant',
            'content': 'List all disks on the system'
        },
        {
            'role': 'user',
            'content': 'docker pull alpine:3'
        },
        {
            'role': 'assistant',
            'content': 'Pull the Alpine 3 container from DockerHub'
        },
        {
            'role': 'user',
            'content': 'sed -i "s/foo/bar/g" docker-compose.yml'
        },
        {
            'role': 'assistant',
            'content': 'Substitute all occurrences of the string "foo" with ' +
                    'the string "bar" in the file "docker-compose.yml"'
        },
        {
            'role': 'user',
            'content': commandline
        }
    ]


def get_messages(commandline):
    return [engine.get_system_prompt()] + get_instructions(commandline)


def explain():
    engine.get_logger().info('----- BEGIN SESSION -----')

    commandline = engine.get_args()[0]

    try:
        engine.get_logger().debug('Explaining commandline: ' + commandline)
        response = engine.get_response(messages=get_messages(commandline))
        print('# ' + response.replace('\n', ' '), end='')
    except Exception as e:
        engine.get_logger().exception(e)
        print('# An error occurred when running fish-ai. More info: ' +
              str(e.args), end='')
    finally:
        engine.get_logger().info('----- END SESSION -----')
