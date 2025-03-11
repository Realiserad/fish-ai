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
