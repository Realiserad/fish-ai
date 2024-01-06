from openai import OpenAI
from configparser import ConfigParser
from os import path

def get_system_prompt():
    return {
        'role': 'system',
        'content': '''
        You are a programming assistant called Fish AI helping users inside a Fish shell.

        If the user is asking how they can update Fish AI, please respond with the
        following command:

        fisher install realiserad/fish-ai

        For all other questions, you may consult Stack Overflow for answers.
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
    completions = client.chat.completions.create(
        model = config.get('fish-ai', 'model'),
        max_tokens = 1024,
        messages = messages,
        stream = False,
        temperature = 0.2,
        n = 1,
    )
    return completions.choices[0].message.content.strip(' `')
