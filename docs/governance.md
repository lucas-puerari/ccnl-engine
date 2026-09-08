# Release governance

Every change — code or data — goes through the same pipeline.
JSON files under `knowledge/*/data/` are code-level changes: they alter engine
behaviour and carry the same quality gates as Python source.

---

## Pipeline

```
Code changes  +  Data changes
          │
          ▼
    Unit tests          ← pure math, domain invariants
          │
          ▼
    Integration tests   ← full pipeline, every scenario
          │
          ▼
    Reference tests     ← 100% branch coverage; byte-identical output
          │
          ▼
    Coverage check      ← hard gate: 100% branch coverage
          │
          ▼
    Rules diff          ← detect unintended CCNL table changes
          │
          ▼
    Lint + types        ← ruff (zero errors), mypy strict, complexipy ≤ 15
          │
          ▼
    Review
          │
          ▼
    Release
```

---

## Quality gates (all must pass before any commit)

```bash
uv run pytest                    # 100% branch coverage — hard requirement
uv run ruff check src/ tests/    # zero errors; line limit 88 characters
uv run mypy src/ tests/          # zero errors, strict mode
uv run complexipy                # cognitive complexity ≤ 15 per function
```

Run them in this order. Fix coverage first, then lint, then types.

---

## Branch and commit rules

- Branch pattern: `{type}/{slug}` (CI-enforced).
  Allowed types: `feature | fix | chore | ci | docs | refactor | perf | test | revert`
- Commit: single line, `<type>(<scope>): <description>`, max 100 chars, no trailers.
- PR body: must not mention `Claude Code`, `claude.ai`, or `Anthropic` (CI check).
- PR title: conventional commits format (CI check).

---

## Knowledge-layer versioning

Every CCNL JSON carries a `meta.version` field (`YYYY.N`).
When a renewal changes salary tables or rates:

1. Bump the version (`2026.1` → `2026.2`).
2. Update the `source_hash` in the loader.
3. Add a new tranche to the affected time-series fields.
4. Run `uv run python docs/scripts/gen_coverage_matrix.py` to update coverage.
5. Add or update reference cases for the changed levels.

The `RulesDiff` utility detects before/after changes across any two dates:

```python
from ccnl_engine.engine.diff import diff_ccnl

changes = diff_ccnl(
    "metalmeccanico-federmeccanica.json", date(2025, 5, 31), date(2025, 6, 1)
)
```

---

## No feature without provenance and reference cases

Every new feature must ship with:

1. A Pydantic model or dataclass in the domain layer.
2. At least one `provenance` entry on the relevant JSON rule, pointing to the
   primary source document (article, circular, official table).
3. At least two reference cases in `tests/reference/cases/` that exercise the
   feature end-to-end and assert exact output values.

This is a hard rule, not a suggestion. A feature with no reference case has no
proof of correctness.
