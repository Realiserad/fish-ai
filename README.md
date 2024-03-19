![Badge with time spent](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Ffish-ai-git-estimate.json)

# About

`fish-ai` adds AI functionality to [Fish shell](https://fishshell.com).

Originally based on [Tom Dörr's `fish.codex` repository](https://github.com/tom-doerr/codex.fish)
which is now outdated, this repository uses the [chat completions API endpoint](https://platform.openai.com/docs/api-reference/chat/create)
and can be hooked up to OpenAI, Azure OpenAI or a self-hosted LLM behind any
OpenAI-compatible API.

Continuous integration is performed against Azure OpenAI.

If you like it, please add a ⭐.

## 🎥 Demo

![demo](https://github.com/Realiserad/fish-ai/assets/6617918/14584dc9-f47d-45ca-93a3-c650301b7d99)

## 👨‍🔧 How to install

### Create a configuration

Create a configuration file called `.config/fish-ai.ini`.

If you use [a self-hosted LLM](https://github.com/ollama/ollama), e.g. [`codellama`](https://ollama.com/library/codellama):

```ini
[fish-ai]
configuraton = self-hosted

[self-hosted]
provider = self-hosted
server = http://localhost:11434/v1
model = codellama
```

If you use [OpenAI](https://platform.openai.com/login):

```ini
[fish-ai]
configuration = openai

[openai]
model = gpt-3.5-turbo
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

### Install `openai`

Install the `openai` Python package.

```shell
python3 -m pip install -U openai
```

### Install `fish-ai`

Install the plugin itself. You can install it using [`fisher`](https://github.com/jorgebucaran/fisher).

```shell
fisher install realiserad/fish-ai@stable
```

## 🙉 How to use

### Transform comments into commands and vice versa

Type a comment (anything starting with `#`), and press **Ctrl + P** to turn it
into shell command!

You can also run it in reverse. Type a command and press **Ctrl + P** to turn it
into a comment explaining what the command does.

### Autocomplete commands

Begin typing your command and press **Ctrl + Space** to autocomplete at the cursor
position.

### Suggest fixes

If a command fails, you can immediately press **Ctrl + Space** at the command prompt
to let `fish-ai` suggest a fix!

## 🔨 Development

Clone the code and install directly from the repository using `fisher`.

```shell
git clone git@github.com:Realiserad/fish-ai.git
fisher install .
```

### Install the hooks

This repository ships with [pre-commit hooks](https://pre-commit.com) which can
prevent some faulty commits from being pushed.

### Enable debug logging

Enable debug logging to syslog by putting `debug = True` in your `fish-ai.ini`.

### Run the tests

[The tests](https://github.com/Realiserad/fish-ai/actions/workflows/test-tapes.yaml)
are packaged into a container and can be executed locally with e.g. `docker`.

```shell
cp ~/.config/fish-ai.ini tests/azure-openai
docker build -f tests/azure-openai/Dockerfile .
```
