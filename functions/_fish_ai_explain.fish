#!/usr/bin/env fish

function _fish_ai_explain --description "Turn a command into a comment using AI." --argument-names command
    if test ("$_fish_ai_install_dir/bin/lookup_setting" "debug") = True
        set -f output ("$_fish_ai_install_dir/bin/explain" "$command" | \
            string collect)
    else
        set -f output ("$_fish_ai_install_dir/bin/explain" "$command" | \
            string collect 2> /dev/null)
    end
    echo -n "$output"
end
