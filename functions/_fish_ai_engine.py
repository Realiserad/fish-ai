# -*- coding: utf-8 -*-

from openai import OpenAI
from openai import AzureOpenAI
from configparser import ConfigParser
from os import path
import logging
from logging.handlers import SysLogHandler
from time import time_ns

config = ConfigParser()
config.read(path.expanduser('~/.config/fish-ai.ini'))


def get_logger():
    logger = logging.getLogger()
    handler = SysLogHandler(address='/dev/log')
    logger.addHandler(handler)
    if get_config('debug') == 'True':
        logger.setLevel(logging.DEBUG)
    return logger


def get_system_prompt():
    return {
        'role': 'system',
        'content': '''
        You are a shell scripting assistant working inside a fish shell.
        You may consult Stack Overflow and the official Fish shell
        documentation for answers. If you are unable to fulfill the request,
        respond with a short message starting with "error: ".
        '''
    }


def get_config(key):
    active_section = config.get(section='fish-ai', option='configuration')
    if key not in config[active_section]:
        return None
    return config.get(section=active_section, option=key)


def get_client():
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


def get_response(messages):
    start_time = time_ns()
    completions = get_client().chat.completions.create(
        model=get_config('model'),
        max_tokens=4096,
        messages=messages,
        stream=False,
        temperature=0.2,
        n=1,
    )
    end_time = time_ns()
    response = completions.choices[0].message.content.strip(' `')
    get_logger().debug('Response received from backend: ' + response)
    get_logger().debug('Processing time: ' +
                       str(round((end_time - start_time) / 1000000)) + ' ms.')
    if response.startswith('error: '):
        raise Exception(response)
    return response
