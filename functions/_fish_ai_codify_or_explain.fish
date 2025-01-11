#!/usr/bin/env fish

function _fish_ai_codify_or_explain --description "Transform a command into a comment and vice versa using AI."
    set input (commandline --current-buffer)

    show_progess_indicator

    if test -z "$input"
        return
    end

    if test (string sub --length 2 "$input") = "# "
        set output (_fish_ai_codify "$input")
    else
        set output (_fish_ai_explain "$input")
    end

    commandline --replace "$output"

    commandline -f repaint
end
