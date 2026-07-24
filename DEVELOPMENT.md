# Development

If you want to contribute, I recommend reading [`ARCHITECTURE.md`](https://github.com/Realiserad/fish-ai/blob/main/ARCHITECTURE.md)
first.

There are some hardcoded references in this GitHub repository that you
may want to erase using `ops/fork.fish` if you decide to maintain your
own fork.

To create a virtual environment with the tools needed for development,
simply run `uv sync`. When using an editor such as Zed, everything should
work out of the box.

To install `fish-ai` from a local copy, use `fisher`:

```shell
fisher install .
```

## Install the pre-commit hooks

To install the pre-commit hooks, use [prek](https://prek.j178.dev/installation):

```shell
prek install --hook-type pre-commit --hook-type commit-msg --hook-type post-commit
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
commits specification for incrementing the version number and computing changelogs.

## Create a release

A release is created by GitHub Actions when a new tag is pushed.

```shell
set tag (grep '^version =' pyproject.toml | \
    cut -d '=' -f2- | \
    string replace -ra '[ "]' '')
git tag -a "v$tag" -m "🚀 v$tag"
git push origin "v$tag"
```
