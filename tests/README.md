# Test suite

The layout below is binding: `tests/architecture/test_test_layout.py`
enforces the folders, the mirror rule and the depth, and
`scripts/structure/check.py` the size of each test file.

## Levels

```text
tests/
├── unit/                    one pure function or object: no bundle, no I/O
├── integration/             several real components: loaders, bundle, pipeline, state
├── acceptance/
│   ├── public_api/          only `ccnl_engine` and its public namespaces
│   └── legal_scenarios/     end to end against an independent normative oracle
├── architecture/            static rules of the repository
└── fixtures/                support data and builders; never tests
```

Inside `unit/` and `integration/` the path mirrors the module under test:
`src/ccnl_engine/x/y/z.py` (or `_z.py`, or a package `z/`) is tested by
`tests/<level>/ccnl_engine/x/y/test_z.py` or `test_z_<behaviour>.py`.
Tooling is mirrored the same way under `integration/scripts/` and
`integration/demo/`.  Do not create a `domain/`, `service/` or
`application/` folder that the source does not have.

At most five directories under `tests/` before a file (`fixtures/` aside).

## Ownership

Each behaviour has one owning level; another level may touch it, but only
for what it alone can show.

| Level | Owns |
|---|---|
| unit | formula, value object, local boundary |
| integration | wiring, loaders, pipeline, state transitions |
| acceptance/public_api | contract and shape visible to the consumer |
| acceptance/legal_scenarios | correctness against an independent source |
| architecture | static rules of the repository |

An acceptance test checks a few public outcomes, the assurance and the
lineage; it does not repeat every assertion of the unit test.  Share input
builders through `fixtures/`; do not share helpers that hide assertions,
since they make an oracle opaque.

A regression test goes into the file of the behaviour it protects, named
after that behaviour, not into a file collecting past bugs.  Strict xfails
document a known wrong result: keep their reason and the error they raise.

## Fixtures

| Folder or module | Holds |
|---|---|
| `fixtures/reference_tables/` | reference cases: one regular period pinned to a signed salary table, checked by `scripts/provenance/check.py` |
| `fixtures/normative_oracles/` | hand-written calculators of the rules (IRPEF, family deductions, surtaxes), written from the sources without importing the engine |
| `fixtures/normative_oracles/payslips/` | full-payslip oracles built on the rule oracles |
| `fixtures/observed_payslips/` | anonymous transcriptions of real and teaching payslips (one JSON per payslip, amounts as printed): evidence of how payrolls apply the rules, never a signed source. Part of them is converted from the gold annotations of the BurocrazIA dataset (albertobarnabo/burocrazia on Hugging Face, Apache-2.0) |
| `fixtures/synthetic_contracts/` | expected CCNL values the bundled-contract loader tests compare against |
| `fixtures/*.py` | request, state and schedule builders shared by several tests |

Name a fixture after its role, never `data`, `expected` or `samples`.

## Duplicates and inventory

`tests/architecture/test_duplicate_tests.py` fails on any exact duplicate:
two tests with the same body, decorators, arguments and class fields, using
names imported from the same modules.  It does not see conceptual
duplicates, the same boundary asserted at several levels with different
inputs.  For those, print the inventory:

```bash
uv run python -m tests.architecture._test_inventory
```

It counts the tests owning each capability per level and lists the
modules tested at more than one level: check that each level asserts
something the others do not.
