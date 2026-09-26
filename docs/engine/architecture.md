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
- Only the package root `ccnl_engine/__init__.py` imports `api`.
- The graph of `<capability>.<layer>` nodes has no cycle.
- Every module belongs to a layer. `ccnl_engine.version` and the
  `knowledge` data bundle outside `knowledge/service` are metadata: any
  layer except `domain` may import them. A capability `__init__.py` stays
  import free.

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
- No production module exceeds 400 lines.

## Payroll application layout

`payroll/application/` keeps its entry modules at the top level:
`calculate_period`, `calculate_year`, `close_tax_year`, `opening_balances`,
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
