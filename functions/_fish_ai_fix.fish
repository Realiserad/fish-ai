#!/usr/bin/env fish

function _fish_ai_fix --description "Fix a command using AI." --argument-names previous_command
    if test ("$_fish_ai_install_dir/bin/lookup_setting" "debug") = True
        set -f output ("$_fish_ai_install_dir/bin/fix" "$previous_command")
    else
        set -f output ("$_fish_ai_install_dir/bin/fix" "$previous_command" 2> /dev/null)
    end
    echo -n "$output"
end
