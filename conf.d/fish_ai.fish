##
## Supported major.minor versions of Python.
## Unit tests are run in CI against these versions.
##
set -g supported_versions 3.9 3.10 3.11 3.12 3.13

##
## This section contains the keybindings for fish-ai. If you want to change the
## default keybindings, use the environment variables:
##
##   - FISH_AI_KEYMAP_1 (defaults to Ctrl + P)
##   - FISH_AI_KEYMAP_2 (defaults to Ctrl + Space)
##
## These should be set to the key binding escape sequence for a keyboard shortcut
## you want to use + any flags. You can get the key binding escape sequence using
## the command `fish_key_reader`.
##
if test -n "$FISH_AI_KEYMAP_1"
    set -g keymap_1 "$FISH_AI_KEYMAP_1"
else
    set -g keymap_1 \cp
end
if test -n "$FISH_AI_KEYMAP_2"
    set -g keymap_2 "$FISH_AI_KEYMAP_2"
else
    if type -q sw_vers
        # macOS
        set -g keymap_2 ctrl-space
    else
        # Linux
        set -g keymap_2 -k nul
    end
end
if test "$fish_key_bindings" = fish_vi_key_bindings
    set -g bind_command bind -M insert
else
    set -g bind_command bind
end
$bind_command $keymap_1 _fish_ai_codify_or_explain
$bind_command $keymap_2 _fish_ai_autocomplete_or_fix

##
## This section contains the plugin lifecycle hooks invoked by the fisher package
## manager.
##
function _fish_ai_install --on-event fish_ai_install
    set_python_version
    if type -q uv
        echo "🥡 Setting up a virtual environment using uv..."
        uv venv --seed --python $python_version ~/.fish-ai
    else
        echo "🥡 Setting up a virtual environment using venv..."
        python$python_version -m venv ~/.fish-ai
    end
    if test $status -ne 0
        echo "💔 Installation failed. Check previous terminal output for details."
        return 1
    end

    echo "🍬 Installing dependencies. This may take a few seconds..."
    ~/.fish-ai/bin/pip -qq install "$(get_installation_url)"
    if test $status -ne 0
        echo "💔 Installation from '$(get_installation_url)' failed. Check previous terminal output for details."
        return 2
    end
    python_version_check
    notify_custom_keybindings
    symlink_truststore
    autoconfig_gh_models
    if ! test -f ~/.config/fish-ai.ini
        echo "🤗 You must create a configuration file before the plugin can be used!"
    end
end

function _fish_ai_update --on-event fish_ai_update
    set_python_version
    if type -q uv
        uv venv --seed --python $python_version ~/.fish-ai
    else
        python$python_version -m venv --upgrade ~/.fish-ai
    end
    if test $status -ne 0
        echo "💔 Installation failed. Check previous terminal output for details."
        return 1
    end

    echo "🐍 Now using $(~/.fish-ai/bin/python3 --version)."
    echo "🍬 Upgrading dependencies. This may take a few seconds..."
    ~/.fish-ai/bin/pip install -qq --upgrade "$(get_installation_url)"
    if test $status -ne 0
        echo "💔 Installation failed. Check previous terminal output for details."
        return 2
    end
    python_version_check
    notify_custom_keybindings
    symlink_truststore
    warn_plaintext_api_keys
end

function _fish_ai_uninstall --on-event fish_ai_uninstall
    if test -d ~/.fish-ai
        echo "💣 Nuking the virtual environment..."
        rm -r ~/.fish-ai
    end
end

function set_python_version
    if test -n "$FISH_AI_PYTHON_VERSION"
        echo "🐍 Using Python $FISH_AI_PYTHON_VERSION as specified by the environment variable 'FISH_AI_PYTHON_VERSION'."
        set -g python_version $FISH_AI_PYTHON_VERSION
    else if type -q uv
        # Use the last supported version of Python
        set -g python_version $supported_versions[-1]
    else
        # Use the Python version provided by the system
        set -g python_version 3
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

function symlink_truststore --description "Use the bundle with CA certificates trusted by the OS."
    if test -f /etc/ssl/certs/ca-certificates.crt
        echo "🔑 Symlinking to certificates stored in /etc/ssl/certs/ca-certificates.crt."
        ln -snf /etc/ssl/certs/ca-certificates.crt (~/.fish-ai/bin/python3 -c 'import certifi; print(certifi.where())')
    else if test -f /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
        echo "🔑 Symlinking to certificates stored in /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem."
        ln -snf /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem (~/.fish-ai/bin/python3 -c 'import certifi; print(certifi.where())')
    else if test -f /etc/ssl/cert.pem
        echo "🔑 Symlinking to certificates stored in /etc/ssl/cert.pem."
        ln -snf /etc/ssl/cert.pem (~/.fish-ai/bin/python3 -c 'import certifi; print(certifi.where())')
    end
end

function warn_plaintext_api_keys --description "Warn about plaintext API keys."
    if ! test -f ~/.config/fish-ai.ini
        return
    end
    if grep -q "^api_key" ~/.config/fish-ai.ini
        echo -n "🚨 One or more plaintext API keys are stored in "
        set_color --bold red
        echo -n "~/.config/fish-ai.ini"
        set_color normal
        echo -n ". Consider moving them to your keyring using "
        set_color --italics blue
        echo -n fish_ai_put_api_key
        set_color normal
        echo "."
    end
end

function autoconfig_gh_models --description "Deploy configuration for GitHub Models."
    if test -f ~/.config/fish-ai.ini
        return
    end
    if ! type -q gh
        return
    end
    if test -z (gh auth token 2>/dev/null)
        return
    end
    if test -z (gh ext ls | grep "gh models" 2>/dev/null)
        return
    end
    echo "[fish-ai]" >>~/.config/fish-ai.ini
    echo "configuration = github" >>~/.config/fish-ai.ini
    echo "" >>~/.config/fish-ai.ini
    echo "[github]" >>~/.config/fish-ai.ini
    echo "provider = self-hosted" >>~/.config/fish-ai.ini
    echo "server = https://models.inference.ai.azure.com" >>~/.config/fish-ai.ini
    echo "api_key = $(gh auth token)" >>~/.config/fish-ai.ini
    echo "model = gpt-4o-mini" >>~/.config/fish-ai.ini

    echo "😺 Access to GitHub Models has been automatically configured for you!"
end

function show_progess_indicator --description "Show a progress indicator."
    if type -q fish_right_prompt
        set rplen (string length -v (fish_right_prompt)[-1])
    else
        set rplen 0
    end
    # Move the cursor to the end of the line and insert progress indicator
    tput hpa (math $COLUMNS - $rplen - 2)
    echo -n '⏳'
end

function notify_custom_keybindings --description "Print a message when custom keybindings are used."
    if test -n "$FISH_AI_KEYMAP_1"
        echo "🎹 Using custom keyboard shortcut '$FISH_AI_KEYMAP_1' instead of Ctrl+P."
    end
    if test -n "$FISH_AI_KEYMAP_2"
        echo "🎹 Using custom keyboard shortcut '$FISH_AI_KEYMAP_2' instead of Ctrl+Space."
    end
end
