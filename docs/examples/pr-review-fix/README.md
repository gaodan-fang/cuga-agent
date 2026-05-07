# pr-review-fix

**This is the reply-only version of the skill.** When armed, cuga replies to any
new comment on the PR with a short, grounded response. No code edits, no commits,
no pushes. Code-fix behaviour is planned for a future revision.

## How it works

Comment `/cuga` on a PR to arm it. Arming adds the `cuga-enabled` label to the PR. After
that, every new comment on the PR fires the GitHub Actions workflow. The workflow runs
under a `cuga-pr-<PR>` concurrency group with `cancel-in-progress: true`, so back-to-back
CodeRabbit comments collapse into one run instead of piling up. The workflow calls cuga
headless via the Python SDK; cuga reads the triggering comment, composes a reply, and
posts it back on the PR conversation.

## Files

- `SKILL.md` — the agent instructions loaded by cuga at runtime
- `../../../.github/workflows/cuga-pr-review.yml` — the GitHub Actions workflow that triggers on PR comments

Canonical path in this repo: `docs/examples/pr-review-fix/SKILL.md`. The workflow curls it
from this location at runtime into `.agents/skills/pr-review-fix/SKILL.md` on the runner,
which is where cuga's loader actually discovers skills. The runtime `.agents/` tree is
gitignored because it is per-user / per-run workspace.

## Install (in a consumer repo)

The skill itself lives in this repo (cuga-agent) — you do not vendor it into your project.
The workflow file fetches `SKILL.md` from cuga-agent at runtime, so a consumer repo only
needs to drop in one file.

1. Copy `.github/workflows/cuga-pr-review.yml` into your repo at `.github/workflows/`.
2. Add repo secrets: `GROQ_API_KEY` or `OPENAI_API_KEY` (whichever LLM provider cuga will use).
3. Grant the default `GITHUB_TOKEN` PR write access: Settings > Actions > General >
   Workflow permissions > "Read and write permissions".
4. Open a PR and comment `/cuga` once to arm it.

To pin to a specific cuga release, edit `CUGA_SKILLS_REF` in the "Fetch pr-review-fix
skill" step of the workflow (defaults to `main` on `cuga-project/cuga-agent`).

## Commands

| Command | Effect |
|---|---|
| `/cuga` | Arm the PR (first time) or re-run cuga manually |
| `/cuga stop` | Disarm; cuga will stop auto-responding to new comments |
| any other comment on an armed PR | Auto-triggers cuga |

## Limits

- Reply-only in this version — does not edit files, commit, or push.
- One reply per invocation. No back-and-forth inside a single run.
- Requires either a `cuga-enabled` label or a comment starting with `/cuga` to fire; otherwise the workflow skips silently.
- The concurrency group cancels in-flight runs when new comments arrive, so bursts from CodeRabbit collapse into one run and only the final comment is replied to.
- cuga currently lacks a native one-shot CLI, so the workflow calls the Python SDK via a small inline script.

## Troubleshooting

- If cuga is silent, check the Actions tab for the workflow run — it may have been cancelled by concurrency before it started.
- If `/cuga stop` does not disarm, verify that the `cuga-enabled` label was actually removed in the PR sidebar.
