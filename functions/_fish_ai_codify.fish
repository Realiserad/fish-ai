#!/usr/bin/env fish

function _fish_ai_codify --description "Turn a comment into a command using AI." --argument-names comment
    set output (~/.fish-ai/bin/codify "$comment" 2> /dev/null)
    echo -n "$output"
end
