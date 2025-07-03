#!/usr/bin/env fish

set install_dir "$(get_install_dir)"

function fish_ai_switch_context --description "Interactively switch to a different context."
    "$install_dir/bin/switch_context"
end
