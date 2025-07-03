#!/usr/bin/env fish

set install_dir "$(get_install_dir)"

function _fish_ai_explain --description "Turn a command into a comment using AI." --argument-names command
    if test ("$install_dir/bin/lookup_setting" "debug") = True
        set output ("$install_dir/bin/explain" "$command")
    else
        set output ("$install_dir/bin/explain" "$command" 2> /dev/null)
    end
    echo -n "$output"
end
