#!/usr/bin/env fish

set install_dir "$(get_install_dir)"

function _fish_ai_autocomplete --description "Autocomplete the current command using AI." --argument-names command cursor_position
    if test ("$install_dir/bin/lookup_setting" "debug") = True
        set selected_completion ("$install_dir/bin/autocomplete" "$command" "$cursor_position")
    else
        set selected_completion ("$install_dir/bin/autocomplete" "$command" "$cursor_position" 2> /dev/null)
    end
    echo -n "$selected_completion"
end
