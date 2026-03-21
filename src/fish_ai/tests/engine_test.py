# -*- coding: utf-8 -*-

from unittest.mock import patch, MagicMock
from fish_ai.engine import get_commandline_history, get_response


@patch('fish_ai.engine.get_config')
@patch('fish_ai.engine.get_logger')
def test_get_commandline_history_disabled(mock_get_logger, mock_get_config):
    mock_get_config.return_value = '0'
    assert get_commandline_history('command', 0) == \
        'No commandline history available.'
    mock_get_logger.assert_called_once()


@patch('fish_ai.engine.get_config')
def test_bedrock_happy_path(mock_get_config):
    def config_side_effect(key):
        config = {
            'provider': 'bedrock',
            'aws_region': 'us-west-2',
            'api_key': 'test-api-key',
            'model': 'anthropic.claude-sonnet-4-6-20250514-v1:0',
            'redact': 'False',
        }
        return config.get(key)
    mock_get_config.side_effect = config_side_effect

    mock_completions = MagicMock()
    mock_completions.choices = [
        MagicMock(message=MagicMock(content='echo hello'))
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completions

    with patch('fish_ai.engine.get_openai_client',
               return_value=mock_client) as mock_get_client:
        response = get_response([
            {'role': 'system', 'content': 'You are helpful.'},
            {'role': 'user', 'content': 'hello'}
        ])
        mock_get_client.assert_called_once()
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == \
            'anthropic.claude-sonnet-4-6-20250514-v1:0'
        assert response == 'echo hello'


@patch('fish_ai.engine.get_config')
def test_bedrock_constructs_mantle_url(mock_get_config):
    def config_side_effect(key):
        config = {
            'provider': 'bedrock',
            'aws_region': 'eu-west-1',
            'api_key': 'test-key',
        }
        return config.get(key)
    mock_get_config.side_effect = config_side_effect

    with patch('openai.OpenAI') as mock_openai_cls:
        from fish_ai.engine import get_openai_client
        get_openai_client()
        mock_openai_cls.assert_called_once_with(
            base_url='https://bedrock-mantle.eu-west-1.api.aws/v1',
            api_key='test-key',
            default_headers=None,
        )


@patch('fish_ai.engine.get_config')
def test_bedrock_default_region(mock_get_config):
    def config_side_effect(key):
        config = {
            'provider': 'bedrock',
            'api_key': 'test-key',
        }
        return config.get(key)
    mock_get_config.side_effect = config_side_effect

    with patch('openai.OpenAI') as mock_openai_cls:
        from fish_ai.engine import get_openai_client
        get_openai_client()
        mock_openai_cls.assert_called_once_with(
            base_url='https://bedrock-mantle.us-east-1.api.aws/v1',
            api_key='test-key',
            default_headers=None,
        )


@patch('fish_ai.engine.get_config')
def test_bedrock_auto_token_when_no_api_key(mock_get_config):
    def config_side_effect(key):
        config = {
            'provider': 'bedrock',
            'aws_region': 'us-west-2',
        }
        return config.get(key)
    mock_get_config.side_effect = config_side_effect

    import sys
    mock_token_module = MagicMock()
    mock_token_module.provide_token.return_value = 'auto-generated-token'
    with patch.dict(sys.modules,
                    {'aws_bedrock_token_generator': mock_token_module}):
        with patch('openai.OpenAI') as mock_openai_cls:
            from fish_ai.engine import get_openai_client
            get_openai_client()
            mock_token_module.provide_token.assert_called_once_with(
                region='us-west-2')
            mock_openai_cls.assert_called_once_with(
                base_url='https://bedrock-mantle.us-west-2.api.aws/v1',
                api_key='auto-generated-token',
                default_headers=None,
            )
