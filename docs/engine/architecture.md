# Architecture rules

The package is organised by capability (`payroll`, `contract`, `tax`,
`knowledge`, `provenance`, `diff`, `shared`) plus the `api` facade. Each
capability holds only the layers it needs:

| Layer | Holds |
|---|---|
| `application/` | use cases and orchestration |
| `service/` | calculators, resolvers, loaders and repositories |
| `domain/` | types, pure rules and invariants |

The rules below are enforced by `tests/architecture/`, which parses the
sources without importing them. Imports under `if TYPE_CHECKING:` are not
counted because they never run.

## Import direction

```text
api -> application -> service -> domain
       application -> domain
```

- `domain` imports only `domain`: its own, `shared.domain`, and another
  capability's domain only through a short allowlist in
  `tests/architecture/test_dependencies.py`, where each entry states its
  reason. An entry that no import uses any more fails the suite, so the list
  can only shrink.
- `service` never imports `application`.
- `api` imports `application`, plus metadata such as the bundle version; it
  never reaches loaders such as `knowledge.service` directly.
- Only the root layer (the package root `ccnl_engine/__init__.py` and the
  public namespaces) may import `api`.
- The graph of `<capability>.<layer>` nodes has no cycle.
- Every module belongs to a layer. `ccnl_engine.version` and the
  `knowledge` data bundle outside `knowledge/service` are metadata: any
  layer except `domain` may import them. A capability `__init__.py` stays
  import free.

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
- `tests/architecture/test_public_exports.py` pins each `__all__`, keeps the
  modules disjoint and keeps README, `docs/examples` and the wheel smoke test
  on these five modules. Acceptance tests import nothing else.

## Domain purity

Domain modules perform no I/O: no `importlib.resources`, no `pathlib`, no
`open()`, no `json.load()` and no `.read_text()`, `.read_bytes()` or
`.open()` calls. Reading bundled data is a `service` concern.

## Source layout

- At most three directories under `ccnl_engine` before a source file:
  `ccnl_engine/<capability>/<layer>/<subfeature>/file.py`. `data/` resource
  directories are exempt.
- Every directory holding Python sources has an `__init__.py`.
- No layer directory exists without at least one module besides
  `__init__.py`.
- File length and source depth follow the structural limits below.

## Structural limits

`scripts/ci/check_structure.py` measures the tree with `ast` and `tokenize`
and runs in CI and in `tests/architecture/test_structure_limits.py`. Ruff
enforces statement count and public methods with the same ceilings.

| Rule | Measured on | Target | Hard limit |
|---|---|---:|---:|
| `production_file_lines` | modules under `src/ccnl_engine` | 250 | 300 |
| `test_file_lines` | modules under `tests` | 350 | 500 |
| `function_lines` | functions in `src`, `tests`, `scripts` | 40 | 60 |
| `class_lines` | classes in `src`, `tests`, `scripts` | 100 | 150 |
| `public_methods` | classes, also Ruff `PLR0904` | 10 | 15 |
| `source_depth` | directories under `src/ccnl_engine` | | 3 |
| statements per function | Ruff `PLR0915` | 30 | 40 |
| cognitive complexity | complexipy | 10 | 15 |

File lengths are physical lines. Function and class lengths are effective
lines: from the `def` or `class` line to the end of the body, without
blank lines, comment-only lines and docstrings. A class whose only methods
are pydantic validators or serializers is declarative and exempt from
`class_lines`; `data/` directories are exempt from `source_depth`.

Current offenders are listed in `scripts/ci/structure_baseline.json` with
their measured value. The check fails when:

- a file, function or class above a hard limit is not in the baseline;
- an offender grows past its baseline value;
- a baseline entry is back within the limit and still listed.

The baseline only shrinks. To remove an entry, bring the offender under the
hard limit and delete its line; an offender that shrinks but still offends
passes with a note, and its value should be lowered in the same change.
`python scripts/ci/check_structure.py --write-baseline` rewrites the file
from the tree: review the diff and reject any added entry.

## Payroll application layout

`payroll/application/` keeps its entry modules at the top level:
`calculate_period`, `calculate_competence_year`, `calculate_tax_year`,
`year_result`, `close_tax_year`, `opening_balances`,
`reconcile`, `allocate_events`, `post_ledger`, `knowledge_repository` and
`bundled_sources`, plus the shared helpers `_period_utils` and
`_posting_service`. The steps they call live in subfeature packages, each
private to the application layer:

| Package | Holds |
|---|---|
| `period/` | one run: context, pipeline steps, base lines, closing state, checks, result assembly |
| `amounts/` | contributions and TFR, taxable income, IRPEF and surtax of a run |
| `withholding/` | withholding plan and cap, somma esente, carried recoveries |
| `year/` | calendar, run selection and requests, extra-month ratei |
| `invariants/` | the reconciliation invariants that `reconcile` runs |
| `handlers/` | one handler per event family, their registry and event totals |

`calculate_period` reads as the pipeline: `build_context`, then
`run_events`, `run_amounts`, `run_decisions`, `run_credits`, `post_run` and
`assemble_result`.

## Test layout

`tests/architecture/test_test_layout.py` keeps the suite in five categories:
`unit` (pure rules), `integration` (real bundle, loaders, wiring),
`acceptance` (`public_api` and `legal_scenarios`, through `PayrollEngine`),
`architecture` and `fixtures` (data only). Unit and integration paths mirror
the module under test, for example `src/ccnl_engine/payroll/domain/calendar.py`
and `tests/unit/ccnl_engine/payroll/domain/test_calendar.py`. No file sits
deeper than five directories under `tests`, `fixtures` aside.
