You have been invoked to add a new CCNL to ccnl-engine.

Follow every step in order. Do not skip ahead. Do not guess any value.
If a source cannot be found, stop and search further — never invent or borrow from another contract without independent verification.

---

## Step 0 — Merge all open PRs before starting

Run:
```bash
gh pr list --state open
```

For each open PR found, merge it automatically:
```bash
gh pr merge {PR_NUMBER} --squash --auto
```

If `--auto` is not available (branch protection not configured), merge directly:
```bash
gh pr merge {PR_NUMBER} --squash
```

Wait for each merge to complete before proceeding to the next. After all PRs are merged, sync main:
```bash
git checkout main
git pull
```

Only continue to Step 1 once `gh pr list --state open` returns no results and `main` is fully up to date.

---

## Step 1 — Select the contract

If no contract has been specified by the user, choose the one with the highest **worker headcount** not yet in the coverage matrix in `README.md`.

How to find headcount:
- Search: `CNEL archivio contratti lavoratori coperti {sector}` or
  `ISTAT lavoratori dipendenti CCNL {sector} {year}`
- CNEL contract archive: https://www.cnel.it/Contratti-Collettivi
- Ministero del Lavoro: annual report on collective bargaining coverage
- State the headcount and source explicitly before proceeding.

---

## Step 2 — Research: every parameter needs a primary source

**Acceptable primary sources**: official CCNL PDF, CNEL archive, signatory union or employer
association website (e.g. ance.it, federchimica.it, filleacgil.it, lexplain.it for tabelle
retributive confirmed by union).

**Not sufficient as sole source**: generic blogs, aggregator sites without citations, Wikipedia.

For each parameter, record the URL and the date the table was published or last updated.

### 2a. Salary tables and tranche dates

Find:
- The effective date of the current renewal (`agreement_date`)
- All tranche dates and the incremental amounts for each level
- The full table for every tranche (not just the latest)

Then immediately run the **conglobated check** (see 2b).

Common pitfall: some sources publish only the paga base increase, not the total. Others publish
the total (conglobated). Misidentifying this causes systematically wrong `gross_monthly`.

### 2b. Conglobated vs. split — mandatory check before writing any JSON

For at least **3 levels**, compute: `total_monthly_value / hourly_rate_from_official_table`.

- All results equal the same integer → values are **conglobated** (paga base + contingenza + EDR
  rolled in):
  - Model as `base_salary` (single TimeSeries per level)
  - Set `fixed_allowances: []` for every level
- Results are less than `hourly_divisor` → values are **paga base only**:
  - `base_salary` = paga base (time-series, changes each tranche)
  - `fixed_allowances` = contingenza as a separate `Allowance` (usually frozen since 1993)
  - EDR (Elemento Distinto della Retribuzione) = fixed `Allowance` if separate

### 2c. `hourly_divisor`

Derive: `total_monthly / hourly_rate`. Cross-check on ≥3 levels. All must give the same integer.

If they don't match across levels, re-examine whether the salary model is conglobated (see 2b).

Typical values: 173 (edilizia, 40h/week), 172 (terziario/turismo), 175 (chimica), 168 (some
artigianato). **Never copy — always derive.**

### 2d. `additional_months`

Find the explicit CCNL clause on mensilità aggiuntive:
- 13 = tredicesima only
- 14 = tredicesima + quattordicesima

Some CCNLs have 14 for impiegati and 13 for operai — model the dominant case and document the
exception in `coverage.notes`.

### 2e. Seniority increments (scatti di anzianità)

Find:
- Cadence in months (24 = biennale, 36 = triennale, 48 = quadriennale)
- Maximum count (e.g. 5 or 6)
- Per-level euro amounts (every level may differ)

If a category uses an alternative mechanism (e.g. APE via Cassa Edile for operai in edilizia),
model the tabular amounts as an approximation and document in `coverage.notes` as SIMPLIFICATION.

### 2f. Apprenticeship type — most error-prone parameter

**Always find the specific renewal date that governs current rules.**
The previgente CCNL and the post-renewal may use completely different models.

Two types supported by the engine:
- `percentage`: apprentice paid as % of destination level salary
  - Periods: `{ months_from, months_until, percentage }` (Decimal string, e.g. "0.80")
- `under_classification`: apprentice classified at a specific lower level code
  - Periods: `{ months_from, months_until, pay_level_code }` (must be an existing level code)

Verification procedure:
1. Find the current CCNL renewal year.
2. Search: `CCNL {sector} apprendistato {year} percentuale OR "sotto livello"`.
3. Confirm the source is dated after the renewal — previgente rules do not apply.
4. State the source URL and renewal date in `coverage.notes`.

### 2g. INPS contribution rates

Find current-year (year of implementation) values for this specific sector.

