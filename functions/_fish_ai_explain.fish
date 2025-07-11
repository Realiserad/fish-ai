#!/usr/bin/env fish

set -g install_dir (test -z "$XDG_DATA_HOME"; and echo "$HOME/.local/share/fish-ai"; or echo "$XDG_DATA_HOME/fish-ai")

function _fish_ai_explain --description "Turn a command into a comment using AI." --argument-names command
    if test ("$install_dir/bin/lookup_setting" "debug") = True
        set output ("$install_dir/bin/explain" "$command")
    else
        set output ("$install_dir/bin/explain" "$command" 2> /dev/null)
    end
    echo -n "$output"
end
