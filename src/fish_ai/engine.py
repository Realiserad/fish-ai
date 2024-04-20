# -*- coding: utf-8 -*-

from openai import OpenAI
from openai import AzureOpenAI
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from configparser import ConfigParser
from os import path
from os.path import isfile
import platform
import logging
from logging.handlers import SysLogHandler, RotatingFileHandler
from time import time_ns

config = ConfigParser()
config.read(path.expanduser('~/.config/fish-ai.ini'))


def get_logger():
    logger = logging.getLogger()

    if path.exists('/dev/log'):
        # Syslog on GNU/Linux
        handler = SysLogHandler(address='/dev/log')
        logger.addHandler(handler)
    elif path.exists('/var/run/syslog'):
        # Syslog on OS X
        handler = SysLogHandler(address='/var/run/syslog')
        logger.addHandler(handler)

    if get_config('log'):
        handler = RotatingFileHandler(path.expanduser(get_config('log')),
                                      backupCount=0,
                                      maxBytes=1024*1024)
        logger.addHandler(handler)

    if get_config('debug') == 'True':
        logger.setLevel(logging.DEBUG)
    return logger


def get_os():
    if platform.system() == 'Linux':
        if isfile('/etc/os-release'):
            with open('/etc/os-release') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip('"')
        return 'GNU/Linux'
    if platform.system() == 'Darwin':
        return 'Mac OS X ' + platform.mac_ver()[0]
    return 'Unknown'


def get_system_prompt():
    return {
        'role': 'system',
        'content': '''
        You are a shell scripting assistant working inside a fish shell.
        The operating system is {os}.
        You may consult Stack Overflow and the official Fish shell
        documentation for answers. If you are unable to fulfill the request,
        respond with a short message starting with "error: ".
        '''.format(os=get_os())
    }


def get_config(key):
    active_section = config.get(section='fish-ai', option='configuration')
    if key not in config[active_section]:
        return None
    return config.get(section=active_section, option=key)


def get_openai_client():
    if (get_config('provider') == 'azure'):
        return AzureOpenAI(
            azure_endpoint=get_config('server'),
            api_version='2023-07-01-preview',
            api_key=get_config('api_key'),
            azure_deployment=get_config('azure_deployment'),
        )
    elif (get_config('provider') == 'self-hosted'):
        return OpenAI(
            base_url=get_config('server'),
            api_key=get_config('api_key') or 'dummy',
        )
    elif (get_config('provider') == 'openai'):
        return OpenAI(
            api_key=get_config('api_key'),
            organization=get_config('organization'),
        )
    else:
        raise Exception('Unknown provider "{}".'
                        .format(get_config('provider')))


def create_message_history(messages):
    """
    Create message history which can be used with Gemini.
    Google uses a different chat history format than OpenAI.
    The message content should be put in a parts array and
    system messages are not supported.
    """
    outputs = []
    system_messages = []
    for message in messages:
        if message.get('role') == 'system':
            system_messages.append(message.get('content'))
    for i in range(len(messages) - 1):
        message = messages[i]
        if message.get('role') == 'user':
            outputs.append({
                'role': 'user',
                'parts': system_messages + [message.get('content')] if i == 0
                else [message.get('content')]
            })
        elif message.get('role') == 'assistant':
            outputs.append({
                'role': 'model',
                'parts': [message.get('content')]
            })
    return outputs


def get_response(messages):
    start_time = time_ns()

    if get_config('provider') == 'google':
        genai.configure(api_key=get_config('api_key'))
        model = genai.GenerativeModel(get_config('model') or 'gemini-pro')
        chat = model.start_chat(history=create_message_history(messages))
        generation_config = GenerationConfig(
            candidate_count=1,
            temperature=float(get_config('temperature') or '0.2'))
        response = (chat.send_message(generation_config=generation_config,
                                      content=messages[-1].get('content'),
                                      stream=False)
                    .text.strip(' `'))
    else:
        completions = get_openai_client().chat.completions.create(
            model=get_config('model') or 'default',
            max_tokens=4096,
            messages=messages,
            stream=False,
            temperature=float(get_config('temperature') or '0.2'),
            n=1,
        )
        response = completions.choices[0].message.content.strip(' `')

    end_time = time_ns()
    get_logger().debug('Response received from backend: ' + response)
    get_logger().debug('Processing time: ' +
                       str(round((end_time - start_time) / 1000000)) + ' ms.')
    if response.startswith('error: '):
        raise Exception(response)
    return response
