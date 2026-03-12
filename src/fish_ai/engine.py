# -*- coding: utf-8 -*-

import logging
from logging.handlers import SysLogHandler, RotatingFileHandler
from os.path import isfile, exists, expanduser, expandvars
from platform import system, mac_ver
from time import time_ns
import textwrap
from os import access, R_OK, environ
from re import match
from binaryornot.check import is_binary
from subprocess import run, PIPE, DEVNULL, Popen
from itertools import islice
from sys import argv

from fish_ai.redact import redact
from fish_ai.config import get_config

# LazyLLM 统一 Provider 接入
import lazyllm

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


def get_custom_headers():
    """
    Parse custom headers from config.

    The headers config option should be in the format:
    headers = Header-Name: value, Another-Header: value

    This is useful for authentication headers like Cloudflare Access.
    """
    headers_config = get_config('headers')
    if not headers_config:
        return None

    headers = {}
    for header in headers_config.split(','):
        header = header.strip()
        if ':' in header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers if headers else None


def get_messages_for_anthropic(messages):
    """
    Convert OpenAI format messages to Anthropic format.
    
    Args:
        messages: List of messages in OpenAI format
        
    Returns:
        Tuple of (system_messages, user_messages)
    """
    user_messages = []
    system_messages = []
    for message in messages:
        if message.get('role') == 'system':
            system_messages.append(message.get('content'))
        else:
            user_messages.append(message)
    return system_messages, user_messages


def get_messages_for_gemini(messages):
    """
    Create message history which can be used with Gemini.
    Google uses a different chat history format than OpenAI.
    The message content should be put in a parts array and
    system messages are not supported.
    
    Args:
        messages: List of messages in OpenAI format
        
    Returns:
        List of messages in Gemini format
    """
    outputs = []
    system_messages = []
    other_messages = []
    for message in messages:
        if message.get('role') == 'system':
            system_messages.append({'text': message.get('content')})
        else:
            other_messages.append(message)

    for i in range(len(other_messages)):
        message = other_messages[i]
        if message.get('role') == 'user':
            outputs.append({
                'role': 'user',
                'parts': system_messages + [{'text': message.get('content')}]
                if i == 0 else [{'text': message.get('content')}]
            })
        elif message.get('role') == 'assistant':
            outputs.append({
                'role': 'model',
                'parts': [{'text': message.get('content')}]
            })
    return outputs


def create_system_prompt(messages):
    return '\n\n'.join(
        list(
            map(lambda message: message.get('content'),
                list(
                    filter(
                        lambda message: message.get('role') == 'system',
                        messages)))))


