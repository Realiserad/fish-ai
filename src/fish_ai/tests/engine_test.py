# -*- coding: utf-8 -*-
"""
Unit tests for fish_ai.engine module with LazyLLM integration.

Test Coverage:
- LazyLLM mode: openai, deepseek, groq, mistral, azure, self-hosted
- Fallback mode: anthropic, cohere, google
- Special parameters: Groq reasoning, Gemini thinking
- Error handling
- Message format conversion
- Thinking token removal
"""

from unittest.mock import patch, MagicMock, Mock
import pytest
from fish_ai.engine import (
    get_commandline_history,
    get_lazyllm_chat_module,
    get_response,
    get_messages_for_anthropic,
    get_messages_for_gemini,
    remove_thinking_tokens,
)


class TestLazyLLMChatModule:
    """Test get_lazyllm_chat_module function."""

    @patch('fish_ai.engine.lazyllm.OnlineChatModule')
    def test_openai_module(self, mock_online_chat):
        """Test OpenAI module creation."""
        mock_module = MagicMock()
        mock_online_chat.return_value = mock_module

        result, mode = get_lazyllm_chat_module(
            provider_name='openai',
            model_name='gpt-4o',
            api_key='test-key'
        )

        mock_online_chat.assert_called_once_with(
            source='openai',
            model='gpt-4o',
            api_key='test-key',
            stream=False,
            return_trace=False,
        )
        assert mode == 'lazyllm'
        assert result == mock_module

    @patch('fish_ai.engine.lazyllm.OnlineChatModule')
    def test_deepseek_module(self, mock_online_chat):
        """Test DeepSeek module creation."""
        mock_module = MagicMock()
        mock_online_chat.return_value = mock_module

        result, mode = get_lazyllm_chat_module(
            provider_name='deepseek',
            model_name='deepseek-chat',
            api_key='test-key'
        )

        call_args = mock_online_chat.call_args
        assert call_args.kwargs['source'] == 'deepseek'
        assert call_args.kwargs['model'] == 'deepseek-chat'
        assert call_args.kwargs['api_key'] == 'test-key'
        assert mode == 'lazyllm'

    @patch('fish_ai.engine.lazyllm.OnlineChatModule')
    def test_azure_module(self, mock_online_chat):
        """Test Azure OpenAI module creation."""
        mock_module = MagicMock()
        mock_online_chat.return_value = mock_module

        result, mode = get_lazyllm_chat_module(
            provider_name='azure',
            model_name='gpt-4',
            api_key='test-key',
            server_url='https://test.openai.azure.com',
            azure_deployment='my-deployment'
        )

        call_args = mock_online_chat.call_args
        assert call_args.kwargs['source'] == 'openai'
        assert 'azure' in call_args.kwargs['base_url']
        assert 'my-deployment' in call_args.kwargs['base_url']
        assert mode == 'lazyllm'

    @patch('fish_ai.engine.lazyllm.OnlineChatModule')
    def test_self_hosted_module(self, mock_online_chat):
        """Test self-hosted module creation."""
        mock_module = MagicMock()
        mock_online_chat.return_value = mock_module

        result, mode = get_lazyllm_chat_module(
            provider_name='self-hosted',
            model_name='local-model',
            api_key='dummy',
            server_url='http://localhost:8000/v1'
        )

        call_args = mock_online_chat.call_args
        assert call_args.kwargs['source'] == 'openai'
        assert call_args.kwargs['base_url'] == 'http://localhost:8000/v1'
        assert mode == 'lazyllm'

    @patch('fish_ai.engine.lazyllm.OnlineChatModule')
    def test_groq_module(self, mock_online_chat):
        """Test Groq module creation."""
        mock_module = MagicMock()
        mock_online_chat.return_value = mock_module

        result, mode = get_lazyllm_chat_module(
            provider_name='groq',
            model_name='qwen/qwen3-32b',
            api_key='test-key'
        )

        call_args = mock_online_chat.call_args
        assert call_args.kwargs['source'] == 'openai'
        assert 'groq.com' in call_args.kwargs['base_url']
        assert mode == 'lazyllm'

    @patch('fish_ai.engine.lazyllm.OnlineChatModule')
    def test_mistral_module(self, mock_online_chat):
        """Test Mistral module creation."""
        mock_module = MagicMock()
        mock_online_chat.return_value = mock_module

        result, mode = get_lazyllm_chat_module(
            provider_name='mistral',
            model_name='mistral-large',
            api_key='test-key'
        )

        call_args = mock_online_chat.call_args
        assert call_args.kwargs['source'] == 'openai'
        assert 'mistral.ai' in call_args.kwargs['base_url']
        assert mode == 'lazyllm'

    def test_anthropic_fallback(self):
        """Test Anthropic returns fallback mode (not supported by LazyLLM)."""
        result, mode = get_lazyllm_chat_module(
            provider_name='anthropic',
            model_name='claude-sonnet-4-6',
            api_key='test-key'
        )

        assert mode == 'fallback'
        assert result is None

    def test_cohere_fallback(self):
        """Test Cohere returns fallback mode (not supported by LazyLLM)."""
        result, mode = get_lazyllm_chat_module(
            provider_name='cohere',
            model_name='command-r-plus',
            api_key='test-key'
        )

        assert mode == 'fallback'
        assert result is None

    def test_google_fallback(self):
        """Test Google returns fallback mode (not supported by LazyLLM)."""
        result, mode = get_lazyllm_chat_module(
            provider_name='google',
            model_name='gemini-2.5',
            api_key='test-key'
        )

        assert mode == 'fallback'
        assert result is None