Sources in order of preference:
1. INPS annual circular for the year (e.g. "Circolare INPS n. X/2026 aliquote")
2. kitech.it (proxy — label as SIMPLIFICATION: "dati proxy, verificare circolare INPS")

What to collect:
- `employee_rate`: usually 9.19% (IVS+NASpI) — some sectors add CIGO addizionale (~0.30%)
- `employer_tiers`: list of `{ max_employees, rate }` — must end with `{ max_employees: null, ... }`
- Check if the sector has a **Cassa Edile or bilateral fund** that substitutes part of the
  employer INPS contribution. If yes, the INPS-pure rate is lower than total cost — document
  as SIMPLIFICATION and do not double-count.

IRPEF brackets and `work_deduction_breakpoints` are statutory (same across all sectors).
Copy them unchanged from any existing tax file. Do not re-research.

---

## Advisor checkpoint — end of research

**Pre-condition before calling advisor**: review every parameter found so far.
If any value was estimated, interpolated, assumed, or taken from an unverified source
rather than a confirmed primary source, **do not call advisor yet** — resolve the
ambiguity first. No trade-off on CCNL data is acceptable at this stage.

Call `advisor()` now, before writing any file.

Provide a summary of what you found:
- Contract name, CNEL code, headcount and source
- Salary model: conglobated or split, and the back-calculation result (3 levels)
- `hourly_divisor` derived value and verification levels used
- `additional_months`, seniority cadence and maximum count
- Apprenticeship type, the source URL and the renewal date it applies to
- INPS rates source and whether a bilateral fund substitutes part of the employer rate
- Any ambiguity or SIMPLIFICATION you intend to document

Do not proceed to Step 3 until the advisor has confirmed the research is sound.

---

## Step 3 — Set up the branch

```bash
git checkout main
git pull
git checkout -b chore/{id}-{datoriale}
```

The CI validates branch naming — use the pattern above, no deviations.
Never work directly on `main`. Never push directly to `main`.

---

## Step 4 — Check if engine modifications are needed

**TaxSector enum** (`src/ccnl_engine/models/ccnl.py`):
- `tax_sector` already in `TaxSector` → no change needed.
- Not present → add `NEW_SECTOR = "new_sector"` to the enum **before any other file**.
  The loader rejects JSON that references an unknown sector.

**Tax data file** (`src/ccnl_engine/tax/data/{year}-{sector}.json`):
- File already exists → reuse it (check `load_year_rules` in `src/ccnl_engine/tax/loaders.py`).
- Does not exist → create it by copying the nearest existing tax file and replacing values.
  Branch coverage on a new `TaxSector` value requires both (a) the enum value and (b) the CCNL
  JSON file in `contracts/data/` — ship both in the same commit or coverage will fail.

---

## Step 5 — Write the CCNL JSON

File: `src/ccnl_engine/contracts/data/{id}.json`

Pydantic validators enforce these invariants at load time (violations = immediate error):
- `valid_from` on the first period = exact CCNL renewal date
- `valid_until` on the last period = `null` (open-ended)
- `order` values must be unique across all levels
- Level codes must be unique
- `amount_by_level` keys must exactly match the codes present in `levels`
- `base_salary` must be non-decreasing over time within each level
- Higher `order` = higher or equal salary at every tranche date

`sources` array: at least one entry per primary source used (url + type + agreement_date).
`extraction.timestamp`: ISO 8601 date of today.
`extraction.human_reviewed`: true.

Validate immediately after writing:
```bash
uv run python -c "from ccnl_engine.contracts.loaders import load_ccnl; load_ccnl('{id}.json')"
```
Fix all Pydantic errors before continuing. Do not proceed with broken JSON.

---

## Step 6 — Compute the golden case with the engine

**Never compute expected values by hand.** Run the engine and capture the output:

```python
from datetime import date
from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.engine.compute import Scenario, compute
from ccnl_engine.models.ccnl import TaxSector
from ccnl_engine.models.employment import Permanent

ccnl  = load_ccnl("{id}.json")
rules = load_year_rules({year}, TaxSector.{SECTOR}, num_employees=50)
result = compute(
    ccnl,
    rules,
    Scenario(level_code="{level}", as_of=date({year}, {mm}, 1), employment=Permanent()),
)
```

Choose: mid-range level, no seniority (`seniority_count=0`), permanent, 50 employees,
date on the second tranche.

Save to `tests/ccnl_engine/golden/cases/{id}_{level}_{year}.json`.

---

## Step 7 — Write unit tests

Append class `TestLoad{CamelCaseName}` at the bottom of
`tests/ccnl_engine/data/test_data_files.py`.

