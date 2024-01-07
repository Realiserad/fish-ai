from openai import OpenAI
from configparser import ConfigParser
from os import path
import logging
from logging.handlers import SysLogHandler
from time import time_ns

def get_logger():
    logger = logging.getLogger()
    # Explain the line below
    handler = SysLogHandler(address = '/dev/log')
    logger.addHandler(handler)
    if get_config().get('fish-ai', 'debug') == 'True':
        logger.setLevel(logging.DEBUG)
    return logger

def get_system_prompt():
    return {
        'role': 'system',
        'content': '''
        You are a programming assistant. You may consult Stack Overflow for answers.
        '''
    }

def get_config():
    config = ConfigParser()
    config.read(path.expanduser('~/.config/fish-ai.ini'))
    return config

def get_response(messages):
    config = get_config()
    client = OpenAI(
        base_url = config.get('fish-ai', 'server'),
        api_key = config.get('fish-ai', 'api_key'),
    )
    # Get unix timestamp
    start_time = time_ns()
    completions = client.chat.completions.create(
        model = config.get('fish-ai', 'model'),
        max_tokens = 1024,
        messages = messages,
        stream = False,
        temperature = 0.2,
        n = 1,
    )
    end_time = time_ns()
    response = completions.choices[0].message.content.strip(' `')
    get_logger().debug('Response received from backend: ' + response)
    get_logger().debug('Processing time: ' + str(round((end_time - start_time) / 1000000)) + ' ms.')
    return response
