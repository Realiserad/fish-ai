#!/usr/bin/env fish

set -g install_dir (test -z "$XDG_DATA_HOME"; and echo "$HOME/.local/share/fish-ai"; or echo "$XDG_DATA_HOME/fish-ai")

function _fish_ai_codify --description "Turn a comment into a command using AI." --argument-names comment
    if test ("$install_dir/bin/lookup_setting" "debug") = True
        set output ("$install_dir/bin/codify" "$comment")
    else
        set output ("$install_dir/bin/codify" "$comment" 2> /dev/null)
    end
    echo -n "$output"
end
