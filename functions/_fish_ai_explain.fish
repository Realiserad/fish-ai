#!/usr/bin/env fish

function _fish_ai_explain --description "Turn a command into a comment using AI." --argument-names command
    if test ("$_fish_ai_install_dir/bin/lookup_setting" "debug") = True
        set -f output ("$_fish_ai_install_dir/bin/explain" "$command")
    else
        set -f output ("$_fish_ai_install_dir/bin/explain" "$command" 2> /dev/null)
    end
    echo -n "$output"
end
