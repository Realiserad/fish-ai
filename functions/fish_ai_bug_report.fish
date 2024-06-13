#!/usr/bin/env fish

function fish_ai_bug_report
    print_header Environment
    print_environment

    print_header Dependencies
    print_dependencies

    print_header "Fish plugins"
    print_fish_plugins

    print_header Configuration
    print_configuration

    print_header "Functionality tests"
    perform_functionality_tests

    if test "$error_found" = true
        echo "❌ Problems were found (see output above for details)."
        return 1
    end
end

function print_header --argument-names title
    set_color --bold blue
    echo "$title"
    echo ""
    set_color normal
end

function print_environment
    if test -f /etc/os-release
        echo "Running on $(cat /etc/os-release | grep PRETTY | cut -d= -f2 | tr -d '\"')"
    else if type -q sw_vers
        echo "Running on Mac OS X $(sw_vers --productVersion)"
    else
        echo "❌ Running on an unsupported platform."
        set -g error_found true
    end

    echo ""
end

function print_dependencies
    if ! test -d ~/.fish-ai
        echo "❌ The virtual environment '$(echo ~/.fish-ai)' does not exist."
        set -g error_found true
        return
    end

    ~/.fish-ai/bin/python3 --version
    fish --version
    fisher --version
    git --version
    echo ""

    ~/.fish-ai/bin/pip list
    if ! test (~/.fish-ai/bin/pip list | grep fish_ai)
        echo "❌ The Python package 'fish_ai' could not be found."
        set -g error_found true
    end

    echo ""
end

function print_fish_plugins
    fisher list
    echo ""
end

function print_configuration
    if ! test -f ~/.config/fish-ai.ini
        echo "😕 The configuration file '$(echo ~/.config/fish-ai.ini)' does not exist."
    else
        sed /api_key/d ~/.config/fish-ai.ini | sed /password/d
    end

    echo ""
end

function perform_functionality_tests
    if ! test -f ~/.config/fish-ai.ini
        echo "😴 No configuration available. Skipping."
        return
    end

    echo "🔥 Running functionality tests..."

    set start (date +%s%3N)
    set result (_fish_ai_codify 'print the current date')
    set duration (math (date +%s%3N) - $start)
    echo "codify 'print the current date' -> '$result' (in $duration ms)"

    set start (date +%s%3N)
    set result (_fish_ai_explain 'date' | \
        string trim --chars '# ' | \
        string shorten --max 50)
    set duration (math (date +%s%3N) - $start)
    echo "explain 'date' -> '$result' (in $duration ms)"
end
