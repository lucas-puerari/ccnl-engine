# Target trees

Part of the [Architecture contract](architecture-contract.md). The trees
below are destinations: every tracked file under `src`, `tests`, `demo` and
`scripts` reaches one of them, and the [inventory](#inventory) maps the
moves of each migration.

## Data tree

The knowledge bundle stays one tree. Its datasets take the name of the
concept that reads them; inside a dataset the path is
`dataset/year/scope.json`, and a dimension that does not exist gets no
directory. A JSON name is the identity of the resource and never repeats
the path. The content of a file does not change with its path.

```text
src/ccnl_engine/knowledge/
├── manifest.json
├── agreement/<slug>.json                      from contract/agreement/
├── contribution/<year>/<sector>.json          from social_security/contribution/
├── sickness/indemnity/rates.json              from social_security/sickness/
├── sector/<year>/<sector>.json                from taxation/annual/
├── tax_credit/somma_esente/<year>.json        from taxation/exemption/
├── family/<year>.json                         from taxation/family/
├── severance/revaluation/<year>.json          from taxation/severance/
├── variable_pay/<year>.json                   from taxation/variable_pay/
├── surtax/{regional,municipal}/<year>.json    unchanged
├── capability/registry/<year>.json            from capability/<year>/catalog.json
├── limitation/engine.json                     unchanged
└── pay_item/italy.json                        from policy/
```

`sector/<year>/<sector>.json` still holds the rules of several concepts
(IRPEF brackets, the NASpI surcharge, TFR, complementary pension) for one
tax sector; splitting it changes the data and is outside the layout
migration.

## Demo, scripts and examples trees

```text
demo/
├── app.py  index.html  style.css  ui.js
├── localization/en.json  it.json
└── release/                                   build output, gitignored
    ├── site/                                  today demo/_build
    └── packages/                              today demo/wheels

scripts/
├── structure/     check.py  baseline.json
│   ├── inventory/ build.py  map.json  rules.json
│   └── naming/    rules.py
├── provenance/    check.py  assign.py  demote.py  rules.py  baseline.json
│   ├── evidence/  check.py
│   ├── fiscal/    rules.py
│   └── label/     check.py
├── knowledge/     build.py  update.py  diff.py
│   └── manifest/  build.py
├── documentation/
│   ├── capability_matrix/  contract_example/  contract_page/
│   ├── coverage_matrix/  trust_count/  limitation/   generate.py
│   └── coverage/  loaders.py
├── quality/       mutation/check.py  smoke/test.py
└── distribution/  build.py                    the hatch build hook

docs/examples/
├── quickstart/  period/  result/  fixed_term/  family/  seniority/
├── apprenticeship/  surtax/  calendar/  balance/  domestic/
├── explanation/  event/  pension_fund/  tax_year/      example.py
└── agreement/<slug>/example.py                generated, one per CCNL
```

A script is named after its action (`check`, `build`, `generate`,
`update`, `diff`, `assign`, `demote`, `report`, `test`) or after a role.
The reading order of the examples lives in the documentation index.

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
- A directory under a mirror root is a directory of the code tree it
  mirrors.
- A test module is `test_<role>.py` after the module it tests: the tests
  of `contribution/naspi/services.py` sit in
  `tests/<category>/ccnl_engine/contribution/naspi/test_services.py`.
  Tests at a mirror root test a root module (`test_api.py`). Several test
  files of one module merge; a test file above the limit splits by going
  one subdomain deeper, never with a suffix.
- Besides tests, a test directory holds `conftest.py`, `builders.py`,
  `oracles.py` and `support.py`.
- A directory of non-Python resources (`synthetic_contract`,
  `observed_payslip`, `reference_case`) may sit under the mirror directory
  of the module it exercises; it holds data only.

## Inventory

`scripts/structure/inventory.py` maps every file `git ls-files` lists
under `src`, `tests`, `demo` and `scripts` to its target, from the ordered
rules and per-file overrides of `scripts/structure/inventory_rules.json`,
and writes `scripts/structure/inventory.json`. Overrides win; otherwise the
first matching rule applies.

A target is a path, or `{"dissolve": "<dir>"}` for a package marker that
becomes part of the namespace package `<dir>`.

```bash
uv run python scripts/structure/inventory.py            # regenerate the JSON
uv run python scripts/structure/inventory.py --check    # CI gate
uv run python scripts/structure/inventory.py --summary  # counts per area
```

`--check` fails on a path no rule maps, two paths with one target, an
underscore basename other than the package root, a technical directory, a
production module whose name is not a role, a directory outside the trees,
a dissolved marker that holds code, and on drift between the rules and the
JSON.
