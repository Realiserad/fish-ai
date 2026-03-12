# -*- coding: utf-8 -*-

from unittest.mock import patch

from fish_ai.config import lookup_setting


@patch('fish_ai.config.get_config', lambda key: None)
@patch('sys.argv', ['lookup_setting'])
def test_lookup_setting_without_key(capsys):
    lookup_setting()
    assert capsys.readouterr().out == '\n'


@patch('fish_ai.config.get_config', lambda key: None)
@patch('sys.argv', ['lookup_setting', 'missing', 'fallback'])
def test_lookup_setting_uses_default(capsys):
    lookup_setting()
    assert capsys.readouterr().out == 'fallback\n'


@patch('fish_ai.config.get_config', lambda key: 'openai')
@patch('sys.argv', ['lookup_setting', 'provider'])
def test_lookup_setting_prints_value(capsys):
    lookup_setting()
    assert capsys.readouterr().out == 'openai\n'
