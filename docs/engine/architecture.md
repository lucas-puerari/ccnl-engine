# Architecture rules

The [Architecture contract](architecture-contract.md) fixes the layout: one
root per concept, directories named after domains, files named after roles.
The layout by source (`contract`, `tax`, `payroll`) has been fully migrated.

The facade sits in `api.py`, the shared `errors`, `primitives` and
`validation` modules at the root. Each file is named by its role, and the
role places it on a layer:

| Layer | Roles |
|---|---|
| application | `services`, `handlers`: use cases and orchestration |
| service | `ports`, `repositories`, `loaders`, `serializers` |
| domain | `models`, `types`, `inputs`, `requests`, `results`, `policies`, `rules`, `validators`, `facade` |

The rules below are enforced by `tests/integration/scripts/structure/`, which
parses the sources without importing them. Imports under `if TYPE_CHECKING:`
are not counted because they never run.

## Import direction

```text
api -> application -> service -> domain
       application -> domain
```

- `domain` imports only `domain`: its own, the shared root modules, and another
  capability's domain only through a short allowlist in
  `tests/integration/scripts/structure/test_dependencies.py`, where each entry states its
  reason. An entry that no import uses any more fails the suite, so the list
  can only shrink.
- `service` never imports `application`.
- `api` imports `application`, plus metadata such as the bundle version; it
  never reaches a loader such as `knowledge.loaders` directly.
- Only the root layer (the package root `ccnl_engine/__init__.py` and the
  public namespaces) may import `api`.
- The graph of `<capability>.<layer>` nodes of the legacy roots has no
  cycle.
