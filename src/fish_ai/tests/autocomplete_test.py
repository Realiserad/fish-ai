# -*- coding: utf-8 -*-

from unittest.mock import patch

from fish_ai.autocomplete import autocomplete, get_pipe


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


@patch('fish_ai.engine.get_args', lambda: ['echo hello', 4])
@patch('fish_ai.autocomplete.iterfzf',
       side_effect=Exception('crystal ball failed'))
def test_unsuccessful_autocomplete(_, caplog):
    autocomplete()
    assert 'crystal ball failed' in caplog.text


def test_get_pipe():
    assert get_pipe('echo hello') == ''
    assert get_pipe('echo hello | grep world') == 'echo hello'
    assert get_pipe('echo hello | grep world | wc -l') == \
        'echo hello | grep world'
    assert get_pipe('echo hello | grep world | wc -l |') == \
        'echo hello | grep world | wc -l'
    assert get_pipe('(echo hello | (echo world | wc -l') == \
        'echo world'
    assert get_pipe('echo "|"') == ''
    assert get_pipe('echo "hello | world" | wc -l') == \
        'echo "hello | world"'
    assert get_pipe("echo '|'") == ''
    assert get_pipe("echo 'hello | world' | wc -l") == "echo 'hello | world'"
    assert get_pipe('echo "hello ( world" | wc -l') == \
        'echo "hello ( world"'
    assert get_pipe('💩') == ''
    assert get_pipe('az vm list | jq ".[] =|') == 'az vm list'
    assert get_pipe('echo "\\"foo" | a') == 'echo "\\"foo"'
    assert get_pipe('echo \'{"foo":"bar}\' | jq .foo') == \
        'echo \'{"foo":"bar}\''

    assert get_pipe("""set sponsors (gh api graphql -f query='
        query {
            blah blah
        }' | jq -r .data)""") == \
        """gh api graphql -f query='
        query {
            blah blah
        }'"""
