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

Gather all comment sources:

```
gh pr view $PR_NUMBER --json number,headRefName,baseRefName,author
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments        # inline diff comments
gh api repos/$OWNER/$REPO/issues/$PR_NUMBER/comments       # top-level PR comments
```

Filter out:
- Bot self-replies (comments where the commenter is the same bot that already posted a fix note).
- Any comments already posted by cuga (author login matches cuga's bot identity).

### Step 4: Triage CodeRabbit findings

For each comment authored by `coderabbitai` (or similar bot login):

- Extract the severity label from the comment body. Accept: `critical`, `major`, `minor`.
- Skip `nitpick` or any finding labelled `nitpick` / `suggestion` only.
- For each accepted finding, read the relevant file(s) and verify the issue is still present in
  the current code. If already resolved, mark as skipped (reason: already fixed).
- Apply the minimal targeted fix. Do not refactor surrounding code.

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
