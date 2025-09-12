#!/usr/bin/env fish

function _fish_ai_autocomplete_or_fix --description "Autocomplete the current command or fix the previous command using AI."
    set -f previous_status $status

    set -f input (commandline --current-buffer)

    _fish_ai_show_progress_indicator

    if test -z "$input" && test $previous_status -ne 0
        # Fix the previous command.
        set -l previous_command (history | head -1)
        set -l output (_fish_ai_fix "$previous_command")
        commandline --replace "$output"
    else if test -n "$input"
        # Autocomplete the current command.
        set -l cursor_position (commandline --cursor)
        set -l output (_fish_ai_autocomplete "$input" "$cursor_position")
        set -l completion_length (math (string length "$output") - (string length "$input"))
        commandline --replace "$output"
        commandline --cursor (math $cursor_position + $completion_length)
    end

    commandline -f repaint
end
