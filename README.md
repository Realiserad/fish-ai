![Badge with time spent](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Ffish-ai-git-estimate.json)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/Realiserad/fish-ai/codespaces)

# About

`fish-ai` adds AI functionality to [Fish](https://fishshell.com).
It's awesome! I built it to make my life easier, and I hope it will make
yours easier too. Here is the complete sales pitch:

- It can turn a comment into a shell command and vice versa, which means
less time spent
reading manpages, googling and copy-pasting from Stack Overflow. Great
when working with `git`, `kubectl`, `curl` and other tools with loads
of parameters and switches.
- Did you make a typo? It can also fix a broken command (similarly to
[`thefuck`](https://github.com/nvbn/thefuck)).
- Not sure what to type next or just lazy? Let the LLM autocomplete
your commands with a built in fuzzy finder.
- Everything is done using two keyboard shortcuts, no mouse needed!
- It can be hooked up to the LLM of your choice (even a self-hosted one!).
- Everything is open source, hopefully somewhat easy to read and
around 2000 lines of code, which means that you can audit the code
yourself in an afternoon.
- Install and update with ease using [`fisher`](https://github.com/jorgebucaran/fisher).
- Tested on both macOS and the most common Linux distributions.
- Does not interfere with [`fzf.fish`](https://github.com/PatrickF1/fzf.fish),
[`tide`](https://github.com/IlanCosman/tide) or any of the other plugins
you're already using!
- Does not wrap your shell, install telemetry or force you to switch
to a proprietary terminal emulator.

This plugin was originally based on [Tom Dörr's `fish.codex` repository](https://github.com/tom-doerr/codex.fish).
Without Tom, this repository would not exist!

If you like it, please add a ⭐. If you don't like it, create a PR. 😆

## 🎥 Demo

![Demo](https://github.com/user-attachments/assets/86b61223-e568-4152-9e5e-d572b2b1385b)

## 👨‍🔧 How to install

### Install `fish-ai`

Make sure `git` and either [`uv`](https://github.com/astral-sh/uv), or
[a supported version of Python](https://github.com/Realiserad/fish-ai/blob/main/.github/workflows/python-tests.yaml)
along with `pip` and `venv` is installed. Then grab the plugin using
[`fisher`](https://github.com/jorgebucaran/fisher):

```shell
fisher install realiserad/fish-ai
```

### Create a configuration

Create a configuration file `~/.config/fish-ai.ini`.

If you use a self-hosted LLM (behind an OpenAI-compatible API):

```ini
[fish-ai]
configuration = self-hosted

[self-hosted]
provider = self-hosted
server = https://<your server>:<port>/v1
model = <your model>
api_key = <your API key>
```

If you are self-hosting, my recommendation is to use
[Ollama](https://github.com/ollama/ollama) with
[Llama 3.3 70B](https://ollama.com/library/llama3.3). An out of the box
configuration  running on `localhost` could then look something
like this:

```ini
[fish-ai]
configuration = local-llama

[local-llama]
provider = self-hosted
model = llama3.3
server = http://localhost:11434/v1
```

If you use [OpenAI](https://platform.openai.com):

```ini
[fish-ai]
configuration = openai

[openai]
provider = openai
model = gpt-4o
api_key = <your API key>
organization = <your organization>
```

If you use [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service):

```ini
[fish-ai]
configuration = azure

[azure]
provider = azure
server = https://<your instance>.openai.azure.com
model = <your deployment name>
api_key = <your API key>
```

If you use [Hugging Face](https://huggingface.co):

```ini
[fish-ai]
configuration = huggingface

[huggingface]
provider = huggingface
email = <your email>
api_key = <your password>
model = meta-llama/Llama-3.3-70B-Instruct
```

Available models are listed [here](https://huggingface.co/chat/models).
Note that 2FA must be disabled on the account.

If you use [Mistral](https://mistral.ai):

```ini
[fish-ai]
configuration = mistral

[mistral]
provider = mistral
api_key = <your API key>
```

If you use [GitHub Models](https://github.com/marketplace/models):

```ini
[fish-ai]
configuration = github

[github]
provider = self-hosted
server = https://models.inference.ai.azure.com
api_key = <paste GitHub PAT here>
model = gpt-4o-mini
```

You can create a personal access token (PAT) [here](https://github.com/settings/tokens).
The PAT does not require any permissions.

If you use [Anthropic](https://www.anthropic.com):

```ini
[anthropic]
provider = anthropic
api_key = <your API key>
```

If you use [Cohere](https://cohere.com):

```ini
[cohere]
provider = cohere
api_key = <your API key>
```

If you use [DeepSeek](https://www.deepseek.com):

```ini
[deepseek]
provider = deepseek
api_key = <your API key>
model = deepseek-chat
```

### Put the API key on your keyring

Instead of putting the API key in the configuration file, you can let
`fish-ai` load it from your keyring. To save a new API key or transfer
an existing API key to your keyring, run `fish_ai put_api_key`.

## 🙉 How to use

### Transform comments into commands and vice versa

Type a comment (anything starting with `#`), and press **Ctrl + P** to turn it
into shell command! Note that if your comment is very brief or vague, the LLM
may decide to improve the comment instead of providing a shell command. You
then need to press **Ctrl + P** again.

You can also run it in reverse. Type a command and press **Ctrl + P** to turn it
into a comment explaining what the command does.

### Autocomplete commands

Begin typing your command and press **Ctrl + Space** to display a list of
completions in [`fzf`](https://github.com/junegunn/fzf) (it is bundled
with the plugin, no need to install it separately). Completions load in the
background and show up as they become available.

To refine the results, type some instructions and press **Ctrl + P**
inside `fzf`.

### Suggest fixes

If a command fails, you can immediately press **Ctrl + Space** at the command prompt
to let `fish-ai` suggest a fix!

## 🤸 Additional options

You can tweak the behaviour of `fish-ai` by putting additional options in your
`fish-ai.ini` configuration file.

### Explain in a different language

To explain shell commands in a different language, set the `language` option
to the name of the language. For example:

```ini
[fish-ai]
language = Swedish
```

This will only work well if the LLM you are using has been trained on a dataset
with the chosen language.

### Change the temperature

Temperature is a decimal number between 0 and 1 controlling the randomness of
the output. Higher values make the LLM more creative, but may impact accuracy.
The default value is `0.2`.

Here is an example of how to increase the temperature to `0.5`.

```ini
[fish-ai]
temperature = 0.5
```

This option is not supported when using the `huggingface` provider.

Some reasoning models, such as OpenAI's o3, does not support the
temperature parameter, and you need to explicitly disable it by
setting `temperature = None`.

### Number of completions

To change the number of completions suggested by the LLM when pressing
**Ctrl + Space**, set the `completions` option. The default value is `5`.

Here is an example of how you can increase the number of completions to `10`:

```ini
[fish-ai]
completions = 10
```

To change the number of refined completions suggested by the LLM when pressing
**Ctrl + P** in `fzf`, set the `refined_completions` option. The default value
is `3`.

```ini
[fish-ai]
refined_completions = 5
```

### Personalise completions using commandline history

You can personalise completions suggested by the LLM by sending
an excerpt of your commandline history.

To enable it, specify the maximum number of commands from the history
to send to the LLM using the `history_size` option. The default value
is `0` (do not send any commandline history).

```ini
[fish-ai]
history_size = 5
```

If you enable this option, consider the use of [`sponge`](https://github.com/meaningful-ooo/sponge)
to automatically remove broken commands from your commandline history.

### Preview pipes

To send the output of a pipe to the LLM when completing a command, use the
`preview_pipe` option.

```ini
[fish-ai]
preview_pipe = True
```

This will send the output of the longest consecutive pipe after the last
unterminated parenthesis before the cursor. For example, if you autocomplete
`az vm list | jq`, the output from `az vm list` will be sent to the LLM.

This behaviour is disabled by default, as it may slow down the completion
process and lead to commands being executed twice.

## 🎭 Switch between contexts

You can switch between different sections in the configuration using the
`fish_ai_switch_context` command.

## 🐾 Data privacy

When using the plugin, `fish-ai` submits the name of your OS and the
commandline buffer to the LLM.

When you codify or complete a command, it also sends the contents of any
files you mention (as long as the file is readable), and when you explain
or complete a command, the output from `<command> --help` is provided to
the LLM for reference.

`fish-ai` can also send an excerpt of your commandline history
when completing a command. This is disabled by default.

Finally, to fix the previous command, the previous commandline buffer,
along with any terminal output and the corresponding exit code is sent
to the LLM.

If you are concerned with data privacy, you should use a self-hosted
LLM. When hosted locally, no data ever leaves your machine.

### Redaction of sensitive information

The plugin attempts to redact sensitive information from the prompt
before submitting it to the LLM. Sensitive information is replaced by
the `<REDACTED>` placeholder.

The following information is redacted:

- Passwords and API keys supplied on the commandline.
- Base64 encoded data in single or double quotes.
- PEM-encoded private keys.

## 🔨 Development

If you want to contribute, I recommend to read [`ARCHITECTURE.md`](https://github.com/Realiserad/fish-ai/blob/main/ARCHITECTURE.md)
first.

This repository ships with a `devcontainer.json` which can be used with
GitHub Codespaces or Visual Studio Code with
[the Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

To install `fish-ai` from a local copy, use `fisher`:

```shell
fisher install .
```

### Enable debug logging

Enable debug logging by putting `debug = True` in your `fish-ai.ini`.
Logging is done to syslog by default (if available). You can also enable
logging to file using `log = <path to file>`, for example:

```ini
[fish-ai]
debug = True
log = ~/.fish-ai/log.txt
```

### Run the tests

[The installation tests](https://github.com/Realiserad/fish-ai/actions/workflows/installation-tests.yaml)
are packaged into containers and can be executed locally with e.g. `docker`.

```shell
docker build -f tests/ubuntu/Dockerfile .
docker build -f tests/fedora/Dockerfile .
docker build -f tests/archlinux/Dockerfile .
```

The Python modules containing most of the business logic can be tested using
`pytest`.

### Create a release

A release is created by GitHub Actions when a new tag is pushed.

```shell
set tag (grep '^version =' pyproject.toml | \
    cut -d '=' -f2- | \
    string replace -ra '[ "]' '')
git tag -a "v$tag" -m "🚀 v$tag"
git push origin "v$tag"
```
