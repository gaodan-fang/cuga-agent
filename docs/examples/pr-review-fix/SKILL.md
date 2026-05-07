---
name: pr-review-fix
description: Reads inline review comments and top-level PR comments, then replies to each with either a text answer or a GitHub suggestion block that the reviewer can one-click commit. Does not push commits directly.
---

## Goal

When invoked on a PR, read the review feedback and respond to it. For each
comment you address:

- If it's a question or discussion → reply with a short text answer.
- If it's a concrete code change request → reply with a `suggestion` block so
  GitHub shows a "Commit suggestion" button. The reviewer applies the fix with
  one click; cuga never writes to the repo itself.

## Available tools

- `run_command` — execute shell commands (use for `gh` CLI)
- `read_file` — read a file's full contents (use to ground your suggestions in the actual code)
- `write_file` — available but **must not be used** in this skill (no direct edits)
- `list_files` — available but rarely needed

## Inputs already provided in the environment

- `PR_NUMBER` — the PR this run is handling
- `TRIGGER_COMMENT_AUTHOR` — the author of the comment that woke cuga up
- `TRIGGER_COMMENT_BODY` — the full text of that comment
- `GITHUB_TOKEN` / `GITHUB_REPOSITORY` — standard Actions values

## Workflow

### Step 1: Resolve OWNER and REPO

```
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name -q .name)
```

The `run_command` tool returns plain stdout on exit 0, so the result of these
commands can be interpolated directly into later commands.

### Step 2: Check out the PR branch

```
gh pr checkout $PR_NUMBER
```

This lets `read_file` reach the PR's version of the code.

### Step 3: Fetch the comment sources

Three endpoints, because review feedback can live in any of them:

```
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments          # inline diff comments (line-level)
gh api repos/$OWNER/$REPO/issues/$PR_NUMBER/comments         # top-level PR conversation
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews           # review bodies (CodeRabbit summaries land here)
```

Parse each as JSON. An empty body or non-JSON response should be treated as an
empty list, not an error.

### Step 4: Decide which comments to address

Pick the set of comments to respond to in this run:

1. Always address the triggering comment (`TRIGGER_COMMENT_BODY` from env) — it
   is the reason this run exists. If it is the literal arming text `/cuga` or
   `/cuga stop`, skip it (no reply needed; the workflow already handles arming).
2. Additionally address any **inline review comment** from a non-cuga author
   that does not yet have a reply authored by cuga or `github-actions[bot]`.
3. Skip anything authored by cuga itself or by `github-actions[bot]`.

Cap at five comments per run to keep responses focused.

### Step 5: Compose each reply

For each selected comment, pick one of two reply shapes.

**Text reply.** Use this when the comment is a question, discussion, or
acknowledgement. Keep it to 1–3 sentences. Prefix with `@<author>` so the
commenter gets a notification.

**Suggestion block.** Use this when the comment points at specific lines and a
concrete change is obvious. Read the file with `read_file`, then post a reply
containing a fenced `suggestion` block with the new code:

```` markdown
@alice good catch — here's the fix:

```suggestion
def greet(name):
    return f"Hello, {name}!"
```
````

The `suggestion` block must contain **only** the replacement for the exact
lines the reviewer commented on. GitHub renders it with a one-click
"Commit suggestion" button; the reviewer is the one who actually commits it.

If you cannot ground a suggestion in the real file contents (you didn't read
it, or the line anchor is unclear), fall back to a text reply explaining what
would need to change.

### Step 6: Post each reply

Two different endpoints depending on where the comment lives.

**Inline review comment** — reply in the same thread so GitHub attaches the
suggestion to the right lines:

```
gh api -X POST \
  repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments/$COMMENT_ID/replies \
  --field body="<your reply>"
```

**Top-level PR conversation comment** (including the `/cuga` trigger itself):

```
gh pr comment $PR_NUMBER --body "<your reply>"
```

Escape safely. Prefer piping the body in via a file or `--body-file -` rather
than embedding multi-line strings in a shell argument.

### Step 7: Print a summary line per reply

One line per comment, e.g.:

```
replied (text) to @alice on issue comment 123
replied (suggestion) to @bob on inline comment 456 at src/foo.py:42
skipped /cuga arming comment
```

This is only for the Actions log — it is not posted back to the PR.

## Hard rules

- Do not call `write_file`, `git add`, `git commit`, or `git push`. All changes
  reach the repo only via suggestion blocks that the reviewer commits.
- Do not reply to the same comment twice in one run.
- Do not invent facts about the diff, CI status, or unrelated files. Ground
  suggestions in file contents you actually read.
- Do not reply to yourself (`cuga` / `github-actions[bot]`).
- Keep each reply under ~600 characters of prose plus, at most, one
  `suggestion` block.
