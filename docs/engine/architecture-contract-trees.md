# Target trees

Part of the [Architecture contract](architecture-contract.md). The trees
below are destinations, not a selection: every tracked file under `src`,
`tests`, `demo` and `scripts` has exactly one entry in the
[inventory](#inventory).

## Data tree

The knowledge bundle orders its path as `domain/dataset/year/scope.json`.
A dimension that does not exist gets no directory: an agreement carries its
validity in the document, and the engine limitations and the INPS sick-pay
table have no year in their path. A JSON name is the identity of the
resource in the last dimension and never repeats the path.

```text
src/ccnl_engine/knowledge/
├── contract/agreement/<slug>.json             from ccnl/data/<slug>.json
├── social_security/
│   ├── contribution/<year>/<sector>.json      from inps/data/<year>-<sector>.json
│   └── sickness/rates.json                    from inps/data/sick-pay-rates.json
├── taxation/
│   ├── annual/<year>/<sector>.json            from tax/data/<year>-<sector>.json
│   ├── family/<year>.json                     from tax/data/family-deductions-<year>.json
│   ├── exemption/<year>.json                  from tax/data/somma-esente-<year>.json
│   ├── variable_pay/<year>.json               from tax/data/variable-pay-rules-<year>.json
│   └── severance/<year>.json                  from tax/data/tfr-revaluation-<year>.json
├── surtax/
│   ├── regional/<year>.json                   from surtax/data/regionale-<year>.json
│   └── municipal/<year>.json                  from surtax/data/comunale-<year>.json
├── capability/<year>/catalog.json             from capabilities/data/<year>.json
├── limitation/engine.json                     from limitations/data/engine.json
└── policy/italy.json                          from policies/data/it.json
```

The knowledge loaders sit at `knowledge/loaders.py`,
`knowledge/loaders_resource.py` and `knowledge/validators.py`; the loaders
of one dataset sit in its directory (`knowledge/capability/loaders.py`,
`knowledge/limitation/loaders.py`). The bundle version moves from
`knowledge/__init__.py` to `knowledge/facade.py`. The manifest
(`knowledge/manifest.json`) belongs to the knowledge migration and is not
part of this contract.

## Demo and scripts trees

```text
demo/
├── app.py  index.html  style.css  ui.js
├── localization/en.json  it.json             from i18n/
└── release/                                   build output, gitignored
    ├── site/                                  today demo/_build
    └── packages/                              today demo/wheels and demo/_build/wheels

scripts/
├── structure/   check.py  baseline.json  inventory.py  inventory_rules.json  inventory.json
├── provenance/  check.py  baseline.json  evidence.py  labels.py  rules.py
│                assign.py  demote.py  fiscal.py
├── knowledge/   build.py  update.py  diff.py
├── documentation/ generate_capability_matrix.py  generate_contract_examples.py
│                generate_contract_pages.py  generate_coverage_matrix.py
│                generate_trust_counts.py  coverage.py  limitations.py
├── quality/     mutation.py  smoke_test.py
└── distribution/ build.py                     the hatch build hook
```

Scripts are grouped by the object they operate on and named after the
action. The five documentation generators keep one file each, split by the
`<role>_<suffix>.py` rule, since merging them would change their entry
points. `demo/release` holds gitignored build output only, so it has no
entry in the file inventory.

## Test tree

```text
tests/
├── conftest.py  README.md
├── knowledge/
│   └── ccnl_engine/   normative oracles, legal scenarios, reference and observed payslips
├── unit/
│   └── ccnl_engine/   one unit, no I/O, no real bundle
└── integration/
    ├── ccnl_engine/   public API, loaders, repositories, wiring, persistence
    ├── demo/
    └── scripts/
```

- A category holds at most the mirror roots `ccnl_engine`, `demo` and
  `scripts`; an absent one is not created.
- A directory under a mirror root is a directory of the target code tree it
  mirrors. A dataset directory of non-Python resources may sit right below
  one (`payroll/period/observed_payslip/`, `contract/catalog/synthetic_contract/`).
- A mirrored unit or integration test is named
  `test_<target module stem>[_<behaviour>].py`: it takes the stem of the
  module it mirrors after the move, so
  `tests/unit/ccnl_engine/payroll/domain/test_ledger.py` becomes
  `tests/unit/ccnl_engine/payroll/ledger/test_models.py`. Knowledge
  tests, public API tests and repository-rule tests keep descriptive
  names (`test_pension_fund_prevedi.py`, `test_public_exports.py`).
- Besides tests, a test directory holds `conftest.py`, `builders[_x].py`
  (request and state builders), `oracles[_x].py` (normative oracles) and
  `support[_x].py` (helpers of a test family).
- Builders and oracles shared across categories live with the category of
  their main consumer; another category may import them. Tests never import
  each other.
- At most five directories sit under `tests` before a file.

Where the current tests go:

| Today | Target |
|---|---|
| `tests/unit/ccnl_engine/...`, `tests/integration/...` | the same category, mirrored on the target module |
| `tests/acceptance/public_api/` | `tests/integration/ccnl_engine/` (the public surface is the root) |
| `tests/acceptance/legal_scenarios/` | `tests/knowledge/ccnl_engine/payroll/<subdomain>/` of the verified rule |
| `tests/architecture/` | `tests/integration/scripts/<domain>/` for repository rules, `tests/integration/ccnl_engine/` for the public API, errors and input defaults, `tests/knowledge/ccnl_engine/` for data quality, limitations and observed payslips |
| `tests/fixtures/*.py` | `builders_*.py` next to their main consumer |
| `tests/fixtures/normative_oracles/` | `oracles_*.py` in `tests/knowledge/ccnl_engine/payroll/<subdomain>/` |
| `tests/fixtures/reference_tables/` | `tests/knowledge/ccnl_engine/payroll/period/reference_case/` |
| `tests/fixtures/observed_payslips/` | `tests/knowledge/ccnl_engine/payroll/period/observed_payslip/` |
| `tests/fixtures/synthetic_contracts/` | `tests/integration/ccnl_engine/contract/catalog/synthetic_contract/` |
| `tests/helpers.py` | `tests/unit/ccnl_engine/builders.py` |

## Inventory

`scripts/structure/inventory.py` maps every file `git ls-files` lists
under `src`, `tests`, `demo` and `scripts` to its target, from the ordered
rules and per-file overrides of `scripts/structure/inventory_rules.json`,
and writes `scripts/structure/inventory.json`. Overrides win; otherwise the
first matching rule applies. Data, demo, public API and legal scenario
files map by pattern; every production module below the root and every
script has an override;
unit and integration tests map through the module they mirror. Default
rules per current directory place a new production module provisionally
(a new `payroll/application/period/_x.py` goes to
`payroll/period/services_x.py`); give it an override as soon as its
subdomain or role differs.

A target is a path, or `{"dissolve": "<dir>"}` for a package marker that
becomes part of the namespace package `<dir>`. Only an `__init__.py` with
nothing but a docstring may dissolve; the five markers with code (the root,
`contract/domain/identity`, `knowledge`, `payroll/domain/events` and
`payroll/domain/pay_items`) map to a file.

```bash
uv run python scripts/structure/inventory.py            # regenerate the JSON
uv run python scripts/structure/inventory.py --check    # CI gate
uv run python scripts/structure/inventory.py --summary  # counts per area
```

`--check` fails on a path no rule maps, two paths with one target, an
underscore basename other than the package root, a technical directory, a
depth above the limits, a production module whose name is not a role, a
directory outside the trees above, a dissolved marker that holds code, and
on drift between the rules and the JSON.

The `payroll` package maps its 264 files into 16 subdomains (252 modules,
12 dissolved markers):

| Subdomain | Modules | Subdomain | Modules |
|---|---:|---|---:|
| `period` | 30 | `employment` | 14 |
| `contribution` | 30 | `state` | 14 |
| `taxation` | 28 | `sickness` | 12 |
| `amount` | 19 | `capability` | 9 |
| `assurance` | 18 | `accrual` | 8 |
| `event` | 17 | `family` | 7 |
| `year` | 17 | `ledger` | 7 |
| `withholding` | 15 | `termination` | 7 |
