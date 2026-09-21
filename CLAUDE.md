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

## Repository layout

The package is split in two namespaces:

- `src/ccnl_engine/engine/` — computation, pydantic schemas, and loaders
  (`contract`, `tax`, `surtax`, `payroll`, `io`, `primitives`).
- `src/ccnl_engine/knowledge/` — the versioned data bundle only: CCNL, tax,
  INPS and surtax JSON under `data/`, plus `__version__`.
  Loaders read it via `importlib.resources`; it carries no logic.

JSON changes in `knowledge/*/data/` are code-level changes: they alter engine
behaviour. End-to-end scenarios live in `tests/integration/cases/`.
