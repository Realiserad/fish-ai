#!/usr/bin/env zsh

function _fish_ai_autocomplete_or_fix {
    local previous_status=$?

    local input=$(fc -ln -0)

    show_progess_indicator

    if [[ -z "$input" && $previous_status -ne 0 ]]; then
        # Fix the previous command.
        local previous_command=$(fc -ln -1)
        local output=$(_fish_ai_fix "$previous_command")
        fc -s "$output"
    elif [[ -n "$input" ]]; then
        # Autocomplete the current command.
        local cursor_position=${#input}
        local output=$(_fish_ai_autocomplete "$input" "$cursor_position")
        local completion_length=$((${#output} - ${#input}))
        fc -s "$output"
        zle redisplay
    fi
}
