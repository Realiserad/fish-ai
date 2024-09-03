#!/usr/bin/env fish

function _fish_ai_explain --description "Turn a command into a comment using AI." --argument-names command
    set output (~/.fish-ai/bin/explain "$command" 2> /dev/null)
    echo -n "$output"
end
