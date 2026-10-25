# Architecture rules

The [Architecture contract](architecture-contract.md) fixes the layout: one
root per concept, directories named after domains, files named after roles.

The facade sits in `api.py`, the shared `errors`, `types` and `validators`
modules at the root. Each file is named by its role, and the role places it
on a layer:

| Layer | Roles |
|---|---|
| application | `services`, `handlers`: use cases and orchestration |
| service | `ports`, `repositories`, `loaders`, `serializers` |
| domain | `models`, `types`, `inputs`, `requests`, `results`, `policies`, `rules`, `validators`, `facade` |

Imports under `if TYPE_CHECKING:` do not count: they never run.

## Import direction

```text
api -> application -> service -> domain
       application -> domain
```

- `domain` imports only `domain`; `service` never imports `application`.
- `api` imports `application`, plus metadata such as the bundle version; it
  never reaches a loader directly.
- Only the package root `ccnl_engine/__init__.py` and the public namespaces
  import `api`.
- A concept imports only concepts of its own tier or of a lower one
  (orchestration, computation, norms: see
  [Dependency tiers](architecture-contract.md#dependency-tiers)); cycles
  inside a tier are allowed. `scripts/architecture/check.py` enforces
  the tiers, with the upward imports the contract lists by module, and the
  300-line limit of a module against a shrink-only baseline; `make check`
  and CI run it.
- `ccnl_engine.version`, which holds the engine and bundle versions, and
  the bundle series in `bundle/facade.py` are metadata: any layer except `domain` may import them. A package
  `__init__.py` holds a docstring only, except the package root and
  `ccnl_engine.catalog`, which hold the public namespaces.

## Public API

The public API is the package root `ccnl_engine` and four namespace modules
next to it. They only re-export names defined in the concepts.

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
- `tests/integration/ccnl_engine/api/test_public_exports.py` pins each
  `__all__`, keeps the modules disjoint and keeps README, `docs/examples` and
  the wheel smoke test on these five modules.
- `tests/integration/ccnl_engine/api/test_reference.py` keeps `docs/api/`
  on the same names: one directive per public name, none on an internal
  module.

## Domain purity

Domain modules perform no I/O: no `importlib.resources`, no `pathlib`, no
`open()`, no `json.load()` and no `.read_text()`, `.read_bytes()` or
`.open()` calls. Reading bundled data is a `service` concern.

## Source layout

- A directory is a plain domain name from the "Directory names" section of
  the [glossary](../domain/glossary.md); right below the package root only a
  concept. A file is exactly a technical role, or a root module (`api`,
  `inputs`, `events`, `results`, `errors`, `version`). Depth is not limited.
- `knowledge/` holds data only: the JSON resources and their manifest.
- Every directory holding Python sources has an `__init__.py`.

## Size limits

| Rule | Limit | Checked by |
|---|---:|---|
| Lines of a module under `src/ccnl_engine` | 300 | review |
| Lines of a test module | 500 | review |
| Statements per function | 40 | Ruff `PLR0915` |
| Public methods per class | 15 | Ruff `PLR0904` |
| Cognitive complexity per function | 15 | complexipy (`make complexity`) |
| Lines of a hand-written Markdown page | 600 | review |

A module that outgrows its limit moves part of its content into a subdomain
directory with the same role file.

## Test layout

The suite has three categories: `knowledge` (normative oracles, legal
scenarios, reference and observed payslips), `unit` (one unit, no I/O) and
`integration` (public API, loaders, wiring, scripts, demo). Paths mirror the
module under test and a test file is named after its role:
`src/ccnl_engine/contribution/naspi/services.py` and
`tests/unit/ccnl_engine/contribution/naspi/test_services.py`; see
[Target trees](architecture-contract-trees.md#test-tree). `tests/README.md`
holds the rule, the ownership of each level and the role of each data
folder; `scripts/quality/test_tree/check.py` enforces the mirror.
