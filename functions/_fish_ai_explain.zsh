#!/usr/bin/env zsh

function _fish_ai_explain {
    local command=$1
    local output

    if [[ $(~/.fish-ai/bin/lookup_setting "debug") == "True" ]]; then
        output=$(~/.fish-ai/bin/explain "$command")
    else
        output=$(~/.fish-ai/bin/explain "$command" 2> /dev/null)
    fi

    echo -n "$output"
}
