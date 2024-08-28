# -*- coding: utf-8 -*-

from unittest.mock import patch
from fish_ai.engine import get_commandline_history


@patch('fish_ai.engine.get_config')
@patch('fish_ai.engine.get_logger')
def test_get_commandline_history_disabled(mock_get_logger, mock_get_config):
    mock_get_config.return_value = '0'
    assert get_commandline_history('command', 0) == \
        'No commandline history available.'
    mock_get_logger.assert_called_once()


@patch('fish_ai.engine.get_config')
@patch('fish_ai.engine.subprocess')
def test_get_commandline_history_return_2(mock_subprocess, mock_get_config):
    mock_get_config.return_value = '2'
    mock_subprocess.Popen.return_value.stdout.readline.side_effect = [
        b'docker ps | grep apache1\n',
        b'docker ps | grep apache2\n',
        b'docker ps | grep nginx\n',
        b'docker exec -it apache1 /bin/bash\n'
    ]
    # docker ps | grep█
    result = get_commandline_history('docker ps | grep', 16)
    assert result == 'docker ps | grep apache1\ndocker ps | grep apache2'
