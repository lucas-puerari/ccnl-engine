# Architecture contract

This page fixes the layout of the repository and the names it uses.
[Architecture rules](architecture.md) states how the layout is checked.

The package moves from a layout by source (`contract` for the CCNL,
`tax` for the statutory tables, `payroll` for the computation) to a layout
by concept: one root per concept (`sickness`, `contribution`, `irpef`), with
the CCNL rules, the statutory tables and the computation of that concept
below it.

The contract has four pages:

- this page: principles, decisions, the production tree, the concepts, the
  roles and the dependency tiers;
- [Target trees](architecture-contract-trees.md): the data, `demo`,
  `scripts`, examples and test trees;
- [Production map](architecture-contract-map.md): the target of every
  current production module;
- [Migration notes](architecture-contract-migration.md): the namespace
  package spike, the path-keyed data a move must update, and the
  amendments.

## Principles

- A directory is a plain domain name: a concept, or a subdomain of one. A
  file is exactly a technical role. No `<role>_<subject>.py`, no
  `<subject>_<role>.py`: two files with one role in one domain go one domain
  level deeper (`contribution/pension_fund/decision/services.py`).
- Depth is not limited: it follows the domain.
- Every directory name is listed in the "Directory names" section of the
  [glossary](../domain/glossary.md); right below the package root only a
  concept. One concept uses one term in production code, knowledge data,
  scripts and tests; a name means one thing wherever it appears.
- No file name starts with an underscore, except the package root
  `src/ccnl_engine/__init__.py` and the docstring-only package markers.
- Every source directory keeps a package marker: an `__init__.py` holding
  only a docstring. The documentation tooling (griffe, behind
  mkdocstrings) does not load a namespace directory inside a regular
  package. Test directories carry no marker: pytest imports them by path.
- A leaf directory holds only the roles it needs. No empty file is created
  for symmetry.
- A move keeps the persisted identities: ruleset ids (`tax/2026/...`,
  `inps/2026/...`), `ccnl_id` values and the tags of the state codec do
  not follow the directories.

## Decisions

| Topic | Decision |
|---|---|
| Package root | `src/ccnl_engine/__init__.py` stays, with its docstring and its re-exports. |
| Public API | The root and the namespaces `ccnl_engine.inputs`, `ccnl_engine.events`, `ccnl_engine.results` and `ccnl_engine.catalog` keep their import paths, as pinned by `tests/integration/ccnl_engine/api/test_public_exports.py`. |
| `catalog` | Becomes the package `catalog/`: its `__init__.py` holds the public namespace, like the package root, the only other `__init__.py` allowed to hold code; the catalog modules (`loaders`, `models`, `services`) sit next to it. |
| Root modules | `api`, `inputs`, `results`, `events`, `errors`, `version`, plus the roles `types` (today `primitives`) and `validators` (today `validation`); `validation_collection` becomes `collection/validators.py`. No alias: nothing outside the package imports the old names. |
| Deep imports | Paths below the five public modules are not public. Moves carry no shim and no deprecation alias. |
| Knowledge data | The JSON bundle stays in one tree, `knowledge/`, with its datasets named after the concepts that read them. |

## Production tree

```text
src/ccnl_engine/
├── __init__.py  api.py  inputs.py  events.py  results.py
├── errors.py  types.py  validators.py  version.py
├── catalog/  collection/
├── agreement/        the CCNL document: identity, metadata, validity, coverage
├── compensation/     levels, allowances, pay elements, proration, renewal minimum
├── pay_item/         pay item variants, treatment, rounding, policy
├── employment/  employer/  apprenticeship/  seniority/
├── working_time/  absence/  sickness/  extra_month/  termination/
├── contribution/     INPS: rates, bases, ceiling, NASpI, domestic, apprentices
├── fund/  pension_fund/  severance/  end_of_service/
├── irpef/  tax_credit/  surtax/  regime/  variable_pay/  family/
├── withholding/  ledger/  event/  balance/
├── decision/  assurance/  reconciliation/  limitation/  capability/
├── run/  period/  year/  default/  calendar/  amount/
├── knowledge/        the JSON datasets and their manifest, data only
├── bundle/  sector/  readers of the bundle; the rules of a tax sector and year
├── provenance/  comparison/
```

The subdomains of each concept are in
[Production map](architecture-contract-map.md).

## Concepts

