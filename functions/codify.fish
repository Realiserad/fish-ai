#!/usr/bin/env fish

function codify --description "Turn a comment into a command using AI." --argument-names comment
    set dir (dirname (status -f))
    echo -n "$comment" | "$dir/codify.py"
end