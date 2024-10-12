#!/usr/bin/env fish

function _fish_ai_codify --description "Turn a comment into a command using AI." --argument-names comment
    if test (~/.fish-ai/bin/lookup_setting "debug") = True
        set output (~/.fish-ai/bin/codify "$comment")
    else
        set output (~/.fish-ai/bin/codify "$comment" 2> /dev/null)
    end
    echo -n "$output"
end