| Concept | Holds |
|---|---|
| `agreement` | A CCNL as a document: root model, identity, metadata, validity and time series, coverage notes |
| `catalog` | The public catalog: bundled contracts, discovery, ruleset readiness |
| `compensation` | Levels and allowances, the pay elements of a level, proration, hourly pay and its percentages, renewal minimum, raccordo and provincial elements |
| `pay_item` | Pay item variants, their treatment, selection policy and rounding |
| `employment`, `employer` | The employment relationship and its facts; the employer profile |
| `apprenticeship`, `seniority` | Apprentice tracks and pay; seniority increments and their ladder |
| `working_time`, `absence` | Working time, overtime and leave; absences |
| `sickness` | Episodes, sick days, CCNL integration, INPS indemnity, cumulation |
| `extra_month` | Tredicesima and quattordicesima: entitlement, schedule, ratei, settlement, liquidation |
| `termination` | Termination events and their handlers |
| `contribution` | INPS rates, bases, ceiling, minimum base, NASpI, domestic work, apprentices, ENAM |
| `fund`, `pension_fund` | Contractual funds of the CCNL; the complementary pension fund |
| `severance`, `end_of_service` | TFR: accrual, provision, revaluation, relief, public reduction; the public end-of-service fund |
| `irpef`, `tax_credit`, `surtax` | IRPEF; credits paid on the payslip and their recovery; regional and municipal surtax |
| `regime`, `variable_pay`, `family` | Substitute tax regimes; variable pay and benefits; art. 12 TUIR deductions |
| `withholding`, `ledger`, `event` | What a run withholds; ledger entries and remittance; work events |
| `balance` | What a run opens and closes with: competence, tax cash, YTD accounts, obligations, opening balances, the state codec |
| `decision`, `assurance`, `reconciliation`, `limitation` | Calculation decisions and the decisions of a run; payability; result invariants; model limitations |
| `capability` | Capability registry, requirements, traces and reports |
| `run`, `period`, `year`, `default` | The run identity and its month; one payroll run; competence and tax years; defaults of the public inputs |
| `calendar`, `amount` | The payroll calendar: schedules, payment identity, tax year of a payment; the amounts of a run |
| `knowledge` | The JSON data bundle and its manifest, data only |
| `bundle`, `sector` | Readers of the bundle: manifest, resources, hash and label checks; the rules of a tax sector and year |
| `provenance`, `comparison` | Ruleset and source provenance; the rules diff of a CCNL |
| `collection` | Validators of the public collections |
| `codec`, `interchange` | The tagged JSON tree of engine values; the JSON forms of the public inputs and results |

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
| `facade.py` | The single public entry of a domain |

A role that outgrows the structural limits moves part of its content into a
subdomain directory with the same role file; it never takes a suffix.

## Dependency tiers

Every concept sits in one tier. A module imports at runtime only concepts of
its own tier or of a lower one; cycles inside a tier are allowed.

| Tier | Concepts |
|---|---|
| orchestration | `api`, `inputs`, `events`, `results`, `catalog`, `assurance`, `capability`, `comparison`, `default`, `interchange`, `period`, `reconciliation`, `year` |
| computation | `agreement`, `amount`, `bundle`, `calendar`, `decision`, `knowledge`, `sector`, `limitation`, `balance`, `absence`, `apprenticeship`, `compensation`, `contribution`, `employer`, `employment`, `end_of_service`, `event`, `extra_month`, `family`, `fund`, `irpef`, `ledger`, `pay_item`, `pension_fund`, `regime`, `seniority`, `severance`, `sickness`, `surtax`, `tax_credit`, `termination`, `variable_pay`, `withholding`, `working_time` |
| norms | `types`, `validators`, `errors`, `version`, `codec`, `collection`, `provenance`, `run` |

A root module (`api.py`, `inputs.py`) is a concept of its own; the package
root `__init__.py` holds the public namespace and has no tier. Imports under
`if TYPE_CHECKING:` do not count.

The migration resolved the imports from computation into orchestration by
moving the shared helpers and types to the tier of their users
(`pay_item/services.py`, `decision/rules.py`, `calendar/`, `amount/`,
`limitation/types.py`). The upward imports that remain are listed here, by
module; any other fails `scripts/architecture/check.py`, and so does a
listed one that no longer exists.

| Importer | Imported | Reason |
|---|---|---|
| `contribution/ceiling/services.py` | `capability/rule/services.py` | The INPS ceiling decision cites the payable rules of the run through the capability rule lookup |
| `contribution/decision/services.py` | `capability/rule/services.py` | The INPS rate decision cites the payable rules of the run through the capability rule lookup |
| `seniority/services.py` | `capability/rule/services.py` | The seniority decision cites the payable rules of the run through the capability rule lookup |

A module under `src/ccnl_engine` holds at most 300 lines. The modules
longer than that on 2026-10-19 are listed in
`scripts/architecture/baseline.json`; each may only shrink, and a module
leaves the list once it fits.

Inside a concept the role direction holds:

```text
facade -> handlers / services -> ports / repositories / loaders / serializers
                              -> policies / rules / validators -> models / types / inputs / requests / results
```

Pure roles perform no I/O, and only the package root and the public
namespaces import `api.py` or a `facade.py`.
