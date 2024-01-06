#!/usr/bin/env fish

function explain --description "Turn a command into a comment using AI." --argument-names command
    set dir (dirname (status -f))
    echo -n "$command" | "$dir/explain.py"
end