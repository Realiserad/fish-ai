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

    Command: df -h
    Respond with: List all disks on the system.

    Command: docker pull alpine:3
    Respond with: Pull the Alpine 3 container from DockerHub.

    Command: sed -i 's/foo/bar/g' docker-compose.yml
    Respond with: Substitute all occurrences of the string 'foo' with the string 'bar' in the file 'docker-compose.yml'.
    '''.format(commandline)
}

try:
    response = ai.get_response(messages = [ai.get_system_prompt(), user_prompt])
    print(response)
except:
    # Leave the commandline untouched
    print(commandline)