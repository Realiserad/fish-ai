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
import subprocess
import textwrap
import sys
from hugchat import hugchat
from hugchat.login import Login
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

config = ConfigParser()
config.read(path.expanduser('~/.config/fish-ai.ini'))


def get_args():
    return list.copy(sys.argv[1:])


def get_logger():
    logger = logging.getLogger()

    if path.exists('/dev/log'):
        # Syslog on Linux
        handler = SysLogHandler(address='/dev/log')
        logger.addHandler(handler)
    elif path.exists('/var/run/syslog'):
        # Syslog on macOS
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
        return 'Linux'
    if platform.system() == 'Darwin':
        return 'macOS ' + platform.mac_ver()[0]
    return 'Unknown'


def get_manpage(command):
    try:
        helppage = subprocess.run(
            ['fish', '-c', command + ' --help'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL)
        if helppage.returncode == 0:
            return helppage.stdout.decode('utf-8')
        return 'No manpage available.'
    except Exception as e:
        get_logger().debug(
            'Failed to get manpage for command "{}". Reason: {}'.format(
                command, str(e)))
        return 'No manpage available.'


def get_commandline_history(commandline):
    history_size = get_config('history_size') or '0'
    commandline_history = subprocess.check_output(
        [
            'fish', '-c',
            'history search --max {history_size} --prefix "{commandline}"'
            .format(history_size=history_size,
                    commandline=commandline.replace('"', "'")
                    )
        ]).decode('utf-8')
    if commandline_history.strip() == '':
        return 'No commandline history available.'
    return commandline_history


def get_system_prompt():
    return {
        'role': 'system',
        'content': textwrap.dedent('''\
        You are a shell scripting assistant working inside a fish shell.
        The operating system is {os}. Your output must to be shell runnable.
        You may consult Stack Overflow and the official Fish shell
        documentation for answers. If you are unable to fulfill the request,
        respond with a short message starting with "error: ".
        ''').format(os=get_os())
    }


def get_config(key):
    if config.has_section('fish-ai'):
        active_section = config.get(section='fish-ai', option='configuration')
    else:
        # There is no configuration file or the user made a mistake.
        # Just return 'None' here to simplify testing.
        return None

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


def get_messages_for_gemini(messages):
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


def get_messages_for_mistral(messages):
    output = []
    for message in messages:
        output.append(
            ChatMessage(role=message.get('role'),
                        content=message.get('content')))
    return output


def create_system_prompt(messages):
    return '\n\n'.join(
        list(
            map(lambda message: message.get('content'),
                list(
                    filter(
                        lambda message: message.get('role') == 'system',
                        messages
                    )
            )
            )
        )
    )


def get_response(messages):
    start_time = time_ns()

    if get_config('provider') == 'google':
        genai.configure(api_key=get_config('api_key'))
        model = genai.GenerativeModel(
            get_config('model') or 'gemini-1.5-flash')
        chat = model.start_chat(history=get_messages_for_gemini(messages))
        generation_config = GenerationConfig(
            candidate_count=1,
            temperature=float(get_config('temperature') or '0.2'))
        response = (chat.send_message(generation_config=generation_config,
                                      content=messages[-1].get('content'),
                                      stream=False)
                    .text.strip(' `'))
    elif get_config('provider') == 'huggingface':
        email = get_config('email')
        password = get_config('password')
        cookies = Login(email, password).login(
            cookie_dir_path=path.expanduser('~/.fish-ai/cookies/'),
            save_cookies=True)

        bot = hugchat.ChatBot(
            cookies=cookies.get_dict(),
            system_prompt=create_system_prompt(messages),
            default_llm=get_config('model') or
            'meta-llama/Meta-Llama-3-70B-Instruct')

        response = bot.chat(messages[-1].get('content')).wait_until_done()
        bot.delete_conversation(bot.get_conversation_info())
    elif get_config('provider') == 'mistral':
        client = MistralClient(
            api_key=get_config('api_key')
        )
        completions = client.chat(
            model=get_config('model') or 'mistral-large-latest',
            messages=get_messages_for_mistral(messages),
            max_tokens=1024,
            temperature=float(get_config('temperature') or '0.2'),
        )
        response = completions.choices[0].message.content.strip(' `')
    else:
        completions = get_openai_client().chat.completions.create(
            model=get_config('model') or 'gpt-4',
            max_tokens=1024,
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