class TestGetResponseLazyLLM:
    """Test get_response function with LazyLLM mode."""

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_get_response_deepseek(self, mock_headers, mock_config, mock_module):
        """Test get_response with DeepSeek (LazyLLM mode)."""
        # Mock config
        mock_config.side_effect = lambda key: {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'api_key': 'test-key',
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None

        # Mock LazyLLM module (expects string input, returns string)
        mock_chat_module = MagicMock()
        mock_chat_module.return_value = '这是 DeepSeek 的回答'
        mock_module.return_value = (mock_chat_module, 'lazyllm')

        messages = [
            {'role': 'system', 'content': 'You are helpful'},
            {'role': 'user', 'content': 'Hello'}
        ]
        result = get_response(messages)

        assert result == '这是 DeepSeek 的回答'
        mock_module.assert_called_once()
        # Verify LazyLLM module is called with string, not message list
        mock_chat_module.assert_called_once()
        call_args = mock_chat_module.call_args
        assert isinstance(call_args[0][0], str)  # First arg should be string
        assert call_args[0][0] == 'Hello'  # Should be last user message

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_get_response_groq_reasoning(self, mock_headers, mock_config, mock_module):
        """Test get_response with Groq reasoning model."""
        # Mock config
        mock_config.side_effect = lambda key: {
            'provider': 'groq',
            'model': 'qwen/qwen3-32b',
            'api_key': 'test-key',
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None

        # Mock LazyLLM module
        mock_chat_module = MagicMock()
        mock_chat_module.return_value = 'Answer without thinking tokens'
        mock_module.return_value = (mock_chat_module, 'lazyllm')

        messages = [{'role': 'user', 'content': 'Solve this'}]
        result = get_response(messages)

        assert result == 'Answer without thinking tokens'
        # Groq reasoning models should have special handling
        # (Note: LazyLLM may handle this internally)


class TestGetResponseFallback:
    """Test get_response function with Fallback mode."""

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_get_response_anthropic(self, mock_headers, mock_config, mock_module):
        """Test get_response with Anthropic (Fallback mode)."""
        # Mock config
        mock_config.side_effect = lambda key: {
            'provider': 'anthropic',
            'model': 'claude-sonnet-4-6',
            'api_key': 'test-key',
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None

        # Mock fallback returns None to trigger fallback mode
        mock_module.return_value = (None, 'fallback')

        # Mock Anthropic client (imported inside function, patch the import)
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            mock_completion.content = [MagicMock()]
            mock_completion.content[0].text = 'Claude 的回答'
            mock_client.messages.create.return_value = mock_completion
            mock_anthropic.return_value = mock_client

            messages = [
                {'role': 'system', 'content': 'You are helpful'},
                {'role': 'user', 'content': 'Hello'}
            ]
            result = get_response(messages)

            assert result == 'Claude 的回答'
            mock_anthropic.assert_called_once()
            mock_client.messages.create.assert_called_once()

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_get_response_google(self, mock_headers, mock_config, mock_module):
        """Test get_response with Google Gemini (Fallback mode)."""
        # Mock config
        mock_config.side_effect = lambda key: {
            'provider': 'google',
            'model': 'gemini-2.5-flash-lite',
            'api_key': 'test-key',
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None

        # Mock fallback returns None to trigger fallback mode
        mock_module.return_value = (None, 'fallback')

        # Mock Google GenAI client
        with patch('fish_ai.engine.genai') as mock_genai:
            mock_client = MagicMock()
            mock_model_info = MagicMock()
            mock_model_info.thinking = False
            mock_client.models.get.return_value = mock_model_info

            mock_response = MagicMock()
            mock_response.text = 'Gemini 的回答'
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            messages = [{'role': 'user', 'content': 'Hello'}]
            result = get_response(messages)

            assert result == 'Gemini 的回答'
            mock_genai.Client.assert_called_once()
            mock_client.models.generate_content.assert_called_once()


class TestMessageConversion:
    """Test message format conversion functions."""

    def test_get_messages_for_anthropic(self):
        """Test conversion to Anthropic format."""
        messages = [
            {'role': 'system', 'content': 'You are helpful'},
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
        ]

        system_messages, user_messages = get_messages_for_anthropic(messages)

        assert system_messages == ['You are helpful']
        assert len(user_messages) == 2
        assert user_messages[0]['role'] == 'user'
        assert user_messages[1]['role'] == 'assistant'

    def test_get_messages_for_gemini(self):
        """Test conversion to Gemini format."""
        messages = [
            {'role': 'system', 'content': 'You are helpful'},
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
        ]

        result = get_messages_for_gemini(messages)

        assert len(result) == 2
        assert result[0]['role'] == 'user'
        assert result[0]['parts'][0]['text'] == 'You are helpful'
        assert result[0]['parts'][1]['text'] == 'Hello'
        assert result[1]['role'] == 'model'
        assert result[1]['parts'][0]['text'] == 'Hi there!'

    def test_get_messages_for_gemini_empty(self):
        """Test conversion with empty messages."""
        result = get_messages_for_gemini([])
        assert result == []

    def test_get_messages_for_anthropic_no_system(self):
        """Test Anthropic conversion without system message."""
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi!'},
        ]

        system_messages, user_messages = get_messages_for_anthropic(messages)

        assert system_messages == []
        assert len(user_messages) == 2


class TestThinkingTokens:
    """Test thinking token removal."""

    def test_remove_thinking_tokens_with_tokens(self):
        """Test removal of thinking tokens."""
        response = '<think>Let me think</think>This is the answer'
        result = remove_thinking_tokens(response)
        assert result == 'This is the answer'

    def test_remove_thinking_tokens_without_tokens(self):
        """Test response without thinking tokens."""
        response = 'This is the answer'
        result = remove_thinking_tokens(response)
        assert result == 'This is the answer'

    def test_remove_thinking_tokens_multiline(self):
        """Test removal of multi-line thinking tokens."""
        response = '''<think>
Let me think step by step
1. First...
2. Second...
</think>The final answer'''
        result = remove_thinking_tokens(response)
        assert result == 'The final answer'

    def test_remove_thinking_tokens_whitespace(self):
        """Test removal with leading/trailing whitespace."""
        response = '  <think>thinking</think>answer  '
        result = remove_thinking_tokens(response)
        assert result == 'answer'

    def test_remove_thinking_tokens_empty(self):
        """Test with empty response."""
        result = remove_thinking_tokens('')
        assert result == ''

    def test_remove_thinking_tokens_only_thinking(self):
        """Test with only thinking tokens."""
        response = '<think>thinking</think>'
        result = remove_thinking_tokens(response)
        assert result == ''


class TestCommandlineHistory:
    """Test commandline history function."""

    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_logger')
    def test_get_commandline_history_disabled(self, mock_get_logger, mock_get_config):
        """Test when history is disabled."""
        mock_get_config.return_value = '0'
        result = get_commandline_history('command', 0)
        assert result == 'No commandline history available.'
        mock_get_logger.assert_called_once()


class TestAPIKeyConfiguration:
    """Test API key configuration (FISHAI_API_KEY vs FISHAI_{PROVIDER}_API_KEY)."""

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_provider_specific_api_key(self, mock_headers, mock_config, mock_module):
        """Test provider-specific API key takes precedence."""
        # Mock config returns provider-specific key first, then None
        mock_config.side_effect = lambda key: {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'deepseek_api_key': 'sk-deepseek-specific',  # Provider-specific
            'api_key': 'sk-generic',  # Generic (should not be used)
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None
        mock_chat_module = MagicMock()
        mock_chat_module.return_value = 'Response'
        mock_module.return_value = (mock_chat_module, 'lazyllm')

        messages = [{'role': 'user', 'content': 'Test'}]
        result = get_response(messages)

        # Verify get_lazyllm_chat_module was called with provider-specific key
        call_args = mock_module.call_args
        assert call_args.kwargs['api_key'] == 'sk-deepseek-specific'

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_generic_api_key_fallback(self, mock_headers, mock_config, mock_module):
        """Test generic API key is used when provider-specific is not set."""
        # Mock config returns None for provider-specific, then generic key
        mock_config.side_effect = lambda key: {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'deepseek_api_key': None,  # No provider-specific key
            'api_key': 'sk-generic',  # Generic key
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None
        mock_chat_module = MagicMock()
        mock_chat_module.return_value = 'Response'
        mock_module.return_value = (mock_chat_module, 'lazyllm')

        messages = [{'role': 'user', 'content': 'Test'}]
        result = get_response(messages)

        # Verify get_lazyllm_chat_module was called with generic key
        call_args = mock_module.call_args
        assert call_args.kwargs['api_key'] == 'sk-generic'


class TestErrorHandling:
    """Test error handling."""

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_lazyllm_module_creation_error(self, mock_headers, mock_config, mock_module):
        """Test error when LazyLLM module creation fails."""
        mock_config.side_effect = lambda key: {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'api_key': 'invalid-key',
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None
        mock_module.side_effect = Exception('Invalid API key')

        messages = [{'role': 'user', 'content': 'Test'}]

        with pytest.raises(Exception) as exc_info:
            get_response(messages)

        assert 'Invalid API key' in str(exc_info.value)

    @patch('fish_ai.engine.get_lazyllm_chat_module')
    @patch('fish_ai.engine.get_config')
    @patch('fish_ai.engine.get_custom_headers')
    def test_lazyllm_call_error(self, mock_headers, mock_config, mock_module):
        """Test error when LazyLLM call fails."""
        mock_config.side_effect = lambda key: {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'api_key': 'test-key',
            'server': None,
            'azure_deployment': None,
            'extra_body': None,
            'redact': 'False',
        }.get(key)

        mock_headers.return_value = None

        mock_chat_module = MagicMock()
        mock_chat_module.side_effect = Exception('API rate limit')
        mock_module.return_value = (mock_chat_module, 'lazyllm')

        messages = [{'role': 'user', 'content': 'Test'}]

        with pytest.raises(Exception) as exc_info:
            get_response(messages)

        assert 'API rate limit' in str(exc_info.value)
