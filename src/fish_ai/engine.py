# -*- coding: utf-8 -*-

import logging
from logging.handlers import SysLogHandler, RotatingFileHandler
from os.path import isfile, exists, expanduser
from platform import system, mac_ver
from time import time_ns
import textwrap
from os import access, R_OK
from re import match
from binaryornot.check import is_binary
from subprocess import run, PIPE, DEVNULL, Popen
from itertools import islice
from sys import argv

from fish_ai.redact import redact
from fish_ai.config import get_config


logger = logging.getLogger()

if exists('/dev/log'):
    # Syslog on Linux
    handler = SysLogHandler(address='/dev/log')
    logger.addHandler(handler)
elif exists('/var/run/syslog'):
    # Syslog on macOS
    handler = SysLogHandler(address='/var/run/syslog')
    logger.addHandler(handler)

if get_config('log'):
    handler = RotatingFileHandler(expanduser(get_config('log')),
                                  backupCount=0,
                                  maxBytes=1024*1024)
    logger.addHandler(handler)

if get_config('debug') == 'True':
    logger.setLevel(logging.DEBUG)


def get_logger():
    return logger


def get_args():
    return list.copy(argv[1:])


def get_os():
    if system() == 'Linux':
        if isfile('/etc/os-release'):
            with open('/etc/os-release') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip('"')
        return 'Linux'
    if system() == 'Darwin':
        return 'macOS ' + mac_ver()[0]
    return 'Unknown'


def get_manpage(command):
    try:
        get_logger().debug('Retrieving manpage for command "{}"'
                           .format(command))
        helppage = run(
            ['fish', '-c', command + ' --help'],
            stdout=PIPE,
            stderr=DEVNULL)
        if helppage.returncode == 0:
            output = helppage.stdout.decode('utf-8')
            if len(output) > 2000:
                return output[:2000] + ' [...]'
            else:
                return output
        return 'No manpage available.'
    except Exception as e:
        get_logger().debug(
            'Failed to retrieve manpage for command "{}". Reason: {}'.format(
                command, str(e)))
        return 'No manpage available.'


def get_file_info(words):
    """
    If the user is mentioning a file, return the filename and its file
    contents.
    """
    for word in words.split():
        filename = word.rstrip(',.!').strip('"\'')
        if not match(r'[A-Za-z0-9_\-]+\.[a-z]+', filename.split('/')[-1]):
            continue
        if not isfile(filename):
            continue
        if not access(filename, R_OK):
            continue
        if is_binary(filename):
            continue
        with open(filename, 'r') as file:
            get_logger().debug('Loading file: ' + filename)
            return filename, file.read(3072)
    return None, None


def get_commandline_history(commandline, cursor_position):
    history_size = int(get_config('history_size') or 0)
    if history_size == 0:
        get_logger().debug('Commandline history disabled.')
        return 'No commandline history available.'

    def yield_history():
        command = commandline.split(' ')[0]
        before_cursor = commandline[:cursor_position]
        after_cursor = commandline[cursor_position:]

        proc = Popen(
            ['fish', '-c', 'history search --prefix "{}"'.format(command)],
            stdout=PIPE,
            stderr=DEVNULL)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            item = line.decode('utf-8').strip()
            if item.startswith(before_cursor) and item.endswith(after_cursor):
                yield item

    history = list(islice(yield_history(), history_size))

    if len(history) == 0:
        return 'No commandline history available.'
    return '\n'.join(history)


def get_system_prompt():
    return {
        'role': 'system',
        'content': textwrap.dedent('''\
        You are a shell scripting assistant working inside a fish shell.
        The operating system is {os}. Your output must to be shell runnable.
        You may consult Stack Overflow and the official Fish shell
        documentation for answers.
        ''').format(os=get_os())
    }


