#!/usr/bin/env fish

set -g install_dir (test -z "$XDG_DATA_HOME"; and echo "$HOME/.local/share/fish-ai"; or echo "$XDG_DATA_HOME/fish-ai")

function fish_ai_switch_context --description "Interactively switch to a different context."
    "$install_dir/bin/switch_context"
end
