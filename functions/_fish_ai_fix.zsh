#!/usr/bin/env zsh

function _fish_ai_fix {
    local previous_command=$1
    if [[ $(~/.fish-ai/bin/lookup_setting "debug") == "True" ]]; then
        local output=$(~/.fish-ai/bin/fix "$previous_command")
    else
        local output=$(~/.fish-ai/bin/fix "$previous_command" 2> /dev/null)
    fi
    echo -n "$output"
}