def get_lazyllm_chat_module(provider_name, model_name, api_key, server_url=None,
                            azure_deployment=None):
    """
    Get LLM chat module from LazyLLM OnlineChatModule.
    
    使用 LazyLLM 的 OnlineChatModule 统一接入各 LLM 供应商。
    通过配置 source 和 base_url 来支持不同供应商。
    
    Args:
        provider_name: Provider name (openai, anthropic, google, etc.)
        model_name: Model name
        api_key: API key (支持 FISHAI_API_KEY 或 FISHAI_{PROVIDER}_API_KEY)
        server_url: Custom server URL (for self-hosted or Azure)
        azure_deployment: Azure deployment name
        
    Returns:
        LazyLLM OnlineChatModule instance (callable)
        
    Raises:
        Exception: If provider is not supported
    """
    # fish-ai provider 名称到 LazyLLM source 的映射
    # LazyLLM 原生支持的 source: openai, sensenova, glm, kimi, qwen, doubao, ppio, deepseek
    # 对于支持 OpenAI 兼容 API 的供应商，使用 source='openai' + 自定义 base_url
    provider_map = {
        'openai': 'openai',
        'azure': 'openai',  # Azure 使用 OpenAI 兼容模式
        'self-hosted': 'openai',  # 自托管使用 OpenAI 兼容协议
        'deepseek': 'deepseek',  # LazyLLM 原生支持
        'groq': 'openai',  # Groq 兼容 OpenAI API
        'mistral': 'openai',  # Mistral 兼容 OpenAI API
        # 以下供应商需要特殊处理（不兼容 OpenAI API）
        # 'anthropic': 需要单独处理
        # 'cohere': 需要单独处理  
        # 'google': 需要单独处理
    }
    
    # 检查是否是 LazyLLM 原生支持的供应商
    lazyllm_source = provider_map.get(provider_name)
    
    # 构建 base_url（用于 OpenAI 兼容模式）
    base_url = None
    if provider_name == 'azure':
        # Azure OpenAI 格式
        base_url = '{}/openai/deployments/{}/chat/completions?api-version=2023-07-01-preview'.format(
            server_url.rstrip('/'), azure_deployment
        )
    elif provider_name == 'self-hosted':
        base_url = server_url
    elif provider_name == 'groq':
        base_url = 'https://api.groq.com/openai/v1'
    elif provider_name == 'mistral':
        base_url = 'https://api.mistral.ai/v1'
    
    # 对于 LazyLLM 原生支持的供应商，直接创建 OnlineChatModule
    if lazyllm_source:
        try:
            kwargs = {
                'source': lazyllm_source,
                'model': model_name,
                'api_key': api_key,
                'stream': False,  # fish-ai 不使用流式输出
                'return_trace': False,
            }
            
            if base_url:
                kwargs['base_url'] = base_url
            
            chat_module = lazyllm.OnlineChatModule(**kwargs)
            get_logger().debug('Created LazyLLM OnlineChatModule: source={}, model={}'.format(
                lazyllm_source, model_name))
            return chat_module, 'lazyllm'
            
        except Exception as e:
            get_logger().error('Failed to create LazyLLM module: {}'.format(str(e)))
            raise
    
    # 对于 LazyLLM 不支持的供应商（anthropic, cohere, google），返回 None 表示需要单独处理
    get_logger().debug('Provider {} not natively supported by LazyLLM, using fallback'.format(
        provider_name))
    return None, 'fallback'


def get_response(messages):
    """
    Get response from LLM using LazyLLM where possible.
    
    优先使用 LazyLLM OnlineChatModule 统一接入支持的供应商。
    对于 LazyLLM 不支持的供应商（anthropic, cohere, google），使用原有实现。
    
    Args:
        messages: List of messages in OpenAI format
        
    Returns:
        Response text from LLM
        
    Raises:
        Exception: If provider call fails
    """
    if get_config('redact') != 'False':
        messages = redact(messages)

    start_time = time_ns()

    # 从配置读取参数
    provider_name = get_config('provider')
    model_name = get_config('model')
    
    # 支持两种 API Key 配置方式：
    # 1. 供应商专用：FISHAI_{PROVIDER}_API_KEY（推荐）
    # 2. 通用：FISHAI_API_KEY
    api_key = get_config('{}_api_key'.format(provider_name))
    if not api_key:
        api_key = get_config('api_key')
    
    server_url = get_config('server')
    azure_deployment = get_config('azure_deployment')
    custom_headers = get_custom_headers()
    
    # 模型默认值
    if not model_name:
        if provider_name == 'mistral':
            model_name = 'mistral-large-latest'
        elif provider_name == 'anthropic':
            model_name = 'claude-sonnet-4-6'
        elif provider_name == 'cohere':
            model_name = 'command-r-plus-08-2024'
        elif provider_name == 'groq':
            model_name = 'qwen/qwen3-32b'
        elif provider_name == 'google':
            model_name = 'gemini-2.5-flash-lite'
        else:
            model_name = 'gpt-4o'
    
    # 尝试使用 LazyLLM
    chat_module, mode = get_lazyllm_chat_module(
        provider_name=provider_name,
        model_name=model_name,
        api_key=api_key,
        server_url=server_url,
        azure_deployment=azure_deployment,
    )
    
    try:
        if mode == 'lazyllm':
            # 使用 LazyLLM OnlineChatModule
            # ⚠️ LazyLLM 期望字符串输入，不是 OpenAI 格式的消息列表
            # 提取最后一条用户消息
            user_message = messages[-1]['content'] if messages else ''
            response_text = chat_module(user_message)
            
        elif mode == 'fallback':
            # LazyLLM 不支持的供应商，使用原有实现
            # 这里保留原有代码，确保 anthropic/cohere/google 正常工作
            response_text = _get_response_fallback(
                messages, provider_name, model_name, api_key,
                server_url, azure_deployment, custom_headers
            )
        else:
            raise Exception('Unknown mode: {}'.format(mode))
            
    except Exception as e:
        get_logger().error('LLM provider call failed: {}'.format(str(e)))
        raise

    end_time = time_ns()
    get_logger().debug('Response received from backend: ' + repr(response_text))
    get_logger().debug('Processing time: ' +
                       str(round((end_time - start_time) / 1000000)) + ' ms.')
    return remove_thinking_tokens(response_text)