def get_openai_client():
    if (get_config('provider') == 'azure'):
        from openai import AzureOpenAI
        return AzureOpenAI(
            azure_endpoint=get_config('server'),
            api_version='2023-07-01-preview',
            api_key=get_config('api_key'),
            azure_deployment=get_config('azure_deployment'),
        )
    elif (get_config('provider') == 'self-hosted'):
        from openai import OpenAI
        return OpenAI(
            base_url=get_config('server'),
            api_key=get_config('api_key') or 'dummy',
        )
    elif (get_config('provider') == 'openai'):
        from openai import OpenAI
        return OpenAI(
            api_key=get_config('api_key'),
            organization=get_config('organization'),
        )
    elif (get_config('provider') == 'deepseek'):
        # DeepSeek is compatible with OpenAI Python SDK
        from openai import OpenAI
        return OpenAI(
            api_key=get_config('api_key'),
            base_url='https://api.deepseek.com'
        )
    else:
        raise Exception('Unknown provider "{}".'
                        .format(get_config('provider')))


def get_messages_for_anthropic(messages):
    user_messages = []
    system_messages = []
    for message in messages:
        if message.get('role') == 'system':
            system_messages.append(message.get('content'))
        else:
            user_messages.append(message)
    return system_messages, user_messages


def create_system_prompt(messages):
    return '\n\n'.join(
        list(
            map(lambda message: message.get('content'),
                list(
                    filter(
                        lambda message: message.get('role') == 'system',
                        messages)))))


def get_response(messages):
    messages = redact(messages)

    start_time = time_ns()

    if get_config('provider') == 'huggingface':
        from hugchat import hugchat
        from hugchat.login import Login

        email = get_config('email')
        password = get_config('api_key') or get_config('password')
        cookies = Login(email, password).login(
            cookie_dir_path=expanduser('~/.fish-ai/cookies/'),
            save_cookies=True)

        bot = hugchat.ChatBot(
            cookies=cookies.get_dict(),
            system_prompt=create_system_prompt(messages),
            default_llm=get_config('model') or
            'meta-llama/Llama-3.3-70B-Instruct')

        response = bot.chat(
            messages[-1].get('content')).wait_until_done()
        bot.delete_conversation(bot.get_conversation_info())
    elif get_config('provider') == 'mistral':
        from mistralai import Mistral

        client = Mistral(
            api_key=get_config('api_key'),
            server_url=get_config('server') or 'https://api.mistral.ai'
        )
        params = {
            'model': get_config('model') or 'mistral-large-latest',
            'messages': messages,
        }
        temp = get_config('temperature')
        if temp != 'None':
            params['temperature'] = float(temp or '0.2')
        completions = client.chat.complete(**params)
        response = completions.choices[0].message.content
    elif get_config('provider') == 'anthropic':
        from anthropic import Anthropic

        client = Anthropic(
            api_key=get_config('api_key')
        )
        system_messages, user_messages = get_messages_for_anthropic(messages)
        params = {
            'model': get_config('model') or 'claude-3-7-sonnet-latest',
            'system': '\n'.join(system_messages),
            'messages': user_messages,
            'max_tokens': 4096
        }
        temp = get_config('temperature')
        if temp != 'None':
            params['temperature'] = float(temp or '0.2')
        completions = client.messages.create(**params)
        response = completions.content[0].text
    elif get_config('provider') == 'cohere':
        from cohere import ClientV2

        api_key = get_config('api_key')
        client = ClientV2(api_key)
        params = {
            'model': get_config('model') or 'command-r-plus-08-2024',
            'messages': messages,
        }
        temp = get_config('temperature')
        if temp != 'None':
            params['temperature'] = float(temp or '0.2')
        completions = client.chat(**params)
        response = completions.message.content[0].text
    else:
        params = {
            'model': get_config('model') or 'gpt-4o',
            'messages': messages,
            'stream': False,
            'n': 1,
        }
        temp = get_config('temperature')
        if temp != 'None':
            params['temperature'] = float(temp or '0.2')
        completions = get_openai_client().chat.completions.create(**params)
        response = completions.choices[0].message.content

    response = '\n'.join(line.strip(' `') for line in response.split('\n'))

    end_time = time_ns()
    get_logger().debug('Response received from backend: ' + response)
    get_logger().debug('Processing time: ' +
                       str(round((end_time - start_time) / 1000000)) + ' ms.')
    return response
