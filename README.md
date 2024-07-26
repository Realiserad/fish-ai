![Badge with time spent](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Ffish-ai-git-estimate.json)

# About

`fish-ai` adds AI functionality to [Fish](https://fishshell.com). It
has been tested with macOS and Linux, but should run on any system where
Python and git is installed.

Originally based on [Tom Dörr's `fish.codex` repository](https://github.com/tom-doerr/codex.fish),
but with some additional functionality.

It can be hooked up to OpenAI, Azure OpenAI, Google, Hugging Face, Mistral or a
self-hosted LLM behind any OpenAI-compatible API.

If you like it, please add a ⭐. If you don't like it, create a PR. 😆

## 🎥 Demo

![demo](https://github.com/Realiserad/fish-ai/assets/6617918/49d8a959-8f6c-48d8-b788-93c560617c28)

## 👨‍🔧 How to install

### Create a configuration

Create a configuration file `~/.config/fish-ai.ini`.

If you use a self-hosted LLM:

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
[Llama 3.1 70B](https://ollama.com/library/llama3.1). An out of the box
configuration  running on `localhost` could then look something
like this:

```ini
[fish-ai]
configuration = local-llama

[local-llama]
provider = self-hosted
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

If you use [Gemini](https://ai.google.dev):

```ini
[fish-ai]
configuration = gemini

[gemini]
provider = google
api_key = <your API key>
```

If you use [Hugging Face](https://huggingface.co):

```ini
[fish-ai]
configuration = huggingface

[huggingface]
provider = huggingface
email = <your email>
password = <your password>
model = meta-llama/Meta-Llama-3.1-405B-Instruct-FP8
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

### Install `fish-ai`

Install the plugin. You can install it using [`fisher`](https://github.com/jorgebucaran/fisher).

```shell
fisher install realiserad/fish-ai
```

## 🙉 How to use

### Transform comments into commands and vice versa

Type a comment (anything starting with `#`), and press **Ctrl + P** to turn it
into shell command!

You can also run it in reverse. Type a command and press **Ctrl + P** to turn it
into a comment explaining what the command does.

### Autocomplete commands

Begin typing your command and press **Ctrl + Space** to display a list of
completions in [`fzf`](https://github.com/junegunn/fzf) (it is bundled
with the plugin, no need to install it separately). Completions load in the
background and show up as they become available.

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

### Number of completions

To change the number of completions suggested by the LLM when pressing
**Ctrl + Space**, set the `completions` option. The default value is `5`.

Here is an example of how you can increase the number of completions to `10`:

```ini
[fish-ai]
completions = 10
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

## 🎭 Switch between contexts

You can switch between different sections in the configuration using the
`fish_ai_switch_context` command.

## 🐾 Data privacy

When using the plugin, `fish-ai` submits the name of your OS and the
commandline buffer to the LLM.

When you codify a command, it also sends the contents of any files you
mention (as long as the file is readable), and when you explain or
autocomplete a command, the the ouput from `<command> --help` is provided
to the LLM for reference.

`fish-ai` can also send an exerpt of your commandline history
when autocompleting a command. This is disabled by default.

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
docker build -f tests/ubuntu-22/Dockerfile .
docker build -f tests/fedora-40/Dockerfile .
docker build -f tests/archlinux-base/Dockerfile .
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
