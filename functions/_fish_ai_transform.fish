#!/usr/bin/env fish

function _fish_ai_transform --description "Transforms the current commandline using AI."
    set input (commandline -b)
    if test -z "$input"
        # Not clear what should happen here, let's just return the last executed command
        commandline -r (history | head -n1)
        return
    end

    if test (string sub --length 2 "$input") = "# "
        set command (codify "$input")
        commandline -r "$command"
    else
        set comment (explain "$input")
        commandline -r "# $comment"
    end
end