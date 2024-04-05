function fish_ai_bug_report
    echo "Environment:"
    echo ""
    set_color green
    echo "$(cat /etc/os-release | grep PRETTY | cut -d= -f2 | tr -d '\"')"
    echo "$(fish --version)"
    echo "$(openai --version)"
    echo "$(python3 --version)"
    set_color normal
    echo ""
    echo "Configuration:"
    echo ""
    set_color green
    echo "$(sed '/api_key/d' ~/.config/fish-ai.ini)"
    set_color normal
end
