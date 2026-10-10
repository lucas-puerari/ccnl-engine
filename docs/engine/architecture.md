# Architecture rules

The [Architecture contract](architecture-contract.md) fixes the target
layout that replaces the layers below, migration by migration; until then
the rules on this page stay in force.

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

`scripts/structure/check.py` measures the tree with `ast` and `tokenize`
and runs in CI and in `tests/architecture/test_structure_limits.py`. Ruff
enforces statement count and public methods with the same ceilings.

| Rule | Measured on | Target | Hard limit |
|---|---|---:|---:|
| `production_file_lines` | modules under `src/ccnl_engine` | 240 | 300 |
| `test_file_lines` | modules under `tests` | 400 | 500 |
| `function_lines` | functions in `src`, `tests`, `scripts` | 40 | 60 |
| `class_lines` | classes in `src`, `tests`, `scripts` | 100 | 150 |
| `public_methods` | classes, also Ruff `PLR0904` | 10 | 15 |
| `source_depth` | directories under `src/ccnl_engine` | 3 | 3 |
| `underscore_files` | files under `src`, `tests`, `scripts`, `demo` | 0 | 0 |
| `technical_directories` | directories under `src`, `tests`, `scripts`, `demo` | 0 | 0 |
| `markdown_lines` | hand-written Markdown pages | 450 | 600 |
| statements per function | Ruff `PLR0915` | 30 | 40 |
| cognitive complexity | complexipy | 10 | 15 |

File lengths are physical lines. Function and class lengths are effective
lines: from the `def` or `class` line to the end of the body, without
blank lines, comment-only lines and docstrings. A class whose only methods
are pydantic validators or serializers is declarative and exempt from
`class_lines`; `data/` directories are exempt from `source_depth`.

`underscore_files` records every file whose name starts with an underscore,
except the package root `src/ccnl_engine/__init__.py`, and
`technical_directories` every directory named `domain`, `application`,
`service`, `handlers`, `fixtures` or `data`. Each offender is one baseline
entry: a new `__init__.py`, `_module.py` or layer directory fails, and the
structural migrations remove the entries as they go. Hidden directories,
`__pycache__` and the gitignored `demo/_build` and `demo/wheels` are
skipped.

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

## Payroll layout

`payroll/` is laid out by subdomain, each file named by its role
(`inputs`, `models`, `types`, `rules`, `policies`, `validators`, `results`,
`services`, `handlers`, `ports`, `repositories`, `loaders`, `serializers`,
`facade`, optionally followed by a qualifier: `rules_irpef_net.py`):

| Subdomain | Holds |
|---|---|
| `period/` | one run: request, inputs and defaults, context, pipeline, posting, checks, result assembly, the knowledge repository port and its bundled sources |
| `year/` | competence and tax year plans, calendar, run selection, payments, year results, closing a tax year |
| `amount/` | pay items and treatments, the CCNL pay chain, proration, renewal minimum, rounding, the amounts of a run |
| `event/` | work, absence, variable pay and termination events, their handlers and totals |
| `employment/` | employment, employer, seniority, apprenticeship and category |
| `contribution/` | INPS rates and base, apprentices, domestic work, NASpI, pension and contractual funds |
| `taxation/` | IRPEF, deductions and credits, regimes, regional and municipal surtax |
| `family/` | art. 12 TUIR family deductions |
| `withholding/` | withholding plan and cap, deferrals, somma esente, carried recoveries |
| `sickness/` | sick pay rules, day classification, cumulation and comporto |
| `accrual/` | extra-month (tredicesima, quattordicesima) accrual and settlement |
| `termination/` | TFR, its revaluation and destination, ratei at termination |
| `ledger/` | ledger entries, posting and remittance codes |
| `state/` | period state, opening balances and its JSON serializer |
| `assurance/` | decisions, assessment, ruleset assurance and the reconciliation invariants |
| `capability/` | capability catalog, requirements, applicability and coverage |

`period/services.py` (`calculate_period`) reads as the pipeline:
`build_context`, then `run_events`, `run_amounts`, `run_decisions`,
`run_credits`, `post_run` and `assemble_result`. A pure state transition is
a rule (`year/rules_close.py`); the facade reaches it through an application
service (`period/services_facade_input.py`), since `api` imports the
application layer only.

## Test layout

`tests/architecture/test_test_layout.py` keeps the suite in five categories:
`unit` (pure rules), `integration` (real bundle, loaders, wiring),
`acceptance` (`public_api` and `legal_scenarios`, through `PayrollEngine`),
`architecture` and `fixtures` (data only). Unit and integration paths mirror
the module under test, for example `src/ccnl_engine/payroll/year/models_calendar.py`
and `tests/unit/ccnl_engine/payroll/year/test_models_calendar.py`. No file sits
deeper than five directories under `tests`, `fixtures` aside. `tests/README.md`
holds the ownership of each level and the role of each fixture folder.
