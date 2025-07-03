#!/usr/bin/env fish

set install_dir "$(get_install_dir)"
function fish_ai_put_api_key --description "Put an API key on the user's keyring."
    "$install_dir/bin/put_api_key"
end
