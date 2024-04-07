function fish_ai_bug_report
    echo "Environment:"
    set_color normal
    echo ""
    set_color blue
    cat /etc/os-release | grep PRETTY | cut -d= -f2 | tr -d '\"'
    ~/.fish-ai/bin/python3 --version
    fish --version
    set_color normal
    echo ""
    echo "Dependencies:"
    set_color normal
    echo ""
    set_color blue
    ~/.fish-ai/bin/pip list --format columns | grep -E '(fish_ai)|(openai)|(google-generativeai)'
    set_color normal
    echo ""
    echo "Configuration:"
    set_color normal
    echo ""
    set_color blue
    sed /api_key/d ~/.config/fish-ai.ini
    set_color normal
end
