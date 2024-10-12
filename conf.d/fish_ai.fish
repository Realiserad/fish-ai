##
## Supported major.minor versions of Python.
## Unit tests are run in CI against these versions.
##
set -g supported_versions 3.9 3.10 3.11 3.12

##
## This section contains the keybindings for fish-ai. If you want to change the
## default keybindings, edit the key binding escape sequences below according to
## your needs. You can get the key binding escape sequence for a keyboard shortcut
## using the command `fish_key_reader`.
##
bind \cP _fish_ai_codify_or_explain
bind -k nul _fish_ai_autocomplete_or_fix

##
## This section contains functionality for clearing the status emoji
## shown in the right prompt.
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
    echo "🥡 Setting up a virtual environment..."
    if test -n "$FISH_AI_PYTHON_VERSION"
        echo "🐍 Using Python $FISH_AI_PYTHON_VERSION as specified by the environment variable 'FISH_AI_PYTHON_VERSION'."
        set python_exe python$FISH_AI_PYTHON_VERSION
    else
        set python_exe python3
    end
    $python_exe -m venv ~/.fish-ai
    echo "🍬 Installing dependencies. This may take a few seconds..."
    ~/.fish-ai/bin/pip install -qq "$(get_installation_url)"
    python_version_check
    if ! test -f ~/.config/fish-ai.ini
        echo "🤗 You must create a configuration file before the plugin can be used!"
    end
end

function _fish_ai_update --on-event fish_ai_update
    if test -n "$FISH_AI_PYTHON_VERSION"
        echo "🐍 Using Python $FISH_AI_PYTHON_VERSION as specified by the environment variable 'FISH_AI_PYTHON_VERSION'."
        set python_exe python$FISH_AI_PYTHON_VERSION
    else
        set python_exe python3
    end
    $python_exe -m venv --upgrade ~/.fish-ai
    echo "🐍 Now using $(~/.fish-ai/bin/python3 --version)."
    echo "🍬 Upgrading dependencies. This may take a few seconds..."
    ~/.fish-ai/bin/pip install -qq --upgrade "$(get_installation_url)"
    python_version_check
end

function _fish_ai_uninstall --on-event fish_ai_uninstall
    if test -d ~/.fish-ai
        echo "💣 Nuking the virtual environment..."
        rm -r ~/.fish-ai
    end
end

function get_installation_url
    set plugin (fisher list "fish-ai")
    if test "$plugin" = ""
        # fish-ai may be installed from an unknown source, assume
        # that the Python packages can be installed from the
        # current working directory.
        echo -n (pwd)
    else if test (string sub --start 1 --length 1 "$plugin") = /
        # Install from a local folder (most likely a git clone)
        echo -n "$plugin"
    else
        # Install from GitHub
        echo -n "fish-ai@git+https://github.com/$plugin"
    end
end

function python_version_check
    set python_version (~/.fish-ai/bin/python3 -c 'import platform; major, minor, _ = platform.python_version_tuple(); print(major, end="."); print(minor, end="")')
    if ! contains $python_version $supported_versions
        echo "🔔 This plugin has not been tested with Python $python_version and may not function correctly."
        echo "The following versions are supported: $supported_versions"
        echo "Consider setting the environment variable 'FISH_AI_PYTHON_VERSION' to a supported version and reinstalling the plugin. For example:"
        set_color --italics blue
        echo ""
        echo "  fisher remove realiserad/fish-ai"
        echo "  set -g FISH_AI_PYTHON_VERSION $supported_versions[-1]"
        echo "  fisher install realiserad/fish-ai"
        echo ""
        set_color normal
    end
end
