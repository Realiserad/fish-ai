#!/usr/bin/env fish

function _fish_ai_codify --description "Turn a comment into a command using AI." --argument-names comment
    if test ("$_fish_ai_install_dir/bin/lookup_setting" "debug") = True
        set -f output ("$_fish_ai_install_dir/bin/codify" "$comment")
    else
        set -f output ("$_fish_ai_install_dir/bin/codify" "$comment" 2> /dev/null)
    end
    echo -n "$output"
end
