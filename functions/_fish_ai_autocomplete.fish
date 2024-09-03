#!/usr/bin/env fish

function _fish_ai_autocomplete --description "Autocomplete the current command using AI." --argument-names command cursor_position
    set selected_completion (~/.fish-ai/bin/autocomplete "$command" "$cursor_position" 2> /dev/null)
    echo -n "$selected_completion"
end
