#!/usr/bin/env python3

from sys import stdin
import engine as ai

commandline = stdin.read()
if commandline.startswith('# '):
    commandline = commandline[2:]

user_prompt = {
    'role': 'user',
    'content': '''
    RESPOND WITH A COMMAND WHICH DOES THE FOLLOWING:

    {}

    Only respond with the command. Only respond with a single line. Do not explain.
    The command must be compatible with Fish shell.

    Examples:

    User input: List all disks on the system.
    Respond with: df -h

    User input: Pull the Alpine 3 container from DockerHub.
    Respond with: docker pull alpine:3

    User input: Substitute all occurrences of the string 'foo' with the string 'bar' in the file 'docker-compose.yml'
    Respond with: sed -i 's/foo/bar/g' docker-compose.yml
    '''.format(commandline)
}

try:
    response = ai.get_response(messages = [ai.get_system_prompt(), user_prompt])
    print(response)
except:
    # Leave the commandline untouched
    print(commandline)