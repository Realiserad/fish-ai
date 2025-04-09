#!/usr/bin/env fish

function fish_ai_bug_report
    print_header Environment
    print_environment

    print_header "Key bindings"
    print_key_bindings

    print_header Dependencies
    print_dependencies

    print_header "Fish plugins"
    print_fish_plugins

    print_header Configuration
    print_configuration

    print_header "Functionality tests"
    perform_functionality_tests

    print_header "Compatibility check"
    perform_compatibility_check

    print_header "Logs from the last session"
    print_logs

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
        echo "Machine hardware: $(uname -m)"
    else if type -q sw_vers
        echo "Running on macOS $(sw_vers --productVersion)"
        echo "Machine hardware: $(uname -m)"
    else
        echo "❌ Running on an unsupported platform."
        set -g error_found true
    end

    echo ""
end

function print_key_bindings
    bind --key | grep --color=never _fish_ai
    echo ""
    echo "Key bindings in use: $fish_key_bindings"
    echo ""
end

function print_dependencies
    if ! test -d ~/.fish-ai
        echo "❌ The virtual environment '$(echo ~/.fish-ai)' does not exist."
        set -g error_found true
        return
    end

    if type -q uv
        echo "😎 This system has uv installed."
    end
    echo "Python version used by fish-ai: $(~/.fish-ai/bin/python3 --version)"
    if type -q python3
        echo "Python version used by the system: $(python3 --version)"
    end
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
        echo ""
        return
    end

    echo "🔥 Running functionality tests..."

    set start (date +%s)
    set result (_fish_ai_codify 'print the current date')
    set duration (math (date +%s) - $start)
    echo "codify 'print the current date' -> '$result' (in $duration seconds)"

    set start (date +%s)
    set result (_fish_ai_explain 'date' | \
        string trim --chars '# ' | \
        string shorten --max 50)
    set duration (math (date +%s) - $start)
    echo "explain 'date' -> '$result' (in $duration seconds)"
    echo ""
end

function perform_compatibility_check
    source ~/.config/fish/conf.d/fish_ai.fish
    set python_version (~/.fish-ai/bin/python3 -c 'import platform; major, minor, _ = platform.python_version_tuple(); print(major, end="."); print(minor, end="")')
    if ! contains $python_version $supported_versions
        echo "🔔 This plugin has not been tested with Python $python_version and may not function correctly."
        echo "The following versions are supported: $supported_versions"
        set -g error_found true
    else
        echo "👍 Python $python_version is supported."
    end
    echo ""
end

function print_logs
    set log_file (~/.fish-ai/bin/python3 -c "import os; print(os.path.expanduser('$(~/.fish-ai/bin/lookup_setting log)'))")
    if ! test -f "$log_file"
        echo "😴 No log file available."
        return
    end
    print_last_section "$log_file"
    if test (~/.fish-ai/bin/lookup_setting debug) != True
        echo ""
        echo "🙏 Consider enabling debug mode to get more log output."
    end
end

function print_last_section --argument-names log_file
    set -l len (wc -l $log_file | awk '{ print $1 }')
    for i in (seq $len -1 1)
        set -l line (sed -n "$i p" "$log_file")
        if test "$line" = "----- BEGIN SESSION -----"
            for j in (seq $i $len)
                echo (sed -n "$j p" "$log_file")
            end
            return
        end
    end
end
