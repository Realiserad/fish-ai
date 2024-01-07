# About

`fish-ai` adds AI functionality to [Fish shell](https://fishshell.com).

Originally based on [Tom Dörr's `fish.codex` repository](https://github.com/tom-doerr/codex.fish) which
is now outdated, this repository uses the [chat completions API endpoint](https://platform.openai.com/docs/api-reference/chat/create)
and can be hooked up to a self-hosted LLM behind any OpenAI-compatible API. It has been optimised against
[Llama GPT](https://github.com/getumbrel/llama-gpt) but should work with other capable LLMs as well.

If you like it, please add a ⭐.

## How to install

1. Create a configuration file called `.config/fish-ai.ini`. It should look something like this:

```ini
[fish-ai]
server = https://your-server/v1
api_key = sk-XXXXXXXXXXXX
model = code-llama-13b-chat.gguf
```

2. Install the OpenAI package.

```shell
pip3 install openai
```

3. Install the plugin itself. You can install it using [fisher](https://github.com/jorgebucaran/fisher).

```shell
fisher install realiserad/fish-ai
```

## How to use

### Transform comments into commands and vice versa

Type a comment (anything starting with `# `), and press **Ctrl + P** to turn it into shell command!

You can also run it in reverse. Type a command and press **Ctrl + P** to turn it into a comment explaining what the
command does.

### Autocomplete commands

Begin typing your command and press **Ctrl + Space** to autocomplete at the cursor position.