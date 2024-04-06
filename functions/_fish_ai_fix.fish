#!/usr/bin/env fish

function _fish_ai_fix --description "Fix a command using AI." --argument-names previous_command
    set dir (dirname (status -f))
    set output (~/.fish-ai/bin/python3 "$dir/_fish_ai_fix.py" "$previous_command")
    echo -n "$output"
end
