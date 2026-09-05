Open a pull request for the current branch using the project PR template.

## Rules

- The PR body MUST follow the three-section template below. Every section is required.
- NEVER include references to Claude Code, claude.ai, Anthropic, co-authored-by AI, or any AI tooling. The `check-pr-body` CI job will fail if any such reference appears.
- Do not push directly to `main`. This command is only valid on a feature/fix/chore branch.

## Step 1 — Verify the branch

```bash
git branch --show-current
```

If the current branch is `main`, stop and tell the user to switch to a working branch first.

## Step 2 — Check for uncommitted changes

```bash
git status --short
```

If there are uncommitted changes, stop and ask the user whether to commit them first.

## Step 3 — Gather context for the PR body

Run these commands to collect the information you need:

```bash
# Commits on this branch vs. main
git log origin/main..HEAD --oneline

# Files changed
git diff --stat origin/main..HEAD

# Full diff for understanding what changed
git diff origin/main..HEAD
```

Read the CCNL JSON files, test files, or other key files that were added or modified to understand:
- **What** was built (files and their purpose)
- **Why** it was built (coverage gap, headcount, business rationale, CNEL code)
- **How** it was implemented (model choices, verifications, SIMPLIFICATIONs)

If this is a contract PR, also read the JSON file to extract: CNEL code, salary model (conglobated/split), hourly_divisor, additional_months, seniority cadence, apprenticeship type.

## Step 4 — Derive the PR title

Convention: `feat({id}): add CCNL {Name} ({CNEL code}) payroll engine` for contract PRs.
For other work: use `fix(scope): ...`, `chore(scope): ...`, `refactor(scope): ...`, etc.
Keep it to a single line.

## Step 5 — Build the PR body

Fill in the template below. Every section must have real content — no placeholder comments left in.

```
## What
[List the files created or modified and the role of each one. Be specific.]

## Why
[Explain the coverage gap this fills, the headcount or business rationale, and the CNEL code if applicable.]

## How
[Describe the implementation: conglobated vs. split and how verified; hourly_divisor derivation; seniority cadence and source; apprenticeship type with source URL and renewal date; any new TaxSector added; key SIMPLIFICATIONs and their scope.]
```

For non-contract PRs, adapt each section to fit the actual change.

## Step 6 — Push and open the PR

```bash
git push -u origin HEAD
gh pr create \
  --title "{TITLE}" \
  --body "{BODY}" \
  --base main
```

After the PR is created, print the PR URL.

## Hard constraints

- No AI references anywhere in title or body.
- All three CI checks must be passing before opening the PR: `pytest` (100% branch coverage), `ruff check`, `mypy`.
  If any is failing, stop and fix them first.
- The branch name must follow the project pattern: `chore/{id}-{datoriale}`, `feature/...`, `fix/...`.
  The CI validates branch naming.
