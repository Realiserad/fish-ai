#!/usr/bin/env fish

function _fish_ai_autocomplete --description "Autocomplete the current command using AI." --argument-names command cursor_position
    if test ("$_fish_ai_install_dir/bin/lookup_setting" "debug") = True
        set -f selected_completion ("$_fish_ai_install_dir/bin/autocomplete" "$command" "$cursor_position")
    else
        set -f selected_completion ("$_fish_ai_install_dir/bin/autocomplete" "$command" "$cursor_position" 2> /dev/null)
    end
    echo -n "$selected_completion"
end
