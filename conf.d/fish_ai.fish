# Get key binding escape sequence with fish_key_reader
bind \cp _fish_ai_codify_or_explain
bind -k nul _fish_ai_autocomplete_or_fix

bind \r 'clear_status; commandline -f execute'
bind \cc 'clear_status; commandline -f repaint; commandline -f cancel-commandline'

function clear_status
    set -e status_emoji
end
