##
## Supported major.minor versions of Python.
## Unit tests are run in CI against these versions.
##
set -g supported_versions 3.9 3.10 3.11 3.12 3.13

function get_install_dir
    if test -z "$XDG_DATA_HOME"
        echo "$HOME/.local/share/fish-ai"
    else
        echo "$XDG_DATA_HOME/fish-ai"
    end
end

function get_config_path
    if test -z "$XDG_DATA_HOME"
        echo "$HOME/.config/fish-ai.ini"
    else
        echo "$XDG_CONFIG_HOME/fish-ai.ini"
    end
end

set -g install_dir (get_install_dir)
set -g config_path (get_config_path)

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
        uv venv --seed --python $python_version "$install_dir"
    else
        echo "🥡 Setting up a virtual environment using venv..."
        python$python_version -m venv "$install_dir"
    end
    if test $status -ne 0
        echo "💔 Installation failed. Check previous terminal output for details."
        return 1
    end

    echo "🍬 Installing dependencies. This may take a few seconds..."
    "$install_dir/bin/pip" -qq install "$(get_installation_url)"
    if test $status -ne 0
        echo "💔 Installation from '$(get_installation_url)' failed. Check previous terminal output for details."
        return 2
    end
    python_version_check
    notify_custom_keybindings
    symlink_truststore
    autoconfig_gh_models
    if ! test -f "$(get_config_path)"
        echo "🤗 You must create a configuration file before the plugin can be used!"
    end
end

function _fish_ai_update --on-event fish_ai_update
    # Upgrade to fish-ai 1.9.0
    if test -d "$HOME/.fish-ai"
        echo "👷 Moving installation directory to '$install_dir'."
        mv "$HOME/.fish-ai" "$install_dir"
    end
    if test -f "$HOME/.config/fish-ai.ini"
        echo "👷 Moving configuration file to '$config_path'."
        mv -u "$HOME/.config/fish-ai.ini" "$config_path"
    end

    set_python_version
    if type -q uv
        uv venv --seed --python $python_version "$install_dir"
    else
        python$python_version -m venv --upgrade "$install_dir"
    end
    if test $status -ne 0
        echo "💔 Installation failed. Check previous terminal output for details."
        return 1
    end

    echo "🐍 Now using $($install_dir/bin/python3 --version)."
    echo "🍬 Upgrading dependencies. This may take a few seconds..."
    $install_dir/bin/pip install -qq --upgrade "$(get_installation_url)"
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
    if test -d "$install_dir"
        echo "💣 Nuking the virtual environment..."
        rm -r "$install_dir"
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
    set python_version ("$install_dir/bin/python3" -c 'import platform; major, minor, _ = platform.python_version_tuple(); print(major, end="."); print(minor, end="")')
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
        ln -snf /etc/ssl/certs/ca-certificates.crt ("$install_dir/bin/python3" -c 'import certifi; print(certifi.where())')
    else if test -f /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
        echo "🔑 Symlinking to certificates stored in /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem."
        ln -snf /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem ("$install_dir/bin/python3" -c 'import certifi; print(certifi.where())')
    else if test -f /etc/ssl/cert.pem
        echo "🔑 Symlinking to certificates stored in /etc/ssl/cert.pem."
        ln -snf /etc/ssl/cert.pem ("$install_dir/bin/python3" -c 'import certifi; print(certifi.where())')
    end
end

function warn_plaintext_api_keys --description "Warn about plaintext API keys."
    if ! test -f "$config_path"
        return
    end
    if grep -q "^api_key" "$config_path"
        echo -n "🚨 One or more plaintext API keys are stored in "
        set_color --bold red
        echo -n "$config_path"
        set_color normal
        echo -n ". Consider moving them to your keyring using "
        set_color --italics blue
        echo -n fish_ai_put_api_key
        set_color normal
        echo "."
    end
end

function autoconfig_gh_models --description "Deploy configuration for GitHub Models."
    if test -f "$config_path"
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
    echo "[fish-ai]" >>"$config_path"
    echo "configuration = github" >>"$config_path"
    echo "" >>"$config_path"
    echo "[github]" >>"$config_path"
    echo "provider = self-hosted" >>"$config_path"
    echo "server = https://models.inference.ai.azure.com" >>"$config_path"
    echo "api_key = $(gh auth token)" >>"$config_path"
    echo "model = gpt-4o-mini" >>"$config_path"

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
