#!/usr/bin/env python3

from sys import stdin
import engine as ai

commandline = stdin.read()

user_prompt = {
    'role': 'user',
    'content': '''
    Respond with a single sentence which explains the following command:

    {}

    The sentence must begin with a verb.

    Examples:

    [INST] df -h [/INST]
    List all disks on the system

    [INST] docker pull alpine:3 [/INST]
    Pull the Alpine 3 container from DockerHub

    [INST] sed -i 's/foo/bar/g' docker-compose.yml [/INST]
    Substitute all occurrences of the string 'foo' with the string 'bar' in the file 'docker-compose.yml'
    '''.format(commandline)
}

try:
    ai.get_logger().debug('Explaining commandline: ' + commandline)
    response = ai.get_response(messages = [ai.get_system_prompt(), user_prompt])
    print(response)
except Exception as e:
    ai.get_logger().exception(e)
    # Leave the commandline untouched
    print(commandline)