#!/usr/bin/env fish

function _fish_ai_explain --description "Turn a command into a comment using AI." --argument-names command
    set dir (dirname (status -f))
    set output ("$dir/_fish_ai_explain.py" "$command")
    echo -n "$output"
end
