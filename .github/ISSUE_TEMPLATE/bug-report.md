---
name: Bug report
about: Report something which is not working as expected
title: "fix: description of the bug"
labels: type/bug
assignees: Realiserad
---

**📝 Environment**

1. Operating system

```shell
> cat /etc/os-release | grep PRETTY
<paste output here>
```

2. Version of `fish`

```shell
> fish --version
<paste output here>
```

3. Version of `openai`

```shell
> openai --version
<paste output here>
```

4. Version of `python`

```shell
> python3 --version
<paste output here>
```

5. `fish-ai` configuration

```shell
> sed '/api_key/d' ~/.config/fish-ai.ini
<paste output here>
```

**🙉 To reproduce**

Follow these steps to reproduce the bug.

1. Open the terminal `put name of terminal`.

2. Type the following:

```shell
<paste command here>
```

3. Press `put keyboard combination`.

4. *Describe what happens*

**🕊 Expected behavior**

A clear and concise description of what you expected to happen.

**🖥 Log output (optional)**

```shell
> journalctl -f | grep --line-buffered 'python3'
<paste relevant log lines here>
```
