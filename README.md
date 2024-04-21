![Badge with time spent](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Ffish-ai-git-estimate.json)

# About

`fish-ai` adds AI functionality to [Fish shell](https://fishshell.com). It
should run on any system with Python installed.

Originally based on [Tom Dörr's `fish.codex` repository](https://github.com/tom-doerr/codex.fish),
but with some additional functionality. It uses the [`generateContent`](https://ai.google.dev/api/rest/v1/models/generateContent)
or
[chat completions API endpoint](https://platform.openai.com/docs/api-reference/chat/create)
and can be hooked up to Google, OpenAI, Azure OpenAI
or a self-hosted LLM behind any OpenAI-compatible API.

Continuous integration is performed against Azure OpenAI.

If you like it, please add a ⭐.

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
[Llama 3 70B](https://ollama.com/library/llama3). An out of the box
configuration  running on `localhost` could then look something like this:

```ini
[fish-ai]
configuration = local-llama

[local-llama]
provider = self-hosted
server = http://localhost:11434/v1
```

If you use [OpenAI](https://platform.openai.com/login):

```ini
[fish-ai]
configuration = openai

[openai]
provider = openai
model = gpt-4-turbo
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

### Install `fish-ai`

Install the plugin. You can install it using [`fisher`](https://github.com/jorgebucaran/fisher).

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

## 🤸 Additional options

You can tweak the behaviour of `fish-ai` by putting additional options in the
active section of your `fish-ai.ini` file.

### Explain in a different language

To explain shell commands in a different language, set the `language` option
to the name of the language. For example:

```ini
[fish-ai]
configuration = foo

[foo]
language = Swedish
```

### Change the temperature

Temperature is a decimal number between 0 and 1 controlling the randomness of
the output. Higher values make the LLM more creative, but may impact accuracy.
The default value is `0.2`.

Here is an example of how to increase the temperature to `0.5`.

```ini
[fish-ai]
configuration = foo

[foo]
temperature = 0.5
```

### Switch between contexts

You can switch between different sections in the configuration using the
`fish_ai_switch_context` command.

## 🐾 Data privacy

When using the plugin, `fish-ai` submits the name of your OS and the
commandline buffer to the LLM. When you codify a command, it also
sends the contents of any files you mention (as long as the file is
readable).

Finally, to fix the previous command, the previous commandline buffer,
along with any terminal output and the corresponding exit code is sent
to the LLM.

If you are concerned with data privacy, you should use a self-hosted
LLM. When hosted locally, no data ever leaves your machine.

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
configuration = foo

[foo]
debug = True
log = ~/.fish-ai/log.txt
```

### Run the tests

[The tests](https://github.com/Realiserad/fish-ai/actions/workflows/test-tapes.yaml)
are packaged into a container and can be executed locally with e.g. `docker`.

```shell
cp ~/.config/fish-ai.ini tests/azure-openai
docker build -f tests/azure-openai/Dockerfile .
```
