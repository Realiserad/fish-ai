#!/usr/bin/env fish

function _fish_ai_fix --description "Fix a command using AI." --argument-names previous_command
    if test (~/.fish-ai/bin/lookup_setting "debug") = True
        set output (~/.fish-ai/bin/fix "$previous_command")
    else
        set output (~/.fish-ai/bin/fix "$previous_command" 2> /dev/null)
    end
    echo -n "$output"
end
