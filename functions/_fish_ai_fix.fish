#!/usr/bin/env fish

set install_dir "$(get_install_dir)"

function _fish_ai_fix --description "Fix a command using AI." --argument-names previous_command
    if test ("$install_dir/bin/lookup_setting" "debug") = True
        set output ("$install_dir/bin/fix" "$previous_command")
    else
        set output ("$install_dir/bin/fix" "$previous_command" 2> /dev/null)
    end
    echo -n "$output"
end
