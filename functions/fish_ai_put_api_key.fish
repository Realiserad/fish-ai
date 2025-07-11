#!/usr/bin/env fish

set -g install_dir (test -z "$XDG_DATA_HOME"; and echo "$HOME/.local/share/fish-ai"; or echo "$XDG_DATA_HOME/fish-ai")

function fish_ai_put_api_key --description "Put an API key on the user's keyring."
    "$install_dir/bin/put_api_key"
end
