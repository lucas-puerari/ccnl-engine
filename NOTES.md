# Implementation notes

## Commit order interpretation

The "models → engine → data → tests" order describes feature groups, not a statement
about deferring unit tests. CI enforces `pytest --cov-fail-under=100` on every push,
so no module can ever be committed without its unit tests. Each module commit bundles
its own unit tests. The "tests" stage refers specifically to golden/integration tests
in `tests/golden/`, which depend on real CCNL + tax data existing first.

## Directory naming

The project prompt specifies `src/ccnl_engine/models/` (plural) and
`src/ccnl_engine/engine/`. The scaffold had `model/` (singular, empty stub) and no
`engine/`. Decision: follow the prompt's naming; the empty stubs had no users and
created a confusing divergence. The existing empty `engine/` directory already existed
and only needed an `__init__.py`.

## Tax models location

`YearRules` and related tax models live in `src/ccnl_engine/tax/models.py` (prompt is
silent on this). Tax data (`tax/data/2026.json`) is co-located with the tax models.
The loader (`load_year_rules`) lives in `src/ccnl_engine/data/__init__.py` alongside
`load_ccnl`, since both are data-loading concerns.

## Golden test equality

Golden tests use exact `Decimal` equality (not `pytest.approx`). All arithmetic uses
Python `Decimal` with a single `money()` rounding point — the computation is fully
deterministic. Tolerance would silently mask regressions.

## INPS employer rate assumption

The `2026.json` employer rate (28.98%) assumes commerce sector, ≤50 employees, CUAF
intera (Table 7.1). This is declared explicitly in the JSON. Users with different
company sizes must override `YearRules` accordingly.

## IRPEF 2026 second bracket

The second IRPEF bracket is **33%** (not 35%), effective from 1 January 2026 per
Legge di Bilancio 2026 (L. 199/2025). Source: fiscomania.com citing L. 199/2025,
corroborated by AdE portal.

## Art. 13 TUIR deduction — gap

The exact 2026 Art. 13 TUIR work-income deduction breakpoints were not retrieved from
a primary source during initial research. The `work_income_deduction` function in
`engine/irpef.py` uses a `# SIMPLIFICATION:` placeholder until the values are
verified. The golden test net-salary fields are `null` until this gap is filled.

## Salary TimeSeries — single period

Only the November 2025 (4th tranche) salary values were verified from primary sources.
Pre-November-2025 tranche values must be fetched from the original CCNL text to
complete the TimeSeries back to the previous renewal. The current JSON uses a single
period (`valid_from: 2025-11-01, valid_until: null`) which is valid for computing
salaries as of late 2025 or 2026 (before the November 2026 5th tranche).

## Seniority increment amounts — medium confidence

Scatti amounts per level (€19.47–€25.46) come from affarifinanza.it and bustaia.it.
These should be verified against the original CCNL Art. 187 text before production
use. Structure (10 triennali) confirmed by multiple sources.

## Apprenticeship — gap

The specific apprenticeship mechanism for CCNL Commercio (percentage vs.
under-classification) was not retrieved during initial research. The JSON uses
`"type": "percentage"` as a default assumption with a note in `coverage.notes`.
Must be verified against CCNL Art. 42–53 before the implementation is considered
complete.
