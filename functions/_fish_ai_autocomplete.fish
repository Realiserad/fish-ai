#!/usr/bin/env fish

function _fish_ai_autocomplete --description "Autocomplete the current command using AI." --argument-names command cursor_position
    set output (~/.fish-ai/bin/autocomplete "$command" "$cursor_position")
    echo -n "$output"
end
