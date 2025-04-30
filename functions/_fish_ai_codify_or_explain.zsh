#!/usr/bin/env zsh

function _fish_ai_codify_or_explain {
    local input=$(fc -ln -0)

    show_progess_indicator

    if [[ -z "$input" ]]; then
        return
    fi

    if [[ "$input" == "# "* ]]; then
        local output=$(_fish_ai_codify "$input")
    else
        local output=$(_fish_ai_explain "$input")
    fi

    fc -R <<< "$output"
    zle reset-prompt
}
