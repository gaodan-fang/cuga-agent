---
name: pr-review-fix
description: Fetches PR review comments (CodeRabbit + human reviewers), filters CodeRabbit findings to critical/major/minor, applies minimal code fixes with one conventional commit per fix, and pushes to the PR branch.
---

## Goal

Given a PR number, fetch all review comments, triage them, and apply minimal targeted code fixes.
Each fix gets its own conventional commit. Push the result to the PR branch. Print a summary.

## Available tools

- `run_command` — execute shell commands (gh, git, etc.)
- `read_file` — read a file's full contents
- `write_file` — write full file contents (no Edit tool; changes require read → modify → write)
- `list_files` — list directory contents

## Workflow

### Step 1: Resolve PR and repo

Read `PR_NUMBER` from the environment. If absent, require it as an argument.
Determine `OWNER` and `REPO` from `gh repo view --json owner,name`.

```
PR_NUMBER=${PR_NUMBER:?required}
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name -q .name)
```

### Step 2: Check out the PR branch

```
gh pr checkout $PR_NUMBER
```

### Step 3: Fetch review comments

A PR can have comments in three distinct places; you must query all three or you
will miss CodeRabbit findings, which live under **reviews**, not inline comments.

```
gh pr view $PR_NUMBER --json number,headRefName,baseRefName,author
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews         # review bodies (CodeRabbit summary finds itself here)
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments        # inline diff comments (line-level replies from any review)
gh api repos/$OWNER/$REPO/issues/$PR_NUMBER/comments       # top-level PR conversation comments
```

Treat the `run_command` tool output as clean stdout: no "[exit N]" prefix is
added on success, so you can assign the result directly to a variable and
json.loads it without additional cleaning.

Filter out:
- Bot self-replies (comments where the commenter is the same bot that already posted a fix note).
- Any comments already posted by cuga or by `github-actions[bot]` (those are workflow-posted summaries).
- `gh api /user` may return HTTP 403 in GitHub Actions (the default token cannot
  read user info). That is fine — skip the bot-login lookup and rely on the
  login fields inside the comment payloads instead.

### Step 4: Triage CodeRabbit findings

CodeRabbit posts under the `coderabbitai` login (sometimes `coderabbitai[bot]`).
Its findings can appear in any of three shapes:

- Items inside the **review body** from `/pulls/$PR/reviews` (often the summary
  plus a list of actionable findings, each with a severity tag).
- Items in the **inline review comments** from `/pulls/$PR/comments` (per-line
  findings; each has a `path` and sometimes a `line` field).
- Occasional extra notes in `/issues/$PR/comments`.

For each finding:

- Extract the severity label. Accept: `critical`, `major`, `minor`.
- Skip `nitpick` or anything labelled `nitpick` / `suggestion` only.
- Read the referenced file and verify the issue is still present in the current
  code. If already resolved, mark as skipped (reason: already fixed).
- Apply the minimal targeted fix. Do not refactor surrounding code.
- If a finding is inside the review body (not an inline comment) and does not
  clearly name a file/line, skip it with reason "no file anchor" rather than
  guessing.

### Step 5: Triage human comments

For each comment from a non-bot human reviewer:

- Judge actionability: skip questions, praise, general discussion, or anything with no clear
  code change implied.
- Apply a fix only when the comment clearly requests a specific code change.

### Step 6: Commit each fix independently

For each fix applied:

1. Stage only the specific files that were modified for this fix.
   Never run `git add -A` or `git add .`.
2. Commit with a conventional commit message:
   ```
   fix(<scope>): <short description>

   Addresses review comment: <brief citation of the finding>
   ```
3. Do not use `--no-verify`. Do not amend any commit.

### Step 7: Push

```
git push
```

Push all new commits to the PR branch in one push after all fixes are committed.

### Step 8: Print summary

Output a markdown table:

| Status  | Finding source | File(s) changed | Commit |
|---------|---------------|-----------------|--------|
| applied | CodeRabbit (minor) – <excerpt> | src/foo.py | fix(foo): ... |
| skipped | CodeRabbit (nitpick) | — | already-resolved / nitpick |
| skipped | Human comment – question | — | not actionable |

## Hard rules

- Never use `--no-verify` on any git command.
- Never amend a commit (`git commit --amend` is forbidden).
- Never stage files outside the specific fix with `git add -A`, `git add .`, or wildcards.
- Do not reply to or resolve reviewer comment threads (that is a separate workflow).
- Execute a single pass through findings. Do not loop or wait on CI. The workflow re-invokes
  the skill on each new comment trigger.
