# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch, MagicMock
from fish_ai.engine import *

def test_get_args():
    with patch('sys.argv', ['script.py', 'arg1', 'arg2']):
        assert get_args() == ['arg1', 'arg2']

def test_get_logger_with_syslog_linux():
    with patch('fish_ai.engine.path.exists', side_effect=[True, False]), \
         patch('fish_ai.engine.SysLogHandler') as mock_syslog_handler:
        logger = get_logger()
        mock_syslog_handler.assert_called_once_with(address='/dev/log')
        assert mock_syslog_handler.return_value in logger.handlers

def test_get_logger_with_syslog_macos():
    with patch('fish_ai.engine.path.exists', side_effect=[False, True]), \
         patch('fish_ai.engine.SysLogHandler') as mock_syslog_handler:
        logger = get_logger()
        mock_syslog_handler.assert_called_once_with(address='/var/run/syslog')
        assert mock_syslog_handler.return_value in logger.handlers

def test_get_logger_with_file_handler():
    with patch('fish_ai.engine.get_config', return_value='/path/to/log'), \
         patch('fish_ai.engine.RotatingFileHandler') as mock_file_handler:
        logger = get_logger()
        mock_file_handler.assert_called_once_with('/path/to/log', backupCount=0, maxBytes=1048576)
        assert mock_file_handler.return_value in logger.handlers

def test_get_logger_with_debug_level():
    with patch('fish_ai.engine.get_config', return_value='True'):
        logger = get_logger()
        assert logger.level == logging.DEBUG

def test_get_os_linux():
    with patch('platform.system', return_value='Linux'), \
         patch('fish_ai.engine.isfile', return_value=True), \
         patch('builtins.open', MagicMock(return_value=iter(['PRETTY_NAME="Ubuntu 20.04"']))):
        assert get_os() == 'Ubuntu 20.04'

def test_get_os_linux_without_os_release():
    with patch('platform.system', return_value='Linux'), \
         patch('fish_ai.engine.isfile', return_value=False):
        assert get_os() == 'Linux'

def test_get_os_macos():
    with patch('platform.system', return_value='Darwin'), \
         patch('platform.mac_ver', return_value=('10.15.7', ('', '', ''), '')):
        assert get_os() == 'macOS 10.15.7'

def test_get_os_unknown():
    with patch('platform.system', return_value='Unknown'):
        assert get_os() == 'Unknown'

def test_get_manpage_success():
    with patch('subprocess.run', return_value=MagicMock(returncode=0, stdout=b'manpage content')):
        assert get_manpage('command') == 'manpage content'

def test_get_manpage_failure():
    with patch('subprocess.run', return_value=MagicMock(returncode=1)):
        assert get_manpage('command') == 'No manpage available.'

def test_get_manpage_exception():
    with patch('subprocess.run', side_effect=Exception('error')), \
         patch('fish_ai.engine.get_logger') as mock_logger:
        assert get_manpage('command') == 'No manpage available.'
        mock_logger.return_value.debug.assert_called_once_with(
            'Failed to get manpage for command "command". Reason: error'
        )

def test_get_commandline_history():
    with patch('fish_ai.engine.get_config', return_value='10'), \
         patch('subprocess.check_output', return_value=b'history output'):
        assert get_commandline_history('command') == 'history output'

    with patch('fish_ai.engine.get_config', return_value='10'), \
         patch('subprocess.check_output', return_value=b''):
        assert get_commandline_history('command') == 'No commandline history available.'

def test_get_system_prompt():
    with patch('fish_ai.engine.get_os', return_value='macOS 10.15.7'):
        prompt = get_system_prompt()
        assert prompt['role'] == 'system'
        assert 'macOS 10.15.7' in prompt['content']

def test_get_config_with_valid_key():
    with patch('fish_ai.engine.config', MagicMock(
        has_section=MagicMock(return_value=True),
        get=MagicMock(side_effect=['test_section', 'value'])
    )):
        assert get_config('key') == 'value'

