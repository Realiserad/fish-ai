# -*- coding: utf-8 -*-

from unittest.mock import patch

from fish_ai.fix import fix
from subprocess import CalledProcessError


@patch('fish_ai.engine.get_args', lambda: ['foo'])
@patch('subprocess.check_output',
       side_effect=CalledProcessError(
           output=b'permission denied',
           returncode=1,
           cmd=['foo']))
@patch('fish_ai.engine.get_response')
def test_successful_fix(mock_get_response, _, capsys):
    mock_get_response.return_value = 'sudo foo'
    fix()
    assert 'permission denied' in mock_get_response \
        .call_args.kwargs['messages'][-1]['content']
    assert capsys.readouterr().out == 'sudo foo'
    assert capsys.readouterr().err == ''
