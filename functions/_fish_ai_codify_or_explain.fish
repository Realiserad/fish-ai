#!/usr/bin/env fish

function _fish_ai_codify_or_explain --description "Transform a command into a comment and vice versa using AI."
    set -f input (commandline --current-buffer)

    if test -z "$input"
        return
    end

    _fish_ai_show_progress_indicator

    if test (string sub --length 2 "$input") = "# "
        set -f output (_fish_ai_codify "$input")
    else
        set -f output (_fish_ai_explain "$input")
    end

    commandline --replace "$output"

    commandline -f repaint
end
