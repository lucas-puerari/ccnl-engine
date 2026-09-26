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

The package is organised by capability. Each capability holds only the layers
it needs: `application/` (use cases), `service/` (calculators, loaders,
repositories) and `domain/` (pure types and rules).

- `src/ccnl_engine/api/`: the public `PayrollEngine` facade.
- `src/ccnl_engine/payroll/`: period and year payroll computation.
- `src/ccnl_engine/contract/`: CCNL models, discovery and loader.
- `src/ccnl_engine/tax/`: IRPEF, INPS, TFR and surtax rules and loaders.
- `src/ccnl_engine/provenance/`: source, extraction and ruleset identity models.
- `src/ccnl_engine/diff/`: rules diff between two dates of a CCNL.
- `src/ccnl_engine/shared/domain/`: primitives and the error hierarchy, used by
  several capabilities.
- `src/ccnl_engine/knowledge/`: the versioned data bundle. CCNL, tax, INPS,
  surtax, capability and policy JSON under `*/data/` (pure data, no logic),
  plus `__version__`. `knowledge/service/` is its only code: bundled resource
  readers via `importlib.resources`. The bundled knowledge repository lives in
  `payroll/service/`.

Import direction and source depth are enforced by `tests/architecture/`
(see `docs/engine/architecture.md`).

Maximum depth: three directories under `ccnl_engine` before a file
(`ccnl_engine/<capability>/<layer>/<subfeature>/file.py`); `data/` is exempt.

JSON changes in `knowledge/*/data/` are code-level changes: they alter engine
behaviour. End-to-end scenarios live in `tests/integration/cases/`.
