# Architecture contract

This page fixes the target layout of the repository and the names it uses.
It is binding for the structural migrations that follow it: the knowledge
layout, the domains outside `payroll`, the `payroll` domain, `demo` and
`scripts`, and the test tree. Until a migration lands, the current layout
described in [Architecture rules](architecture.md) stays in force; the
guardrails below only stop the old layout from growing.

The contract has three pages:

- this page: principles, decisions, the production tree, the glossary of
  domains and roles, and the dependency direction;
- [Target trees](architecture-contract-trees.md): the data, `demo`,
  `scripts` and test trees, and the inventory of every current file;
- [Migration notes](architecture-contract-migration.md): the namespace
  package spike, the path-keyed data a move must update, and where this
  contract departs from the original proposal.

## Principles

- Directories name domains or subdomains only. Files name technical roles.
- A domain name is singular or uncountable and appears in the glossary
  below. One concept uses one term in production code, public API, knowledge
  data, demo, scripts and tests.
- No file name starts with an underscore. The exceptions are the package
  root `src/ccnl_engine/__init__.py`, which keeps
  `from ccnl_engine import PayrollEngine` working, and the docstring-only
  package markers of the source directories (see below).
- No directory is named after a technical layer: `domain`, `application`,
  `service`, `handlers`, `fixtures` and `data` disappear from the final
  tree. The role lives in the file name instead.
- Every source directory keeps a package marker: an `__init__.py` holding
  only a docstring, never code. The documentation tooling (griffe, behind
  mkdocstrings) does not load a namespace directory inside a regular
  package, so namespace packages below the root would drop every moved
  module from the API reference. An `__init__.py` that holds code moves to a
  file with a role name (usually `facade.py`), so no re-export is lost.
  Test directories carry no marker: pytest imports them by path.
- A leaf directory holds only the roles it needs. No empty file is created
  for symmetry.
- Every move is listed in the inventory before it happens; nothing is
  deleted implicitly.

## Decisions

| Topic | Decision |
|---|---|
| Package root | `src/ccnl_engine/__init__.py` stays, with its docstring and its re-exports. It is the only file whose name starts with an underscore. |
| Public API | The public surface is the root and the namespaces `ccnl_engine.inputs`, `ccnl_engine.events`, `ccnl_engine.results` and `ccnl_engine.catalog`, as pinned by `tests/architecture/test_public_exports.py` and stated in the root docstring. These five modules keep their import paths. |
| Deep imports | Paths below the five public modules (`ccnl_engine.payroll.domain.ledger` and the like) are not public. The migrations move them without compatibility shims and without deprecation aliases. |
| `catalog.py` | Kept at the root next to `api.py`, `inputs.py`, `results.py` and `events.py`, because `ccnl_engine.catalog` is a public namespace. |
| Root modules | `api`, `inputs`, `results`, `events`, `catalog`, `errors`, `primitives`, `validation` and `version`, each splittable as `<name>_<suffix>.py` (for example `validation_collection.py`). |
| New directories | A new source directory gets a docstring-only `__init__.py` marker, which the guardrail accepts. A new test directory needs none: pytest imports tests by path (`--import-mode=importlib`). |
| Inventory upkeep | `scripts/ci/layout_inventory.json` is generated. A change that adds, renames or removes a tracked file under `src`, `tests`, `demo` or `scripts` regenerates it; CI fails on drift. |

## Production tree

```text
src/ccnl_engine/
├── __init__.py            package root, the only underscore file
├── api.py                 PayrollEngine facade
├── inputs.py  events.py  results.py  catalog.py   public namespaces
├── errors.py  primitives.py  validation.py  validation_collection.py
├── version.py
├── contract/
│   ├── identity/  employment/  compensation/  working_time/  absence/
│   └── sickness/  seniority/  fund/  catalog/
├── payroll/
│   ├── period/  year/  employment/  event/  amount/  contribution/
│   ├── taxation/  withholding/  sickness/  family/  termination/
│   └── accrual/  ledger/  assurance/  capability/  state/
├── tax/
│   ├── income/  surtax/  contribution/  pension/  sickness/
│   └── severance/  family/  regime/  annual/
├── knowledge/             loaders at the top, datasets below
│   ├── contract/  taxation/  surtax/  social_security/
│   └── policy/  capability/  limitation/
├── provenance/
│   ├── ruleset/
│   └── source/
└── comparison/
    └── ruleset/
```

