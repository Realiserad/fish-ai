#!/usr/bin/env fish

function _fish_ai_fix --description "Fix a command using AI." --argument-names previous_command
    set output (~/.fish-ai/bin/fix "$previous_command")
    echo -n "$output"
end
