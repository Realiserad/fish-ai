# Development

If you want to contribute, I recommend to read [`ARCHITECTURE.md`](https://github.com/Realiserad/fish-ai/blob/main/ARCHITECTURE.md)
first.

This repository ships with a `devcontainer.json` which can be used with
GitHub Codespaces or Visual Studio Code with
[the Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

To install `fish-ai` from a local copy, use `fisher`:

```shell
fisher install .
```

## Enable debug logging

Enable debug logging by putting `debug = True` in your `fish-ai.ini`.
Logging is done to syslog by default (if available). You can also enable
logging to file using `log = <path to file>`, for example:

```ini
[fish-ai]
debug = True
log = /tmp/fish-ai.log
```

## Run the tests

[The installation tests](https://github.com/Realiserad/fish-ai/actions/workflows/installation-tests.yaml)
are currently running with GitHub Actions on macOS, Fedora, Ubuntu and Arch Linux.

The Python modules containing most of the business logic can be tested using `pytest`.

## Write commit messages

Use [conventional commits](https://www.conventionalcommits.org) when writing
commit messages. This repository uses tooling which relies on the conventional
commits specification for incrementing the version number and compute changelogs.

## Create a release

A release is created by GitHub Actions when a new tag is pushed.

```shell
set tag (grep '^version =' pyproject.toml | \
    cut -d '=' -f2- | \
    string replace -ra '[ "]' '')
git tag -a "v$tag" -m "🚀 v$tag"
git push origin "v$tag"
```
