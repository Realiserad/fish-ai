# -*- coding: utf-8 -*-

from unittest.mock import patch, MagicMock
from fish_ai.engine import get_commandline_history, get_response


@patch("fish_ai.engine.get_config")
@patch("fish_ai.engine.get_logger")
def test_get_commandline_history_disabled(mock_get_logger, mock_get_config):
    mock_get_config.return_value = "0"
    assert get_commandline_history("command", 0) == "No commandline history available."
    mock_get_logger.assert_called_once()


# ── Converse API (default) ──────────────────────────────────────────────


@patch("fish_ai.engine.get_config")
def test_bedrock_converse_happy_path(mock_get_config):
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
def test_bedrock_converse_default_model(mock_get_config):
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
def test_bedrock_converse_is_default_api(mock_get_config):
    """When bedrock_api is not set, converse should be used."""

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

    with patch(
        "fish_ai.engine.get_bedrock_client", return_value=mock_bedrock_client
    ) as mock_get_client:
        get_response(
            [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "hello"},
            ]
        )
        mock_get_client.assert_called_once()
        mock_bedrock_client.converse.assert_called_once()


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
def test_bedrock_converse_thinking_tokens_removed(mock_get_config):
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


# ── Mantle gateway ──────────────────────────────────────────────────────


@patch("fish_ai.engine.get_config")
def test_bedrock_mantle_happy_path(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "bedrock_api": "mantle",
            "aws_region": "us-west-2",
            "api_key": "test-api-key",
            "model": "anthropic.claude-haiku-4-5-20251001-v1:0",
            "redact": "False",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    mock_completions = MagicMock()
    mock_completions.choices = [MagicMock(message=MagicMock(content="echo hello"))]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completions

    with patch(
        "fish_ai.engine.get_openai_client", return_value=mock_client
    ) as mock_get_client:
        response = get_response(
            [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "hello"},
            ]
        )
        mock_get_client.assert_called_once()
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "anthropic.claude-haiku-4-5-20251001-v1:0"
        assert response == "echo hello"


@patch("fish_ai.engine.get_config")
def test_bedrock_mantle_constructs_url(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "eu-west-1",
            "api_key": "test-key",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    with patch("openai.OpenAI") as mock_openai_cls:
        from fish_ai.engine import get_openai_client

        get_openai_client()
        mock_openai_cls.assert_called_once_with(
            base_url="https://bedrock-mantle.eu-west-1.api.aws/v1",
            api_key="test-key",
            default_headers=None,
        )


@patch("fish_ai.engine.get_config")
def test_bedrock_mantle_auto_token_when_no_api_key(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "us-west-2",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    import sys

    mock_token_module = MagicMock()
    mock_token_module.provide_token.return_value = "auto-generated-token"
    with patch.dict(sys.modules, {"aws_bedrock_token_generator": mock_token_module}):
        with patch("openai.OpenAI") as mock_openai_cls:
            from fish_ai.engine import get_openai_client

            get_openai_client()
            mock_token_module.provide_token.assert_called_once_with(region="us-west-2")
            mock_openai_cls.assert_called_once_with(
                base_url="https://bedrock-mantle.us-west-2.api.aws/v1",
                api_key="auto-generated-token",
                default_headers=None,
            )


@patch("fish_ai.engine.get_config")
def test_bedrock_mantle_uses_aws_profile_for_token(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "aws_region": "us-west-2",
            "aws_profile": "my-profile",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    import sys

    mock_credentials = MagicMock()
    mock_session = MagicMock()
    mock_session.get_credentials.return_value = mock_credentials

    mock_token_generator = MagicMock()
    mock_token_generator.get_token.return_value = "profile-token"

    mock_token_module = MagicMock()
    mock_token_module.BedrockTokenGenerator.return_value = mock_token_generator

    mock_botocore_module = MagicMock()
    mock_botocore_module.Session.return_value = mock_session

    with patch.dict(
        sys.modules,
        {
            "aws_bedrock_token_generator": mock_token_module,
            "botocore.session": mock_botocore_module,
            "botocore": MagicMock(),
        },
    ):
        with patch("openai.OpenAI") as mock_openai_cls:
            from fish_ai.engine import get_openai_client

            get_openai_client()
            mock_botocore_module.Session.assert_called_once_with(profile="my-profile")
            mock_session.get_credentials.assert_called_once()
            mock_token_generator.get_token.assert_called_once_with(
                credentials=mock_credentials,
                region="us-west-2",
            )
            mock_openai_cls.assert_called_once_with(
                base_url="https://bedrock-mantle.us-west-2.api.aws/v1",
                api_key="profile-token",
                default_headers=None,
            )


# ── Invalid bedrock_api ─────────────────────────────────────────────────


@patch("fish_ai.engine.get_config")
def test_bedrock_invalid_api_raises(mock_get_config):
    def config_side_effect(key):
        config = {
            "provider": "bedrock",
            "bedrock_api": "invalid",
            "redact": "False",
        }
        return config.get(key)

    mock_get_config.side_effect = config_side_effect

    import pytest

    with pytest.raises(Exception, match='Unknown bedrock_api "invalid"'):
        get_response(
            [
                {"role": "user", "content": "hello"},
            ]
        )
