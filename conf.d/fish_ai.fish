##
## This section contains the keybindings for fish-ai. If you want to change the
## default keybindings, edit the key binding escape sequences below according to
## your needs. You can get the key binding escape sequence for a keyboard shortcut
## using the command `fish_key_reader`.
##
bind \cp _fish_ai_codify_or_explain
bind -k nul _fish_ai_autocomplete_or_fix

##
## This section contains functionality for setting and clearing the status shown
## in the right prompt.
##
bind \r 'clear_status; commandline -f execute'
bind \cc 'clear_status; commandline -f repaint; commandline -f cancel-commandline'

function clear_status
    set -e status_emoji
end

##
## This section contains the plugin lifecycle hooks invoked by the fisher package
## manager.
##
function _fish_ai_install --on-event fish_ai_install
    python3 -m venv ~/.fish-ai
    ~/.fish-ai/bin/pip install -qq openai
end

function _fish_ai_update --on-event fish_ai_update
    ~/.fish-ai/bin/pip install -qq --upgrade openai
end

function __fish_ai_uninstall --on-event fish_ai_uninstall
    rm -r ~/.fish-ai
end
