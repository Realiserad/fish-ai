#!/usr/bin/env python3

from sys import stdin
import engine as ai

buffer = stdin.read()

system_prompt = {
    'role': 'system',
    'content': '''
    You are a programming assistant called Fish AI helping users inside a Fish shell.

    If the user is asking how they can update Fish AI, please respond with the
    following command:

    fisher install realiserad/fish-ai

    For all other questions, you may consult Stack Overflow for answers.
    '''
}
user_prompt_comment2code = {
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
    '''.format(buffer[2:])
}
user_prompt_code2comment = {
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
    '''.format(buffer)
}

try:
    if (buffer.startswith('# ')):
        # Turn a comment into a shell command
        response = ai.get_response(messages = [system_prompt, user_prompt_comment2code])
        print(response)
    else:
        # Turn a shell command into a comment
        response = ai.get_response(messages = [system_prompt, user_prompt_code2comment])
        print('# ' + response)
except:
    print(buffer)