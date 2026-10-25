# Test suite

The layout below follows the
[Architecture contract](../docs/engine/architecture-contract-trees.md#test-tree):
three categories, directories that mirror the code, test files named after the
role of the module they test, or kept in the directory of that module.

## Categories

```text
tests/
├── conftest.py  README.md
├── knowledge/
│   └── ccnl_engine/   legal scenarios, normative oracles, reference and observed payslips
├── unit/
│   └── ccnl_engine/   one pure function or object: no bundle, no I/O
└── integration/
    ├── ccnl_engine/   public API, loaders, repositories, pipeline, state
    ├── demo/
    └── scripts/       tooling and the static rules of the repository
```

Under each category the path mirrors the code: a directory of
`tests/<category>/ccnl_engine/` is a directory of `src/ccnl_engine/`, or
the directory of one module (`period/services/` holds the tests of
`period/services.py`); of
`integration/scripts/` one of `scripts/`, of `integration/demo/` one of
`demo/`. A dataset directory of JSON may sit right below one
(`period/reference_case/`, `catalog/synthetic_contract/`). The few knowledge
directories that group tests by theme are listed, with their reason, in
`scripts/quality/test_tree/check.py`, which `make architecture` and CI run.

A unit test, and an integration test below a mirror root directory, is
named after the module it tests: `src/ccnl_engine/x/y/z.py` is tested by
`tests/<category>/ccnl_engine/x/y/test_z.py` or `test_z_<behaviour>.py`.
Knowledge tests, the public API tests at the root of
`integration/ccnl_engine/` and the repository-rule tests of
`integration/scripts/` keep descriptive names
(`test_pension_fund_prevedi.py`, `test_public_exports.py`).

A knowledge test, and a public API test, imports `ccnl_engine` only through
the public API: the root and `ccnl_engine.inputs`, `.events`, `.results`
and `.catalog`.

Besides tests, a directory holds only `conftest.py`, `builders[_x].py`
(request and state builders), `oracles[_x].py` (normative oracles) and
`support[_x].py` (helpers of a test family). A builder or oracle lives with
the category of its main consumer; another category may import it. Tests
never import each other. At most five directories under `tests/` before a
file.

## Ownership

Each behaviour has one owning category; another may touch it, but only for
what it alone can show.

| Category | Owns |
|---|---|
| unit | formula, value object, local boundary |
| integration, below a mirror root directory | wiring, loaders, pipeline, state transitions |
| integration, root of `ccnl_engine/` | contract and shape visible to the consumer |
| integration, `scripts/` | tooling and the static rules of the repository |
| knowledge | correctness against an independent source |

A public API or knowledge test checks a few public outcomes, the assurance
and the lineage; it does not repeat every assertion of the unit test. Share
input builders; do not share helpers that hide assertions, since they make
an oracle opaque.

A regression test goes into the file of the behaviour it protects, named
after that behaviour, not into a file collecting past bugs. Strict xfails
document a known wrong result: keep their reason and the error they raise.

## Knowledge data

| Path under `knowledge/ccnl_engine/` | Holds |
|---|---|
| `period/reference_case/` | reference cases: one regular period pinned to a signed salary table, checked by `scripts/provenance/check.py` |
| `<concept>/oracles.py` | hand-written calculators of the rules (IRPEF, family deductions, surtaxes, contributions, withholding), written from the sources without importing the engine |
| `period/oracles.py` | full-payslip oracles built on the rule oracles |
| `period/observed_payslip/` | anonymous transcriptions of real and teaching payslips (one JSON per payslip, amounts as printed): evidence of how payrolls apply the rules, never a signed source. Part of them is converted from the gold annotations of the BurocrazIA dataset (albertobarnabo/burocrazia on Hugging Face, Apache-2.0) |

`integration/ccnl_engine/catalog/synthetic_contract/` holds the
expected CCNL values the bundled-contract loader tests compare against.
Name a dataset after its role, never `data`, `expected` or `samples`.
