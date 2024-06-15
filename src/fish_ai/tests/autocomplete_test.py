# -*- coding: utf-8 -*-

from unittest.mock import patch

from fish_ai.autocomplete import autocomplete


@patch('fish_ai.engine.get_args', lambda: ['echo hello', 10])
@patch('fish_ai.engine.get_config', lambda key: {
    'completions': '1'
}.get(key))
@patch('fish_ai.autocomplete.iterfzf',
       lambda iterable, **kwargs: 'echo hello world')
def test_successful_autocomplete(capsys):
    autocomplete()
    assert capsys.readouterr().out == 'echo hello world'
    assert capsys.readouterr().err == ''


@patch('fish_ai.engine.get_args', lambda: ['echo hello', 10])
@patch('fish_ai.engine.get_config', lambda key: {
    'completions': '1'
}.get(key))
@patch('fish_ai.engine.get_response',
       side_effect=Exception('crystal ball failed'))
@patch('builtins.print')
def test_unsuccessful_autocomplete(mock_print, _, caplog):
    autocomplete()
    mock_print.assert_called_with('echo hello', end='')
    assert 'crystal ball failed' in caplog.text
