<h1 align="center">⌨️ 🦾  codex.fish 🐟</h1>

<p align="center">
    AI in the command line.
</p>

<p align="center">
    <a href="https://github.com/tom-doerr/codex.fish/stargazers"
        ><img
            src="https://img.shields.io/github/stars/tom-doerr/codex.fish?colorA=2c2837&colorB=c9cbff&style=for-the-badge&logo=starship style=flat-square"
            alt="Repository's starts"
    /></a>
    <a href="https://github.com/tom-doerr/codex.fish/issues"
        ><img
            src="https://img.shields.io/github/issues-raw/tom-doerr/codex.fish?colorA=2c2837&colorB=f2cdcd&style=for-the-badge&logo=starship style=flat-square"
            alt="Issues"
    /></a>
    <a href="https://github.com/tom-doerr/codex.fish/blob/main/LICENSE"
        ><img
            src="https://img.shields.io/github/license/tom-doerr/codex.fish?colorA=2c2837&colorB=b5e8e0&style=for-the-badge&logo=starship style=flat-square"
            alt="License"
    /><br />
    <a href="https://github.com/tom-doerr/codex.fish/commits/main"
		><img
			src="https://img.shields.io/github/last-commit/tom-doerr/codex.fish/main?colorA=2c2837&colorB=ddb6f2&style=for-the-badge&logo=starship style=flat-square"
			alt="Latest commit"
    /></a>
    <a href="https://github.com/tom-doerr/codex.fish"
        ><img
            src="https://img.shields.io/github/repo-size/tom-doerr/codex.fish?colorA=2c2837&colorB=89DCEB&style=for-the-badge&logo=starship style=flat-square"
            alt="GitHub repository size"
    /></a>
</p>

## What is it?

This is a fish plugin that enables you to use OpenAI's powerful Codex AI in the command line. OpenAI Codex is the AI that also powers GitHub Copilot.
To use this plugin you need to get access to OpenAI's [Codex API](https://openai.com/blog/openai-codex/).


## How do I install it?
1. Install the OpenAI package.
```
pip3 install openai
```

2. Install the plugin itself.
You can install it using [fisher](https://github.com/jorgebucaran/fisher):
```
fisher install tom-doerr/codex.fish
```

3. Create a file called `openaiapirc` in `~/.config` with your ORGANIZATION_ID and SECRET_KEY.

```
[openai]
organization_id = ...
secret_key = ...
```

4. Run `fish`, start typing and complete it using `^X`!

---

[ZSH version](https://github.com/tom-doerr/zsh_codex)
