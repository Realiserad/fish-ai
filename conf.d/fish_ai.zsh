##
## Supported major.minor versions of Python.
## Unit tests are run in CI against these versions.
##
supported_versions=(3.9 3.10 3.11 3.12 3.13)

##
## This section contains the keybindings for fish-ai. If you want to change the
## default keybindings, use the environment variables:
##
##   - FISH_AI_KEYMAP_1 (defaults to Ctrl + P)
##   - FISH_AI_KEYMAP_2 (defaults to Ctrl + Space)
##
## These should be set to the key binding escape sequence for a keyboard shortcut
## you want to use + any flags. You can get the key binding escape sequence using
## the command `bindkey -M viins`.
##
if [[ -n "$FISH_AI_KEYMAP_1" ]]; then
    keymap_1="$FISH_AI_KEYMAP_1"
else
    keymap_1="^P"
fi

if [[ -n "$FISH_AI_KEYMAP_2" ]]; then
    keymap_2="$FISH_AI_KEYMAP_2"
else
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS
        keymap_2="^@"
    else
        # Linux
        keymap_2="^@"
    fi
fi

if [[ "$KEYMAP" == "viins" ]]; then
    bind_command="bindkey -M viins"
else
    bind_command="bindkey"
fi

$bind_command "$keymap_1" _fish_ai_codify_or_explain
$bind_command "$keymap_2" _fish_ai_autocomplete_or_fix

##
## This section contains the plugin lifecycle hooks invoked by the fisher package
## manager.
##
function _fish_ai_install {
    set_python_version
    if command -v uv &> /dev/null; then
        echo "🥡 Setting up a virtual environment using uv..."
        uv venv --seed --python "$python_version" ~/.fish-ai
    else
        echo "🥡 Setting up a virtual environment using venv..."
        python"$python_version" -m venv ~/.fish-ai
    fi

    if [[ $? -ne 0 ]]; then
        echo "💔 Installation failed. Check previous terminal output for details."
        return 1
    fi

    echo "🍬 Installing dependencies. This may take a few seconds..."
    ~/.fish-ai/bin/pip -qq install "$(get_installation_url)"
    if [[ $? -ne 0 ]]; then
        echo "💔 Installation from '$(get_installation_url)' failed. Check previous terminal output for details."
        return 2
    fi

    python_version_check
    notify_custom_keybindings
    symlink_truststore
    autoconfig_gh_models

    if [[ ! -f ~/.config/fish-ai.ini ]]; then
        echo "🤗 You must create a configuration file before the plugin can be used!"
    fi
}

function _fish_ai_update {
    set_python_version
    if command -v uv &> /dev/null; then
        uv venv --seed --python "$python_version" ~/.fish-ai
    else
        python"$python_version" -m venv --upgrade ~/.fish-ai
    fi

    if [[ $? -ne 0 ]]; then
        echo "💔 Installation failed. Check previous terminal output for details."
        return 1
    fi

    echo "🐍 Now using $(~/.fish-ai/bin/python3 --version)."
    echo "🍬 Upgrading dependencies. This may take a few seconds..."
    ~/.fish-ai/bin/pip install -qq --upgrade "$(get_installation_url)"
    if [[ $? -ne 0 ]]; then
        echo "💔 Installation failed. Check previous terminal output for details."
        return 2
    fi

    python_version_check
    notify_custom_keybindings
    symlink_truststore
    warn_plaintext_api_keys
}

function _fish_ai_uninstall {
    if [[ -d ~/.fish-ai ]]; then
        echo "💣 Nuking the virtual environment..."
        rm -r ~/.fish-ai
    fi
}

function set_python_version {
    if [[ -n "$FISH_AI_PYTHON_VERSION" ]]; then
        echo "🐍 Using Python $FISH_AI_PYTHON_VERSION as specified by the environment variable 'FISH_AI_PYTHON_VERSION'."
        python_version="$FISH_AI_PYTHON_VERSION"
    elif command -v uv &> /dev/null; then
        # Use the last supported version of Python
        python_version="${supported_versions[-1]}"
    else
        # Use the Python version provided by the system
        python_version=3
    fi
}

