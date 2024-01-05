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

    Only respond with command. Only respond with a single line. Do not explain or add
    any additional text to the response. Never use markdown backticks or any other
    formatting. Do not use shebangs. The command must be compatible with Fish shell.

    Examples:

    [User] List all disks on the system.
    [Fish AI] df -h

    [User] Pull the Alpine 3 container from DockerHub.
    [Fish AI] docker pull alpine:3

    [User] Substitute all occurrences of the string 'foo' with the string 'bar' in the file 'docker-compose.yml'
    [Fish AI] sed -i 's/foo/bar/g' docker-compose.yml
    '''.format(buffer[2:])
}
user_prompt_code2comment = {
    'role': 'user',
    'content': '''
    Respond with a single sentence which explains the following command:

    {}

    The sentence must begin with a verb.

    Examples:

    [User] df -h
    [Fish AI] List all disks on the system.

    [User] docker pull alpine:3
    [Fish AI] Pull the Alpine 3 container from DockerHub.

    [User] sed -i 's/foo/bar/g' docker-compose.yml
    [Fish AI] Substitute all occurrences of the string 'foo' with the string 'bar' in the file 'docker-compose.yml'
    '''.format(buffer)
}

if (buffer.startswith('# ')):
    # Turn a comment into a shell command
    response = ai.get_response(messages = [system_prompt, user_prompt_comment2code])
    print(response.strip())
else:
    # Turn a shell command into a comment
    response = ai.get_response(messages = [system_prompt, user_prompt_code2comment])
    print('# ' + response.strip())
