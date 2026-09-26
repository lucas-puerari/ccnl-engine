# ccnl-engine

Python engine for auditable Italian payroll simulations: CCNL-aware gross-to-net and
employer cost, versioned rules, provenance, and an explicit status on every result.
Built for technical teams in HR, payroll, and compensation.

[**Demo**](../demo/) · [**GitHub**](https://github.com/lucas-puerari/ccnl-engine) · [**CCNL coverage**](contracts/index.md)

---

## Four pillars

| Pillar | What it covers |
|---|---|
| **Domain** | How Italian labor law and CCNLs are represented as typed models |
| **Rules** | The versioned knowledge base: CCNL tables, INPS rates, IRPEF brackets |
| **Engine** | How rules are applied to produce a reproducible payroll figure |
| **Trust** | Provenance, calculation status, versioning, and reference cases that make results verifiable |

---

## Documentation

| Section | Description |
|---|---|
| [Get started](getting-started/index.md) | Install, quickstart, and first payroll in 10 lines |
| [Domain](domain/index.md) | What CCNLs are, Italian labor law, employment types |
| [Rules](rules/index.md) | The versioned knowledge base: CCNL JSON schema, INPS, IRPEF, surtax |
| [Engine](engine/index.md) | How to use `PayrollEngine` — pay components, fiscal, domestic work |
| [Trust](trust/index.md) | Provenance, calculation status, capability report, versioning, quality gates |
| [Data operations](trust/data-operations.md) | Update policy, changelog, error reporting, version compatibility |
| [Correctness layers](trust/correctness.md) | Software, source, and case correctness — what each layer means and how to read them |
| [Contracts](contracts/index.md) | All 125 supported contracts — salary tables, sources, coverage |
| [API reference](api/index.md) | Full reference for every public type and function |

---

## Why trust a number from this engine?

Every result carries three verifiability layers:

1. **Provenance**: each rule links to its primary source document (CCNL article,
   INPS circular, tax schedule) with a URL, section, and verification status.
2. **Versioning**: `result.bundle_version` records the knowledge-base version,
   so any figure can be reproduced after a CCNL renewal by pinning the package.
3. **Status and decisions**: `result.status` is `final`, `provisional`,
   `incomplete` or `rejected`; `result.issues` says what lowered it,
   `result.decisions` what each capability decided and from which inputs, and
   `result.capability_report` which catalog features the run did not execute.
   An unknown normative fact never yields a `final` result.

```python
from ccnl_engine import CalculationStatus

if result.status is not CalculationStatus.FINAL:
    for issue in result.issues:
        print(issue.code, issue.status, issue.message)
for decision in result.decisions:
    print(decision.capability, decision.reason_code, decision.amount)
for gap in result.capability_report.gaps:
    print(gap.feature, gap.kind.value)
```

See [example 11: Why this number?](examples/11_why_this_number.py) for a
full walkthrough.

---

## Scope

**Always computed (L1: gross, L2: net):**

- IRPEF gross and net (Art. 11-13 TUIR), work income deductions,
  *trattamento integrativo* (Art. 1 D.L. 3/2020)
- Regional and municipal income tax surcharges
  (*addizionale regionale e comunale IRPEF*)
- INPS contributions (employee and employer), resolved by headcount tier
- TFR accrual
- Contractual employer funds
- Part-time scaling, seniority increments, fixed allowances
- Apprenticeship contracts (under-classification and percentage tracks)
- Fixed-term contracts (NASpI *addizionale*)
- Domestic work (flat per-hour contributions, non-withholding employer)

Second-level (territorial and company) allowances are not an engine input.

**L3: work rules (125/125 contracts):**

Work events are part of the run: pass them in `PeriodFacts.events` and they
change gross, net and employer cost according to their treatment. See
[Work rules](engine/work-rules.md).

- Overtime pay (lavoro straordinario) with caller-supplied rate: `OvertimeEvent`
- Night, holiday and shift supplements, with the 2026 substitute tax:
  `NightShiftEvent`, `HolidayWorkEvent`, `ShiftWorkEvent`
- Unpaid absences and sickness: `AbsenceEvent`, `SickLeaveEvent`, `SicknessCaseEvent`
- Bonuses (ordinary, *premio di risultato* with its flat tax, renewal
  increments): `BonusEvent`
- Welfare and fringe benefits: `WelfareEvent`, `FringeEvent`

**Opt-in facts:**

- Family-dependent deductions (Art. 12 TUIR): `PeriodFacts.family_composition`
- Regional and municipal surtax: `PeriodFacts.regione` and `comune_belfiore`
  (omitted, the surtax is skipped; a code without a table makes the result
  `incomplete`)
- Prior-year income and written waivers for the substitute-tax regimes:
  `PriorYearTaxFacts`

---

## Disclaimer

Not legal or tax advice. Always verify results against official sources or a
qualified payroll professional.
