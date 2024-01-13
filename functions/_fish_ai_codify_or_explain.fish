#!/usr/bin/env fish

function _fish_ai_codify_or_explain --description "Transform a command into a comment and vice versa using AI."
    set input (commandline --current-buffer)
    if test -z "$input"
        return
    end

    if test (string sub --length 2 "$input") = "# "
        set command (_fish_ai_codify "$input")
        commandline --replace "$command"
    else
        set comment (_fish_ai_explain "$input")
        commandline --replace "# $comment"
    end
end