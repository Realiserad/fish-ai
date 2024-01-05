#!/usr/bin/env fish

function codify --description "Turn a comment into a command and vice versa using AI."
    set dir (dirname (status -f))
    set buffer (commandline -b)
    set command (echo -n "$buffer" | "$dir/codify.py")
    commandline -r "$command"
end
