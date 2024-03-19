#!/usr/bin/env fish

function _fish_ai_codify --description "Turn a comment into a command using AI." --argument-names comment
    set dir (dirname (status -f))
    set output ("$dir/_fish_ai_codify.py" "$comment")
    echo -n "$output"
end
