#!/usr/bin/env fish

function _fish_ai_autocomplete --description "Autocomplete the current command using AI." --argument-names command cursor_position
    set dir (dirname (status -f))
    set output (~/.fish-ai/bin/python3 "$dir/_fish_ai_autocomplete.py" "$command" "$cursor_position")
    echo -n "$output"
end
