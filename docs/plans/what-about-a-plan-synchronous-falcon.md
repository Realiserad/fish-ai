# Plan: fish history context for `Ctrl+P` codify

## Context

`Ctrl+P` on a `# comment` (codify: comment -> fish command) sends only the comment plus a fixed prompt
(`src/fish_ai/codify.py`). The model never sees how the user actually writes commands (preferred flags,
tools, aliases). `Ctrl+Space` autocomplete already solves this with opt-in history
(`engine.get_commandline_history`, `history_size`), but it searches `history search --prefix <first word>`,
which cannot work for a comment because a comment has no command name.

Outcome: when `history_size > 0`, codify adds earlier history entries that match keywords from the comment
to the system prompt, so output follows the user's own habits.

## Decisions (user)

- Applies to `Ctrl+P` codify only.
- Entries chosen by **keyword match** from the comment, via fish `history search`.
- **Reuse `history_size`** (default `0` = off). No new config key.

## Decisions (my calls, flagged for review)

- Explain (`Ctrl+P` on a non-comment), fix, and autocomplete are unchanged.
- One `history search` per keyword. Verified on fish 4.9.3: `history search git status` matches only the first
  term, so terms cannot be combined in one call.
- Keywords: lowercase `[A-Za-z0-9_.-]+` tokens, length >= 3, minus a small inline stopword set, deduped in order,
  capped at 5.
- Merge in Python: entries matching more keywords rank first, ties broken by recency (first-seen order); return
  at most `history_size` entries.
- Pass keywords to fish as argv (`fish -c '<fixed script>' -- <n> <kw>`), never string-interpolated. The existing
  `get_commandline_history` interpolates into a double-quoted fish string; leave it alone, out of scope.
- When history is off or nothing matches, the codify prompt is byte-identical to today (append the section only
  when there are entries). Autocomplete's "No commandline history available." placeholder is not reused.
- Redaction: history rides in the system message, so the existing `redact()` in `engine.get_response` covers it.
  Known gaps (env assignments such as `TOKEN=x cmd`, short flags, URL credentials) are NOT fixed here; call out
  in README. Separate follow-up.

## Changes

1. `src/fish_ai/engine.py`
   - Add `get_keywords(text)` (pure, unit-testable) and `get_keyword_history(text)` returning `list[str]`
     (`[]` when `history_size` is `0` or nothing matches). Reuse `get_config("history_size")`, `get_logger`, and
     the `Popen`/`subprocess` imports already used by `get_commandline_history` (`engine.py:109`).
2. `src/fish_ai/codify.py`
   - In `get_instructions`, after building the system message, if `engine.get_keyword_history(commandline)` is
     non-empty append a paragraph: "You may use the following commandline history to match the user's preferred
     tools and flags:" plus the entries, one per line. Pattern mirrors `autocomplete.py:30`.
3. Tests (`src/fish_ai/tests/`)
   - `engine_test.py`: `get_keywords` (stopwords, short words, dedupe, cap); `get_keyword_history` disabled ->
     `[]`; ranking/dedupe/cap with `subprocess` patched; no matches -> `[]`.
   - `codify_test.py`: with `get_keyword_history` patched to entries, system message contains them; patched to
     `[]`, system message has no history section.
4. `README.md`
   - Extend "Personalise completions using commandline history" (line ~411): `history_size` also feeds
     `Ctrl+P` on comments, matched by keyword.
   - Update the data-privacy paragraph (line ~484) to mention codify.
   - One line noting redaction limits for history (env assignments, short flags, URL credentials).

## Reuse

- `engine.get_config`, `engine.get_logger`, `engine.get_messages`, `engine.get_response` (redaction),
  `engine.get_commandline_history` as the structural reference.
- Test style: `@patch("fish_ai.engine.get_config")` as in `engine_test.py:32`; `@patch("fish_ai.engine.get_args", ...)`
  as in `codify_test.py`.

## Process

- Per the user's worktree rule, implement in a worktree (e.g. `git worktree add ../fish-ai-codify-history`),
  not the `main` checkout. Run tests there.

## Verification

1. `pytest src/fish_ai/tests` (project uses `pytest`; lint/format via the repo's `prek.toml`).
2. Manual: set `history_size = 5` and `debug = True` in `~/.config/fish-ai.ini`; in fish run
   `history search --max 3 docker`, then press `Ctrl+P` on `# remove all stopped docker containers`; confirm in
   the fish-ai log that the system prompt contains a history section with docker entries.
3. Manual: set `history_size = 0`; confirm the codify prompt has no history section.
4. Confirm `Ctrl+Space` autocomplete behaviour is unchanged.