def _get_response_fallback(messages, provider_name, model_name, api_key,
                           server_url, azure_deployment, custom_headers):
    """
    Fallback implementation for providers not supported by LazyLLM.
    
    保留原有实现，确保 anthropic/cohere/google 正常工作。
    未来如果 LazyLLM 支持这些供应商，可以移除这个函数。
    """
    # 保留原有实现代码...
    # 为了简洁，这里省略，实际应该复制原来的 if-elif 逻辑
    # 但只针对 anthropic/cohere/google 三个供应商
    
    if provider_name == 'anthropic':
        from anthropic import Anthropic
        system_messages, user_messages = get_messages_for_anthropic(messages)
        client = Anthropic(api_key=api_key, default_headers=custom_headers)
        params = {
            'model': model_name,
            'system': '\n'.join(system_messages),
            'messages': user_messages,
            'max_tokens': 4096
        }
        completions = client.messages.create(**params)
        return completions.content[0].text
    
    elif provider_name == 'cohere':
        from cohere import ClientV2
        cohere_kwargs = {'api_key': api_key}
        if custom_headers:
            from httpx import Client
            cohere_kwargs['httpx_client'] = Client(headers=custom_headers)
        client = ClientV2(**cohere_kwargs)
        params = {
            'model': model_name,
            'messages': messages,
        }
        completions = client.chat(**params)
        return completions.message.content[0].text
    
    elif provider_name == 'google':
        from google import genai
        from google.genai import types
        google_kwargs = {'api_key': api_key}
        if custom_headers:
            from google.genai.types import HttpOptions
            google_kwargs['http_options'] = HttpOptions(headers=custom_headers)
        client = genai.Client(**google_kwargs)
        
        model_info = client.models.get(model=model_name)
        if not getattr(model_info, 'thinking', False):
            thinking_config = types.GenerateContentConfig()
        elif 'gemini-2.5' in model_name:
            thinking_config = types.ThinkingConfig(thinking_budget=1024)
        elif 'gemini-3' in model_name:
            thinking_config = types.ThinkingConfig(thinking_level='low')
        else:
            thinking_config = None
        
        response = client.models.generate_content(
            model=model_name,
            contents=get_messages_for_gemini(messages),
            config=types.GenerateContentConfig(thinking_config=thinking_config)
        ).text
        return response
    
    else:
        raise Exception('Fallback not implemented for provider: {}'.format(provider_name))


def remove_thinking_tokens(response):
    """
    Removes thinking tokens which may be present in the beginning of the
    response.

    Example with thinking tokens:

      <think>bar</think>foo -> foo

    :param response: The response from the backend.
    :return: The output without any thinking tokens.
    """
    if not response.strip().startswith('<think>'):
        return response.strip()

    import re
    match = re.search(r'<think>(.*?)</think>(.*)', response, re.DOTALL)
    if match:
        return match.group(2).strip()
    else:
        return response.strip()


def get_install_dir():
    if 'XDG_DATA_HOME' in environ:
        return expandvars('$XDG_DATA_HOME/fish-ai')
    else:
        return expanduser('~/.local/share/fish-ai')
