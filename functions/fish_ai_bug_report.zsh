#!/usr/bin/env zsh

function fish_ai_bug_report {
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

    if [[ "$error_found" == true ]]; then
        echo "❌ Problems were found (see output above for details)."
        return 1
    fi
}

function print_header {
    local title="$1"
    echo -e "\e[1;34m$title\e[0m\n"
}

function print_environment {
    if [[ -f /etc/os-release ]]; then
        echo "Running on $(grep PRETTY /etc/os-release | cut -d= -f2 | tr -d '\"')"
        echo "Machine hardware: $(uname -m)"
    elif type -q sw_vers; then
        echo "Running on macOS $(sw_vers --productVersion)"
        echo "Machine hardware: $(uname -m)"
    else
        echo "❌ Running on an unsupported platform."
        error_found=true
    fi

    echo ""
}

function print_key_bindings {
    bindkey | grep --color=never _fish_ai
    echo ""
    echo "Key bindings in use: $KEYMAP"
    echo ""
}

function print_dependencies {
    if [[ ! -d ~/.fish-ai ]]; then
        echo "❌ The virtual environment '$(echo ~/.fish-ai)' does not exist."
        error_found=true
        return
    fi

    if type -q uv; then
        echo "😎 This system has uv installed."
    fi
    echo "Python version used by fish-ai: $(~/.fish-ai/bin/python3 --version)"
    if type -q python3; then
        echo "Python version used by the system: $(python3 --version)"
    fi
    fish --version
    fisher --version
    git --version
    echo ""

    ~/.fish-ai/bin/pip list
    if ! ~/.fish-ai/bin/pip list | grep -q fish_ai; then
        echo "❌ The Python package 'fish_ai' could not be found."
        error_found=true
    fi

    echo ""
}

function print_fish_plugins {
    fisher list
    echo ""
}

function print_configuration {
    if [[ ! -f ~/.config/fish-ai.ini ]]; then
        echo "😕 The configuration file '$(echo ~/.config/fish-ai.ini)' does not exist."
    else
        sed /api_key/d ~/.config/fish-ai.ini | sed /password/d
    fi

    echo ""
}

function perform_functionality_tests {
    if [[ ! -f ~/.config/fish-ai.ini ]]; then
        echo "😴 No configuration available. Skipping."
        echo ""
        return
    fi

    echo "🔥 Running functionality tests..."

    local start=$(date +%s)
    local result=$(_fish_ai_codify 'print the current date')
    local duration=$(( $(date +%s) - start ))
    echo "codify 'print the current date' -> '$result' (in $duration seconds)"

    start=$(date +%s)
    result=$(_fish_ai_explain 'date' | \
        sed 's/^# //' | \
        awk '{ if (length($0) > 50) print substr($0, 1, 50) "..."; else print $0 }')
    duration=$(( $(date +%s) - start ))
    echo "explain 'date' -> '$result' (in $duration seconds)"
    echo ""
}

function perform_compatibility_check {
    source ~/.config/fish/conf.d/fish_ai.zsh
    local python_version=$(~/.fish-ai/bin/python3 -c 'import platform; major, minor, _ = platform.python_version_tuple(); print(major, end="."); print(minor, end="")')
    if ! echo "$supported_versions" | grep -q "$python_version"; then
        echo "🔔 This plugin has not been tested with Python $python_version and may not function correctly."
        echo "The following versions are supported: $supported_versions"
        error_found=true
    else
        echo "👍 Python $python_version is supported."
    fi
    echo ""
}

function print_logs {
    local log_file=$(~/.fish-ai/bin/python3 -c "import os; print(os.path.expanduser('$(~/.fish-ai/bin/lookup_setting log)'))")
    if [[ ! -f "$log_file" ]]; then
        echo "😴 No log file available."
        return
    fi
    print_last_section "$log_file"
    if [[ $(~/.fish-ai/bin/lookup_setting debug) != True ]]; then
        echo ""
        echo "🙏 Consider enabling debug mode to get more log output."
    fi
}

function print_last_section {
    local log_file="$1"
    local len=$(wc -l < "$log_file")
    for ((i = len; i >= 1; i--)); do
        local line=$(sed -n "${i}p" "$log_file")
        if [[ "$line" == "----- BEGIN SESSION -----" ]]; then
            for ((j = i; j <= len; j++)); do
                sed -n "${j}p" "$log_file"
            done
            return
        fi
    done
}