def test_get_config_with_invalid_key():
    with patch('fish_ai.engine.config', MagicMock(
        has_section=MagicMock(return_value=True),
        get=MagicMock(side_effect=['test_section', None])
    )):
        assert get_config('invalid_key') is None

def test_get_config_without_configuration():
    with patch('fish_ai.engine.config', MagicMock(has_section=MagicMock(return_value=False))):
        assert get_config('key') is None

def test_get_openai_client_azure():
    with patch('fish_ai.engine.get_config', side_effect=['azure', 'endpoint', 'api_key', 'deployment']):
        client = get_openai_client()
        assert isinstance(client, AzureOpenAI)
        assert client.azure_endpoint == 'endpoint'
        assert client.api_version == '2023-07-01-preview'
        assert client.api_key == 'api_key'
        assert client.azure_deployment == 'deployment'

def test_get_openai_client_self_hosted():
    with patch('fish_ai.engine.get_config', side_effect=['self-hosted', 'server', 'api_key']):
        client = get_openai_client()
        assert isinstance(client, OpenAI)
        assert client.base_url == 'server'
        assert client.api_key == 'api_key'

def test_get_openai_client_openai():
    with patch('fish_ai.engine.get_config', side_effect=['openai', 'api_key', 'organization']):
        client = get_openai_client()
        assert isinstance(client, OpenAI)
        assert client.api_key == 'api_key'
        assert client.organization == 'organization'

def test_get_openai_client_unknown_provider():
    with patch('fish_ai.engine.get_config', return_value='unknown'):
        with pytest.raises(Exception, match='Unknown provider "unknown".'):
            get_openai_client()

def test_create_message_history():
    messages = [
        {'role': 'system', 'content': 'System message 1'},
        {'role': 'system', 'content': 'System message 2'},
        {'role': 'user', 'content': 'User message 1'},
        {'role': 'assistant', 'content': 'Assistant message 1'},
        {'role': 'user', 'content': 'User message 2'},
    ]
    history = create_message_history(messages)
    assert history == [
        {'role': 'user', 'parts': ['System message 1', 'System message 2', 'User message 1']},
        {'role': 'model', 'parts': ['Assistant message 1']},
        {'role': 'user', 'parts': ['User message 2']},
    ]

def test_get_response_google():
    messages = [{'role': 'user', 'content': 'Test message'}]
    with patch('fish_ai.engine.get_config', side_effect=['google', 'api_key', 'model', '0.2']), \
         patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model, \
         patch('fish_ai.engine.create_message_history', return_value=[]), \
         patch('fish_ai.engine.get_logger') as mock_logger:
        mock_model.return_value.start_chat.return_value.send_message.return_value.text = 'Test response'
        response = get_response(messages)
        assert response == 'Test response'
        mock_logger.return_value.debug.assert_any_call('Response received from backend: Test response')

def test_get_response_openai():
    messages = [{'role': 'user', 'content': 'Test message'}]
    with patch('fish_ai.engine.get_config', side_effect=['openai', 'model', '0.2']), \
         patch('fish_ai.engine.get_openai_client') as mock_client, \
         patch('fish_ai.engine.get_logger') as mock_logger:
        mock_client.return_value.chat.completions.create.return_value.choices[0].message.content = 'Test response'
        response = get_response(messages)
        assert response == 'Test response'
        mock_logger.return_value.debug.assert_any_call('Response received from backend: Test response')

def test_get_response_error():
    messages = [{'role': 'user', 'content': 'Test message'}]
    with patch('fish_ai.engine.get_config', return_value='openai'), \
         patch('fish_ai.engine.get_openai_client') as mock_client:
        mock_client.return_value.chat.completions.create.return_value.choices[0].message.content = 'error: Test error'
        with pytest.raises(Exception, match='Test error'):
            get_response(messages)
