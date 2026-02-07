#!/usr/bin/env fish

function _fish_ai_codify --description "Turn a comment into a command using AI." --argument-names comment
    if test ("$_fish_ai_install_dir/bin/lookup_setting" "debug") = True
        set -f output ("$_fish_ai_install_dir/bin/codify" "$comment" | \
            fish_indent | \
            string collect)
    else
        set -f output ("$_fish_ai_install_dir/bin/codify" "$comment" | \
            fish_indent | \
            string collect 2> /dev/null)
    end
    printf '%s' "$output"
end
