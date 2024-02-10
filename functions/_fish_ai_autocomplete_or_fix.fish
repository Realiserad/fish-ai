#!/usr/bin/env fish

function _fish_ai_autocomplete_or_fix --description "Autocomplete the current command or fix the previous command using AI."
    set previous_status $status
    if test -z "$input" && test $previous_status -ne 0
        # Fix the previous command.
        set previous_command (history | head -1)
        set fixed_command (_fish_ai_fix "$previous_command")
        commandline --replace "$fixed_command"
    else
        # Autocomplete the current command
        set input (commandline --current-buffer)
        set cursor_position (commandline --cursor)
        set output (_fish_ai_autocomplete "$input" "$cursor_position")
        commandline --insert "$output"
    end
end