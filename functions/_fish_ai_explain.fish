#!/usr/bin/env fish

function _fish_ai_explain --description "Turn a command into a comment using AI." --argument-names command
    if test (~/.fish-ai/bin/lookup_setting "debug") = True
        set output (~/.fish-ai/bin/explain "$command")
    else
        set output (~/.fish-ai/bin/explain "$command" 2> /dev/null)
    end
    echo -n "$output"
end
