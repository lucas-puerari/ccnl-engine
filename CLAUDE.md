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
uv run ruff check src/ tests/ scripts/    # zero errors; line limit 88 characters
uv run ruff format --check src/ tests/ scripts/
uv run mypy src/ tests/          # zero errors, strict mode
uv run mypy scripts/ --explicit-package-bases
uv run python scripts/ci/check_structure.py   # size limits, shrink-only baseline
uv run python scripts/docs/gen_capability_matrix.py --check   # matrix drift
uv run python scripts/docs/gen_contract_pages.py --check      # contract page drift
uv run python scripts/docs/gen_trust_counts.py --check        # docs/trust/ counts drift
```

`check_structure.py` enforces file, function and class size limits and
source depth against `scripts/ci/structure_baseline.json`; see
`docs/engine/architecture.md` for the limits and how to shrink the baseline.

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
behaviour. After one, regenerate the docs that quote the data
(`gen_contract_pages.py`, `gen_trust_counts.py`) and commit the result; every
number in `docs/trust/` sits between `<!-- trust:NAME -->` markers and is
never written by hand. Reference cases citing a signed source live in `tests/fixtures/expected/`
and run through `PayrollEngine` in `tests/acceptance/public_api/test_reference_cases.py`.

## Test layout

Enforced by `tests/architecture/test_test_layout.py`:

- `tests/unit/ccnl_engine/...`: pure rules, no filesystem and no real bundle.
  The path mirrors the module: `src/ccnl_engine/x/y/z.py` is tested by
  `tests/unit/ccnl_engine/x/y/test_z.py` or `test_z_<suffix>.py`.
- `tests/integration/ccnl_engine/...`: same mirror, for tests that read the
  real bundle, loaders, repositories or wire several modules (a
  `calculate_period` call without a repository reads the bundle).
  `tests/integration/scripts/` and `tests/integration/demo/` mirror tooling.
- `tests/acceptance/public_api/` and `tests/acceptance/legal_scenarios/`:
  behaviour through `PayrollEngine` only.
- `tests/architecture/`: dependencies, structure, public exports, data quality.
- `tests/fixtures/`: data and helpers only (`contracts/`, `expected/`,
  `legal_examples/`), never tests.

At most five directories under `tests` before a file (`fixtures` aside).
