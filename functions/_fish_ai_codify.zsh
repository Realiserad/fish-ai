#!/usr/bin/env zsh

function _fish_ai_codify {
    # Description: Turn a comment into a command using AI.
    local comment=$1
    local output

    if [[ $(~/.fish-ai/bin/lookup_setting "debug") == "True" ]]; then
        output=$(~/.fish-ai/bin/codify "$comment")
    else
        output=$(~/.fish-ai/bin/codify "$comment" 2> /dev/null)
    fi

    echo -n "$output"
}