**Required imports at the top of the file** — add only what is missing (never inside methods):
```python
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.ccnl import CCNL, TaxSector
```
Imports inside test methods trigger ruff PLC0415 and fail CI.

**Required 10 test methods:**

| Method | Checks |
|--------|--------|
| `test_{id}_loads` | `id == "{id}"`, `cnel_code == "{CNEL}"` |
| `test_{id}_has_{N}_levels` | `len(levels) == N` and exact code set |
| `test_{id}_level{X}_salary_{tranche1}` | `Decimal("{value}")` at first tranche date |
| `test_{id}_level{X}_salary_{tranche2}` | `Decimal("{value}")` at second tranche date |
| `test_{id}_level_ordering` | highest-order code and lowest-order code |
| `test_{id}_additional_months` | `Decimal(13)` or `Decimal(14)` |
| `test_{id}_hourly_divisor` | integer value |
| `test_{id}_no_fixed_allowances` | all levels `== []` (conglobated model only) |
| `test_{id}_tax_sector` | `TaxSector.{SECTOR}` |
| `test_{id}_seniority_cadence` | `cadence_months == N`, `maximum_count == M` |

**Docstring length**: every docstring must stay under 88 characters. Ruff E501 applies to
docstrings too — count before saving.

---

## Step 8 — Update README.md

Add one row to the coverage matrix table:
```
| {CCNL Name} | {Sector} | ✅ | ✅ |
```

---

## Step 9 — Final checks

All three must pass before committing:

```bash
uv run pytest                   # 100% branch coverage — hard requirement
uv run ruff check src/ tests/   # zero errors; line limit 88 chars
uv run mypy src/ tests/         # zero errors, strict mode
```

If pytest reports < 100% coverage, identify the uncovered branch before committing.
Most common cause: new `TaxSector` enum value has no JSON file in `data/` yet — the
parametrized `test_file_validates` test never executes that enum branch.

---

## Advisor checkpoint — end of implementation

**Pre-condition before calling advisor**: confirm that every value in the JSON file
traces back to a primary source with no assumption or approximation that has not
been explicitly marked as SIMPLIFICATION. No trade-off on CCNL data is acceptable
at this stage — if any parameter is uncertain, find the source first.

Call `advisor()` now, before committing.

Provide:
- All three check results (pytest coverage %, ruff output, mypy output)
- The 10 test method names and what each verifies
- Any SIMPLIFICATION you included and why it is acceptable
- Any deviation from the standard JSON schema or engine model

Do not proceed to Step 10 until the advisor has confirmed the implementation is ready to ship.

---

## Step 10 — Commit and PR

**Commit message**: single line only. The git hook rejects multi-line messages.
```
feat({id}): add CCNL {Name} ({CNEL code}) payroll engine
```

**Branch**: `chore/{id}-{datoriale}` (CI validates branch naming pattern).

**Never push directly to `main`.** All changes go through a PR.

**PR body** — exact structure:

```
## What
[files created/modified and the role of each]

## Why
[which coverage gap this fills; headcount or business rationale; CNEL code]

## How
[conglobated or split and how verified; hourly_divisor derivation; seniority
cadence and source; apprenticeship type with source and renewal date;
new TaxSector if any; key SIMPLIFICATIONs and their scope]

## Verification
[N tests passed, 100% branch coverage, ruff clean, mypy strict]
```

---

## Known pitfalls

- **Apprenticeship type**: always verify against the actual renewal year. A pre-renewal CCNL
  may use `under_classification` while the post-renewal switched to `percentage` — secondary
  sources often describe the old model without flagging it.
- **Conglobated misidentification**: skipping the back-calculation causes `gross_monthly`
  understated by ~30% (paga base only instead of total).
- **Scatti cadence**: biennale (24), triennale (36), quadriennale (48) — never assume.
- **`amount_by_level` codes**: must match `levels[].code` exactly — a mismatch is a load error.
- **Docstring overflow**: ruff E501 applies to docstrings. Long test descriptions overflow 88
  chars. Check before running ruff.
- **Top-level imports**: ruff PLC0415 rejects imports inside test methods. Always add at the
  top of the file.
- **Multi-line commit message**: the git hook rejects it. One line only.
- **Coverage gap on new TaxSector**: ship enum change + tax file + CCNL JSON in the same commit.

---

## Hard constraints

- No value without a primary source.
- No parameter copied from another contract without independent verification.
- No trade-off on CCNL data: every parameter must be confirmed before calling advisor.
  If a value cannot be verified, stop and search further — never approximate or assume.
- No PR before `pytest` reaches 100% branch coverage.
- Commit message: single line.
- Never push directly to `main` — not even for tooling, skills, or documentation.
- Do not open a PR with failing or skipped tests.
- Do not start a new contract if any PR is still open — merge first, then begin.
