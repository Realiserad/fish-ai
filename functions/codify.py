#!/usr/bin/env python3

from sys import stdin
import engine as ai

commandline = stdin.read()
if commandline.startswith('# '):
    commandline = commandline[2:]

user_prompt = {
    'role': 'user',
    'content': '''
    Respond with a shell command which does the following:

    [INST] {} [/INST]

    Only respond with a command. Only respond with a single line.
    Do not use markdown formatting.

    Examples:

    [INST] List all disks on the system [/INST]
    df -h

    [INST] Pull the Alpine 3 container from DockerHub [/INST]
    docker pull alpine:3

    [INST] Substitute all occurrences of the string 'foo' with the string 'bar' in the file 'docker-compose.yml' [/INST]
    sed -i 's/foo/bar/g' docker-compose.yml
    '''.format(commandline)
}

try:
    ai.get_logger().debug('Codifying commandline: ' + commandline)
    response = ai.get_response(messages = [ai.get_system_prompt(), user_prompt])
    print(response)
except Exception as e:
    ai.get_logger().exception(e)
    # Leave the commandline untouched
    print(commandline)