function get_installation_url {
    plugin=$(fisher list "fish-ai")
    if [[ -z "$plugin" ]]; then
        # fish-ai may be installed from an unknown source, assume
        # that the Python packages can be installed from the
        # current working directory.
        echo -n "$(pwd)"
    elif [[ "${plugin:0:1}" == "/" ]]; then
        # Install from a local folder (most likely a git clone)
        echo -n "$plugin"
    else
        # Install from GitHub
        echo -n "fish-ai@git+https://github.com/$plugin"
    fi
}

function python_version_check {
    python_version=$(~/.fish-ai/bin/python3 -c 'import platform; major, minor, _ = platform.python_version_tuple(); print(major, end="."); print(minor, end="")')
    if [[ ! " ${supported_versions[@]} " =~ " ${python_version} " ]]; then
        echo "🔔 This plugin has not been tested with Python $python_version and may not function correctly."
        echo "The following versions are supported: ${supported_versions[*]}"
        echo "Consider setting the environment variable 'FISH_AI_PYTHON_VERSION' to a supported version and reinstalling the plugin. For example:"
        echo -e "\e[3;34m"
        echo ""
        echo "  fisher remove realiserad/fish-ai"
        echo "  export FISH_AI_PYTHON_VERSION=${supported_versions[-1]}"
        echo "  fisher install realiserad/fish-ai"
        echo ""
        echo -e "\e[0m"
    fi
}

function symlink_truststore {
    if [[ -f /etc/ssl/certs/ca-certificates.crt ]]; then
        echo "🔑 Symlinking to certificates stored in /etc/ssl/certs/ca-certificates.crt."
        ln -snf /etc/ssl/certs/ca-certificates.crt $(~/.fish-ai/bin/python3 -c 'import certifi; print(certifi.where())')
    elif [[ -f /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem ]]; then
        echo "🔑 Symlinking to certificates stored in /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem."
        ln -snf /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem $(~/.fish-ai/bin/python3 -c 'import certifi; print(certifi.where())')
    elif [[ -f /etc/ssl/cert.pem ]]; then
        echo "🔑 Symlinking to certificates stored in /etc/ssl/cert.pem."
        ln -snf /etc/ssl/cert.pem $(~/.fish-ai/bin/python3 -c 'import certifi; print(certifi.where())')
    fi
}

function warn_plaintext_api_keys {
    if grep -q "^api_key" ~/.config/fish-ai.ini; then
        echo -n "🚨 One or more plaintext API keys are stored in "
        echo -n -e "\e[1;31m~/.config/fish-ai.ini\e[0m"
        echo -n ". Consider moving them to your keyring using "
        echo -n -e "\e[3;34mfish_ai_put_api_key\e[0m"
        echo "."
    fi
}

function autoconfig_gh_models {
    if [[ -f ~/.config/fish-ai.ini ]]; then
        return
    fi
    if ! command -v gh &> /dev/null; then
        return
    fi
    if [[ -z "$(gh auth token 2>/dev/null)" ]]; then
        return
    fi
    if [[ -z "$(gh ext ls | grep "gh models" 2>/dev/null)" ]]; then
        return
    fi

    echo "[fish-ai]" >> ~/.config/fish-ai.ini
    echo "configuration = github" >> ~/.config/fish-ai.ini
    echo "" >> ~/.config/fish-ai.ini
    echo "[github]" >> ~/.config/fish-ai.ini
    echo "provider = self-hosted" >> ~/.config/fish-ai.ini
    echo "server = https://models.inference.ai.azure.com" >> ~/.config/fish-ai.ini
    echo "api_key = $(gh auth token)" >> ~/.config/fish-ai.ini
    echo "model = gpt-4o-mini" >> ~/.config/fish-ai.ini

    echo "😺 Access to GitHub Models has been automatically configured for you!"
}

function show_progess_indicator {
    if command -v zle &> /dev/null; then
        zle -I
    fi
    echo -n '⏳'
}

function notify_custom_keybindings {
    if [[ -n "$FISH_AI_KEYMAP_1" ]]; then
        echo "🎹 Using custom keyboard shortcut '$FISH_AI_KEYMAP_1' instead of Ctrl+P."
    fi
    if [[ -n "$FISH_AI_KEYMAP_2" ]]; then
        echo "🎹 Using custom keyboard shortcut '$FISH_AI_KEYMAP_2' instead of Ctrl+Space."
    fi
}
