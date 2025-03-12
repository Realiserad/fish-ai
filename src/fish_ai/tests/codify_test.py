# -*- coding: utf-8 -*-

from unittest.mock import patch

from fish_ai.codify import codify


@patch('fish_ai.engine.get_args', lambda: ['# hello'])
@patch('fish_ai.engine.get_response', lambda messages: 'echo hello')
def test_successful_codify(capsys):
    codify()
    assert capsys.readouterr().out == 'echo hello'
    assert capsys.readouterr().err == ''


@patch('fish_ai.engine.get_args', lambda: ['# hello'])
@patch('fish_ai.engine.get_response',
       side_effect=Exception('crystal ball failed'))
def test_unsuccessful_codify(_, caplog):
    codify()
    assert 'crystal ball failed' in caplog.text
