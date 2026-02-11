#!/usr/bin/env fish

function _fish_ai_codify_or_explain --description "Transform a command into a comment and vice versa using AI."
    set -f input (commandline --current-buffer | string collect)

    if test -z "$input"
        return
    end

    _fish_ai_show_progress_indicator

    if string match -q "# *" (string trim "$input")
        set -f output (_fish_ai_codify "$input" | string collect)
    else
        set -f output (_fish_ai_explain "$input" | string collect)
    end

    commandline --replace "$output"

    commandline -f repaint
end
