#!/usr/bin/env fish

function _fish_ai_codify_or_explain --description "Transform a command into a comment and vice versa using AI."
    if test (~/.fish-ai/bin/lookup_setting status_emoji) != False
        eval "function fish_right_prompt; echo (string escape \$status_emoji); end"
    end

    set input (commandline --current-buffer)

    if test -z "$input"
        return
    end

    if test (string sub --length 2 "$input") = "# "
        set output (_fish_ai_codify "$input")
    else
        set output (_fish_ai_explain "$input")
    end

    commandline --replace "$output"

    if test "$output" = "$input"
        set -g status_emoji '❌'
    else
        set -g status_emoji '✅'
    end
    commandline -f repaint
end
