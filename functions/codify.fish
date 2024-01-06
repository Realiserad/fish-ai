#!/usr/bin/env fish

function codify --description "Turn a comment into a command and vice versa using AI."
    set dir (dirname (status -f))
    if set -q argv[1]
        set input "$argv[1]"
        set output (echo -n "# $input" | "$dir/codify.py")
        echo "$output"
    else
        set input (commandline -b)
        if test -n "$input"
            set output (echo -n "$input" | "$dir/codify.py")
            commandline -r "$output"
        else
            echo "# No input"
        end
    end
end
