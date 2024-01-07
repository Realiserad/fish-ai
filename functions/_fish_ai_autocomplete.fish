#!/usr/bin/env fish

function _fish_ai_autocomplete --description "Autocomplete a shell command using AI."
    set input (commandline -b)
    set cursor_position (commandline --cursor)
    set dir (dirname (status -f))
    set output (echo -n "$input" | "$dir/autocomplete.py" $cursor_position)
    commandline --insert "$output"
end