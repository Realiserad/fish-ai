#!/usr/bin/env fish

set install_dir "$(get_install_dir)"

function _fish_ai_codify --description "Turn a comment into a command using AI." --argument-names comment
    if test ("$install_dir/bin/lookup_setting" "debug") = True
        set output ("$install_dir/bin/codify" "$comment")
    else
        set output ("$install_dir/bin/codify" "$comment" 2> /dev/null)
    end
    echo -n "$output"
end
