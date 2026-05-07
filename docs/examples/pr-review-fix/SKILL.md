---
name: pr-review-fix
description: Reply to the PR comment that triggered this workflow run. Posts one short, helpful response on the PR conversation.
---

## Goal

Read the triggering comment (already provided in the prompt and also in the
`TRIGGER_COMMENT_AUTHOR` / `TRIGGER_COMMENT_BODY` environment variables), compose
a short, direct reply, and post it as a PR comment. Nothing else — no file edits,
no commits, no rebases. This is the reply-only version of the skill; code fixes
will come later.

## Available tools

- `run_command` — execute shell commands (use for `gh` CLI)
- `read_file` — read a file's full contents (use only if the comment clearly refers to one)
- `write_file` — write a file (not needed in the reply-only flow)
- `list_files` — list directory contents (not needed in the reply-only flow)

## Workflow

### Step 1: Read the trigger

The prompt already contains the triggering comment. You can also re-read it from
the environment:

```
TRIGGER_COMMENT_AUTHOR=${TRIGGER_COMMENT_AUTHOR:-unknown}
TRIGGER_COMMENT_BODY="$TRIGGER_COMMENT_BODY"
PR_NUMBER=${PR_NUMBER:?required}
```

### Step 2: Compose the reply

Write one short reply (1–3 sentences). Keep it direct and grounded in what the
commenter actually said. Handle these cases:

- **Greeting / `/cuga` with no other text** — acknowledge you are watching the PR
  and will respond to further comments.
- **Question about the PR** — answer based on what the comment contains. If you
  need code context to answer, use `read_file` on the specific file they named.
  If you cannot answer from the comment alone, say so briefly.
- **Code-change request** — acknowledge the request and say that code fixes are
  not yet enabled in this version of the skill.
- **Non-actionable (praise, thanks, discussion)** — respond with a short friendly
  acknowledgement.

Do not invent facts about the PR diff, commits, or CI state — only use what the
comment itself provides or what you can read directly from files.

### Step 3: Post the reply

Escape the body safely (use single quotes and a heredoc to avoid shell expansion):

```
gh pr comment $PR_NUMBER --body "<your reply>"
```

Prefix the reply with `@$TRIGGER_COMMENT_AUTHOR` so the commenter gets a
notification. Keep the whole message under ~400 characters.

### Step 4: Print a one-line summary

Print a single line to stdout so the Actions log shows what happened, e.g.:

```
replied to @alice on PR #42
```

## Hard rules

- Do not modify any files.
- Do not run `git add`, `git commit`, or `git push`.
- Do not reply more than once per invocation.
- Do not quote the full comment back — it's already in the thread.
- If `gh pr comment` fails, print the error and exit without retrying.
