#!/usr/bin/env zsh

function _fish_ai_autocomplete {
    local command="$1"
    local cursor_position="$2"
    local selected_completion

    if [[ $(~/.fish-ai/bin/lookup_setting "debug") == "True" ]]; then
        selected_completion=$(~/.fish-ai/bin/autocomplete "$command" "$cursor_position")
    else
        selected_completion=$(~/.fish-ai/bin/autocomplete "$command" "$cursor_position" 2> /dev/null)
    fi

    echo -n "$selected_completion"
}
