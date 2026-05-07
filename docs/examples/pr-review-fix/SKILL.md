---
name: pr-review-fix
description: Reads the PR and its review comments, then returns a grounded reply to the triggering comment. Does not post back to the PR and does not modify any files — the workflow posts the returned text.
---

## Goal

You are replying to a single triggering comment on a pull request. Fetch the
real data you need (PR metadata, diff, files, other comments), decide what to
say, and **return** the reply as your final text answer. The GitHub Actions
workflow that invoked you will take your final answer and post it on the PR —
you do not post anything yourself.

## Available tools

- `run_command` — execute shell commands (use for `gh` CLI, `git`, and anything else)
- `read_file` — read a file's full contents (use to ground suggestions in real code)
- `write_file` — available but **must not be used**
- `list_files` — available but rarely needed

## Inputs from the environment

- `PR_NUMBER` — the pull request being handled
- `TRIGGER_COMMENT_AUTHOR` — the login of the person who posted the comment that woke you up
- `TRIGGER_COMMENT_BODY` — the exact text of that comment
- `GITHUB_TOKEN`, `GITHUB_REPOSITORY` — standard Actions values

## Workflow

### Step 1: Resolve OWNER and REPO

```
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name -q .name)
```

`run_command` returns plain stdout on success, so the result can be interpolated
into subsequent commands directly.

### Step 2: Check out the PR branch (if you will read files)

```
gh pr checkout $PR_NUMBER
```

Only needed if your reply will reference specific file contents.

### Step 3: Fetch what you need — do NOT rely on memory

Before composing the reply, fetch real data with tools. Typical commands:

```
gh pr view $PR_NUMBER --json number,title,headRefName,baseRefName,author
gh pr diff $PR_NUMBER                                    # the full diff
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/files         # list of changed files with additions/deletions
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments      # inline review comments
gh api repos/$OWNER/$REPO/issues/$PR_NUMBER/comments     # top-level PR conversation
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews       # review bodies (CodeRabbit summaries live here)
```

Use only the endpoints you actually need. Treat an empty body or non-JSON
response as an empty list, not an error.

### Step 4: Compose the reply

One reply, addressed to the triggering comment.

- If the triggering comment is `/cuga` or `/cuga stop`, return a short
  acknowledgement. (The workflow already handled arming; you just say hi.)
- Otherwise, answer the comment directly. Start with `@<TRIGGER_COMMENT_AUTHOR>`
  so the commenter gets a notification. Keep it to a few sentences of prose.
- If the commenter pointed at specific lines and a concrete change is obvious,
  include one fenced `suggestion` block containing **only** the replacement
  code, so a later tool can forward it as a GitHub suggestion:

  ````markdown
  @alice good catch — here is the fix:

  ```suggestion
  def greet(name):
      return f"Hello, {name}!"
  ```
  ````

- Ground every factual claim in what you fetched or read. If you could not
  fetch something you needed, say so in the reply rather than inventing it.

### Step 5: Return the reply as your final answer

Your final model response is the reply text itself. Do not wrap it in extra
narration such as "Here is the reply:" or "I will post this on the PR." The
workflow will take your final answer verbatim and post it as a PR comment.

## Hard rules

- **Do not fabricate PR facts.** File counts, line numbers, diff contents, CI
  status, author names, commit SHAs — all of these must come from tool output.
  If you did not call a tool to get a fact, you do not know it.
- **Do not post comments yourself.** Do not call `gh pr comment`,
  `gh api ... /comments`, or any other posting endpoint. Posting is the
  workflow's job.
- **Do not modify files.** No `write_file`, `git add`, `git commit`,
  `git push`, or any command with those effects.
- **One reply only.** The workflow posts exactly one comment per invocation —
  your final answer is that comment.
- Keep the reply under ~800 characters of prose plus, at most, one
  `suggestion` block.
