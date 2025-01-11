#!/usr/bin/env fish

function _fish_ai_autocomplete_or_fix --description "Autocomplete the current command or fix the previous command using AI."
    set previous_status $status

    set input (commandline --current-buffer)

    show_progess_indicator

    if test -z "$input" && test $previous_status -ne 0
        # Fix the previous command.
        set previous_command (history | head -1)
        set output (_fish_ai_fix "$previous_command")
        commandline --replace "$output"
    else if test -n "$input"
        # Autocomplete the current command.
        set cursor_position (commandline --cursor)
        set output (_fish_ai_autocomplete "$input" "$cursor_position")
        set completion_length (math (string length "$output") - (string length "$input"))
        commandline --replace "$output"
        commandline --cursor (math $cursor_position + $completion_length)
    end

    commandline -f repaint
end