Two subdomains extend the proposal; see
[Migration notes](architecture-contract-migration.md#amendments):
`payroll/state/` and `tax/annual/`.

At most three directories sit between `ccnl_engine` and a module. Knowledge
JSON is exempt, because its path carries the dataset, the year and the scope
(`knowledge/social_security/contribution/2026/industria.json`).

## Glossary of domains

| Domain | Holds |
|---|---|
| `contract` | A CCNL as a document: identity, coverage, validity, levels, pay, working time, absences, sick pay, seniority, funds, the catalog of bundled agreements |
| `contract/catalog` | Discovery and loading of bundled agreements, ruleset readiness |
| `payroll/period` | One payroll run: request, context, pipeline, result, input defaults, the knowledge port |
| `payroll/year` | Competence and tax years: plans, calendar, schedule, run selection, sequences, year results |
| `payroll/employment` | The employment relationship: contract type, employer, hours, seniority, category, apprenticeship |
| `payroll/event` | Work events and their handlers |
| `payroll/amount` | Pay items, treatments, pay chain, proration, rounding, the pay item policy |
| `payroll/contribution` | INPS, contractual, pension fund and end-of-service contributions |
| `payroll/taxation` | IRPEF, credits, deductions, surtaxes, substitute regimes, tax facts |
| `payroll/withholding` | What a run withholds: cap, plan, deferral, somma esente, recoveries, the withholding agent |
| `payroll/sickness` | Sickness episodes, sick days, cumulation, sick pay |
| `payroll/family` | Art. 12 TUIR family deductions |
| `payroll/termination` | TFR fund, destination, revaluation, settlement and ratei at termination |
| `payroll/accrual` | Extra-month accrual: qualifying months, ratei, settlement |
| `payroll/ledger` | Ledger entries, posting, base and tax lines, remittance |
| `payroll/assurance` | Assurance, decisions, invariants, limitations and rulesets a run read |
| `payroll/capability` | Capability catalog, requirements, traces and reports of a run |
| `payroll/state` | State carried between runs: accrual state, tax cash state, YTD accounts, obligations, opening balances, the state codec |
| `tax/<area>` | Typed statutory rules per area: `income` (IRPEF), `surtax`, `contribution` (INPS), `pension`, `sickness`, `severance` (TFR), `family`, `regime` (substitute regimes, variable pay), `annual` (the assembled ruleset of a year and its readers) |
| `knowledge/<dataset>` | Bundled JSON per dataset, see [Target trees](architecture-contract-trees.md#data-tree) |
| `provenance/ruleset`, `provenance/source` | Ruleset identity and assurance; sources, extraction and evidence chains |
| `comparison/ruleset` | The rules diff between two dates of a CCNL |

## Technical roles

| Role file | Holds |
|---|---|
| `models.py`, `types.py` | State and value objects; enums and type aliases |
| `inputs.py`, `requests.py`, `results.py` | Contracts at a boundary: facts a caller passes, requests, results |
| `policies.py`, `rules.py` | Pure decisions: configurable policies, statutory or contractual rules |
| `services.py`, `handlers.py` | Use cases and orchestration; one handler per event family |
| `ports.py`, `repositories.py` | Abstract dependencies and the adapters that implement them |
| `loaders.py`, `serializers.py` | Reading bundled data; persistence and textual forms |
| `validators.py` | Invariants and validation |
| `facade.py` | The single public entry of a domain, including former package re-exports |

A role that outgrows the structural limits splits into
`<role>_<suffix>.py`, for example `models_state.py` and `models_result.py`,
never into a new technical directory. The suffix is a domain word in
snake case. Tests, builders and oracles follow their own names; see
[Target trees](architecture-contract-trees.md#test-tree).

## Dependency direction

Roles form layers inside every domain and across domains:

```text
facade -> handlers / services -> ports / repositories / loaders / serializers
                              -> policies / rules / validators -> models / types / inputs / requests / results
```

- `models`, `types`, `inputs`, `requests`, `results`, `rules`, `policies`
  and `validators` never import `services`, `handlers`, `loaders`,
  `repositories`, `serializers` or `facade`. They perform no I/O.
- `ports` declare protocols over models; `repositories` and `loaders`
  implement them and may read bundled data through `importlib.resources`.
- `services` and `handlers` may import any role except `facade`.
- A `facade.py` is imported only by the package root and the public
  namespaces. Every other importer names the role file that defines the
  symbol: a model imports `contract/identity/models.py`, not
  `contract/identity/facade.py`. The migrations rewrite today's imports
  of the five re-exporting packages accordingly.
- Only the package root and the four public namespaces import `api.py`.
- Across domains, imports point from `payroll` and `comparison` towards
  `contract`, `tax`, `knowledge` and `provenance`, never back. Two current
  exceptions stay explicit and allowlisted: the capability catalog loader
  of `knowledge` builds `payroll/capability` and `payroll/assurance` models,
  and `contract/catalog` names the `payroll/period` port under
  `TYPE_CHECKING` only.
- `provenance` imports nothing but the root modules.
- The graph of `<domain>.<subdomain>` nodes has no cycle.

`tests/architecture/test_dependencies.py` enforces the current layer
direction (`api -> application -> service -> domain`). The role direction
replaces it in the same change that moves the modules.

The roles of the inventory were checked against today's runtime imports
(imports under `TYPE_CHECKING` skipped), mapping both ends of every
import to its target. Apart from the facade imports that the rule above
rewrites, one forbidden edge remains: `payroll/assurance/validators_state.py`
(today `invariants/state.py`) calls `payroll/withholding/services_carried_recovery.py`.
The `payroll` migration moves the pure computation it needs into
`payroll/withholding/rules_carried_recovery.py`. Fourteen modules whose
layer suggested a pure role but that depend on orchestration, or that are
pure although they sit in `application`, carry the role their imports
show (for example `close_tax_year.py` becomes `year/rules_close.py`,
`_pipeline_inputs.py` becomes `period/services_pipeline_input.py`).

## Guardrails

`scripts/ci/check_structure.py` records two layout rules with a hard limit
of zero against its shrink-only baseline:

| Rule | Measured on | Offender |
|---|---|---|
| `underscore_files` | `src`, `tests`, `scripts`, `demo` | a file whose name starts with `_`, except the package root `__init__.py` and the docstring-only `__init__.py` markers under `src` |
| `technical_directories` | `src`, `tests`, `scripts`, `demo` | a directory named `domain`, `application`, `service`, `handlers`, `fixtures` or `data` |

Hidden directories, `__pycache__` and the gitignored `demo/_build` and
`demo/wheels` are skipped. Every current offender is listed in
`scripts/ci/structure_baseline.json`; a new one fails, and an entry whose
offender is gone must be removed. Each migration removes its entries.

`scripts/ci/layout_inventory.py --check` keeps the inventory complete and
conforming; see
[Target trees](architecture-contract-trees.md#inventory).
