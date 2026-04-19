# -*- coding: utf-8 -*-

from unittest.mock import patch, MagicMock
from fish_ai.engine import get_commandline_history, get_response


@patch("fish_ai.engine.get_config")
@patch("fish_ai.engine.get_logger")
def test_get_commandline_history_disabled(mock_get_logger, mock_get_config):
    mock_get_config.return_value = "0"
    assert get_commandline_history("command", 0) == "No commandline history available."
    mock_get_logger.assert_called_once()


@patch("fish_ai.engine.get_config")
def test_bedrock_happy_path(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "us-west-2",
            "model": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "redact": "False",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    mock_bedrock_client = MagicMock()
    mock_bedrock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": "echo hello"}],
            }
        }
    }

    with patch(
        "fish_ai.engine.get_bedrock_client", return_value=mock_bedrock_client
    ) as mock_get_client:
        response = get_response(
            [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "hello"},
            ]
        )
        mock_get_client.assert_called_once()
        mock_bedrock_client.converse.assert_called_once()
        call_kwargs = mock_bedrock_client.converse.call_args[1]
        assert call_kwargs["modelId"] == "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        assert call_kwargs["system"] == [{"text": "You are helpful."}]
        assert call_kwargs["messages"] == [
            {"role": "user", "content": [{"text": "hello"}]}
        ]
        assert response == "echo hello"


@patch("fish_ai.engine.get_config")
def test_bedrock_default_model(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "us-west-2",
            "redact": "False",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    mock_bedrock_client = MagicMock()
    mock_bedrock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": "echo hello"}],
            }
        }
    }

    with patch("fish_ai.engine.get_bedrock_client", return_value=mock_bedrock_client):
        get_response(
            [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "hello"},
            ]
        )
        call_kwargs = mock_bedrock_client.converse.call_args[1]
        assert call_kwargs["modelId"] == "us.anthropic.claude-haiku-4-5-20251001-v1:0"


@patch("fish_ai.engine.get_config")
def test_bedrock_client_uses_profile(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "us-west-2",
            "aws_profile": "my-profile",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    mock_session = MagicMock()

    with patch("boto3.Session", return_value=mock_session) as mock_boto3_session:
        from fish_ai.engine import get_bedrock_client

        get_bedrock_client()
        mock_boto3_session.assert_called_once_with(
            profile_name="my-profile",
            region_name="us-west-2",
        )
        mock_session.client.assert_called_once_with("bedrock-runtime")


@patch("fish_ai.engine.get_config")
def test_bedrock_client_default_credentials(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "us-east-1",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    mock_session = MagicMock()

    with patch("boto3.Session", return_value=mock_session) as mock_boto3_session:
        from fish_ai.engine import get_bedrock_client

        get_bedrock_client()
        mock_boto3_session.assert_called_once_with(
            region_name="us-east-1",
        )
        mock_session.client.assert_called_once_with("bedrock-runtime")


@patch("fish_ai.engine.get_config")
def test_bedrock_default_region(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    mock_session = MagicMock()

    with patch("boto3.Session", return_value=mock_session) as mock_boto3_session:
        from fish_ai.engine import get_bedrock_client

        get_bedrock_client()
        mock_boto3_session.assert_called_once_with(
            region_name="us-east-1",
        )


@patch("fish_ai.engine.get_config")
def test_bedrock_messages_conversion(mock_get_config):
    """Test that OpenAI-format messages are correctly converted to Bedrock
    Converse format with system messages extracted separately."""
    mock_get_config.return_value = None

    from fish_ai.engine import get_messages_for_bedrock

    messages = [
        {"role": "system", "content": "You are a shell assistant."},
        {"role": "user", "content": "How do I list files?"},
        {"role": "assistant", "content": "Use ls command."},
        {"role": "user", "content": "What about hidden files?"},
    ]

    system_prompts, converse_messages = get_messages_for_bedrock(messages)

    assert system_prompts == [{"text": "You are a shell assistant."}]
    assert converse_messages == [
        {"role": "user", "content": [{"text": "How do I list files?"}]},
        {"role": "assistant", "content": [{"text": "Use ls command."}]},
        {"role": "user", "content": [{"text": "What about hidden files?"}]},
    ]


@patch("fish_ai.engine.get_config")
def test_bedrock_thinking_tokens_removed(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "us-west-2",
            "model": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "redact": "False",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    mock_bedrock_client = MagicMock()
    mock_bedrock_client.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": "<think>reasoning</think>echo hello"}],
            }
        }
    }

    with patch("fish_ai.engine.get_bedrock_client", return_value=mock_bedrock_client):
        response = get_response(
            [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "hello"},
            ]
        )
        assert response == "echo hello"
