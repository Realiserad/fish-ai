#!/usr/bin/env fish

function _fish_ai_fix --description "Fix a command using AI." --argument-names "previous_command" "error_message"
    set dir (dirname (status -f))
    set output ("$dir/_fish_ai_fix.py" "$previous_command" "$error_message")
    echo -n "$output"
end