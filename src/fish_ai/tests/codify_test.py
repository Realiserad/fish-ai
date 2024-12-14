# -*- coding: utf-8 -*-

from unittest.mock import patch

from fish_ai.codify import codify
import logging


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


@patch('fish_ai.engine.get_args', lambda: ['# print /tmp/hello.txt'])
@patch('fish_ai.engine.get_response')
@patch('fish_ai.engine.get_logger', lambda: logging.getLogger('dummy'))
def test_codify_with_file(mock_get_response, fs):
    fs.create_file('/tmp/hello.txt', contents='what is cooking?')
    codify()
    assert 'what is cooking?' in mock_get_response \
        .call_args.kwargs['messages'][-1]['content']
