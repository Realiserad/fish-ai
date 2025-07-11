#!/usr/bin/env fish

set -g install_dir (test -z "$XDG_DATA_HOME"; and echo "$HOME/.local/share/fish-ai"; or echo "$XDG_DATA_HOME/fish-ai")

function _fish_ai_autocomplete --description "Autocomplete the current command using AI." --argument-names command cursor_position
    if test ("$install_dir/bin/lookup_setting" "debug") = True
        set selected_completion ("$install_dir/bin/autocomplete" "$command" "$cursor_position")
    else
        set selected_completion ("$install_dir/bin/autocomplete" "$command" "$cursor_position" 2> /dev/null)
    end
    echo -n "$selected_completion"
end