- A concept imports only concepts of its own tier or of a lower one
  (orchestration, computation, norms: see
  [Dependency tiers](architecture-contract.md#dependency-tiers)); cycles
  inside a tier are allowed. Every root of the package has a tier or is a
  legacy root (`tax`), which the rule skips until it empties. An import that cannot
  move yet is allowlisted with its reason; the allowlist and the legacy
  roots only shrink.
- Every module belongs to a layer. `ccnl_engine.version` and the bundle
  version in `bundle/facade.py` are metadata: any layer except `domain`
  may import them. A package `__init__.py` holds a docstring only.

## Public API

The public API is the package root `ccnl_engine` and four namespace modules
next to it. They only re-export names defined in the capabilities and sit on
the root layer.

| Module | Rule |
|---|---|
| `ccnl_engine` | The common path: `PayrollEngine`; the types a caller builds for `calculate_period` and the year plans on the common path (`PeriodInput`, `PeriodFacts`, `PayrollRun`, `Employment`, `EmployerProfile`, `Headcount`, `CompetenceYearPlan`, `TaxYearPlan`); what those calls return (`PeriodResult`, `CompetenceYearResult`, `TaxYearResult`); every `CcnlEngineError` subclass, since a caller catches them; `engine_version` |
| `ccnl_engine.inputs` | Every other fact a caller passes in: optional fields of the root inputs, tax facts, calendar, engine mode, opening state and imported balances |
| `ccnl_engine.events` | Work events of `PeriodFacts.events` and the types an event needs |
| `ccnl_engine.results` | Types read from a result: assurance, blockers, decisions, limitations, capability gaps, ledger accounts, remittance |
| `ccnl_engine.catalog` | What the engine covers before any run: bundled contracts, ruleset identity and readiness, capability catalog |

- A name lives in exactly one of the five modules: no alias, no second
  import path. A new public name goes to a namespace unless it is needed by
  the one-request example of the root docstring or is an error.
- A type reachable from a public type that a caller never builds, matches on
  or catches (state internals, pay item variants) stays internal.
- `tests/integration/ccnl_engine/api/test_public_exports.py` pins each `__all__`, keeps the
  modules disjoint and keeps README, `docs/examples` and the wheel smoke test
  on these five modules. Acceptance tests import nothing else.

## Domain purity

Domain modules perform no I/O: no `importlib.resources`, no `pathlib`, no
`open()`, no `json.load()` and no `.read_text()`, `.read_bytes()` or
`.open()` calls. Reading bundled data is a `service` concern.

## Source layout

- A directory is a plain domain name from the "Directory names" section of
  the [glossary](../domain/glossary.md); right below the package root only a
  concept. A file is exactly a technical role, or a root module (`api`,
  `inputs`, `events`, `results`, `errors`, `version`). Depth is not limited.
- Every directory holding Python sources has an `__init__.py`.
- No directory exists without at least one module besides `__init__.py`.
- File length follows the structural limits below.

## Structural limits

`scripts/structure/check.py` measures the tree with `ast` and `tokenize`
and runs in CI and in `tests/integration/scripts/structure/test_structure_limits.py`. Ruff
enforces statement count and public methods with the same ceilings.

| Rule | Measured on | Target | Hard limit |
|---|---|---:|---:|
| `production_file_lines` | modules under `src/ccnl_engine` | 240 | 300 |
| `test_file_lines` | modules under `tests` | 400 | 500 |
| `function_lines` | functions in `src`, `tests`, `scripts` | 40 | 60 |
| `class_lines` | classes in `src`, `tests`, `scripts` | 100 | 150 |
| `public_methods` | classes, also Ruff `PLR0904` | 10 | 15 |
| `underscore_files` | files under `src`, `tests`, `scripts`, `demo` | 0 | 0 |
| `technical_directories` | directories under `src`, `tests`, `scripts`, `demo` | 0 | 0 |
| `role_files` | Python modules under `src`, `tests`, `scripts`, `demo` | 0 | 0 |
| `domain_directories` | directories above a Python module under the same roots | 0 | 0 |
| `markdown_lines` | hand-written Markdown pages | 450 | 600 |
| statements per function | Ruff `PLR0915` | 30 | 40 |
| cognitive complexity | complexipy | 10 | 15 |

File lengths are physical lines. Function and class lengths are effective
lines: from the `def` or `class` line to the end of the body, without
blank lines, comment-only lines and docstrings. A class whose only methods
are pydantic validators or serializers is declarative and exempt from
`class_lines`.

`underscore_files` records every file whose name starts with an underscore,
except the package root `src/ccnl_engine/__init__.py`, and
`technical_directories` every directory named `domain`, `application`,
`service`, `handlers`, `fixtures` or `data`. Each offender is one baseline
entry: a new `__init__.py`, `_module.py` or layer directory fails, and the
structural migrations remove the entries as they go. Hidden directories,
`__pycache__` and the gitignored `demo/release` are
skipped.

`role_files` records every Python module whose name is not a role or root
module (under `src`), `test_<name>.py` of such a name or a helper
(`conftest`, `builders`, `oracles`, `support`, under `tests`), an action or
a role (under `scripts`), or `app.py` (under `demo`).
`domain_directories` records every directory above a module whose name is
not in the glossary list, or not a concept right below the package root.
`scripts/structure/naming/rules.py` states both rules; the concept
migrations empty their baseline entries.

`markdown_lines` counts the physical lines of the top-level pages and of the
pages under `docs`. The audit notes `REVIEW.md` and `TODO.md` are excluded.
So are the pages generated under `docs/contracts` and the built site under
`docs/_build`: their generators validate them against the sources with
`--check` in CI.

The targets sit at about 80% of the hard limits and never fail the check.
Every run prints how many entries sit above each target;
`python scripts/structure/check.py --targets` lists them. Bring a file
under its target when it is touched, before it reaches the hard limit.

Current offenders are listed in `scripts/structure/baseline.json` with
their measured value. The check fails when:

- a file, function or class above a hard limit is not in the baseline;
- an offender grows past its baseline value;
- a baseline entry is back within the limit and still listed.

The baseline only shrinks. To remove an entry, bring the offender under the
hard limit and delete its line; an offender that shrinks but still offends
passes with a note, and its value should be lowered in the same change.
`python scripts/structure/check.py --write-baseline` rewrites the file
from the tree: review the diff and reject any added entry.

## Test layout

`tests/integration/scripts/structure/test_test_layout.py` keeps the suite in
three categories: `knowledge` (normative oracles, legal scenarios, reference
and observed payslips), `unit` (one unit, no I/O) and `integration` (public
API, loaders, wiring, scripts, demo). Paths mirror the module under test and
a test file is named after its role: `src/ccnl_engine/contribution/naspi/services.py`
and `tests/unit/ccnl_engine/contribution/naspi/test_services.py`; see
[Target trees](architecture-contract-trees.md#test-tree). `tests/README.md`
holds the ownership of each level and the role of each data folder.
