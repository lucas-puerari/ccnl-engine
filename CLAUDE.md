# ccnl-engine — Project knowledge base

Loaded automatically by Claude at the start of every session.

---

## Branch naming (CI-enforced)

Pattern: `{type}/{slug}` — validated by `.github/workflows/branch-name.yml`.

Allowed types: `feature | fix | chore | ci | docs | refactor | perf | test | revert`

For new contracts: `chore/{id}-{datoriale}` — e.g. `chore/e018-unionalimentari`.

Never push directly to `main`. Use `/new-branch` to create branches.

---

## Commit format

**Single line only** — the git hook rejects multi-line messages.

Format: `<type>(<scope>): <description>` (max 100 characters total)

For new contracts: `feat(<id>): add CCNL <Name> (<CNEL code>) payroll engine`

No trailers of any kind: no `Co-authored-by`, no `Signed-off-by`, no AI attribution.

Note: commit type `feat` and branch prefix `feature/` are different namespaces.

---

## PR rules

- **Title**: must follow conventional commits format (validated by CI)
- **Body**: must not mention `Claude Code`, `claude.ai`, or `Anthropic` — CI rejects the PR if it does
- Body structure: `## What`, `## Why`, `## How`

---

## Quality gates (all must pass before any commit)

```bash
uv run pytest                    # 100% branch coverage — hard requirement
uv run ruff check src/ tests/    # zero errors; line limit 88 characters
uv run mypy src/ tests/          # zero errors, strict mode
```

Run them in this order. Fix coverage first, then lint, then types.

---

## Source of truth for contract count

```bash
ls src/ccnl_engine/contracts/data/*.json | grep -v '__init__' | wc -l
```

Use this count for goal tracking, not `git log`. If the two diverge, the JSON count is authoritative.

---

## Available commands

| Command | When to use |
|---------|-------------|
| `/new-contract` | Full 10-step workflow to add one CCNL (research → merged PR) |
| `/batch N` | Add N CCNLs sequentially in one session without stopping |
| `/new-branch <type> <slug>` | Create a CI-valid branch from up-to-date main |

---

## Common pitfalls

- **Apprenticeship type**: verify against the actual CCNL renewal year. Pre-renewal and post-renewal may use different models.
- **Conglobated vs split**: run the back-calculation on at least 3 seniority levels before writing JSON.
- **`hourly_divisor`**: derive from the contract source, never copy from another contract.
- **Docstrings and comments**: ruff E501 applies — keep under 88 characters.
- **Imports in tests**: ruff PLC0415 rejects imports inside test functions. All imports at module top level.
- **Multi-line commits**: the git hook rejects them with no override. One line only.
- **PR body AI mention**: the CI workflow fails the PR silently if the body mentions Claude or Anthropic. Write PR bodies in first person as the author.
