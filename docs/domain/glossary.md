# Payroll glossary — decision record

**Status:** adopted  
**Date:** 2026-09-22  
**Context:** REVIEW.md §2.2, §7 Fase 0 — unambiguous terminology required
before the refactoring sequence (PR-02 through PR-13) to prevent divergence
between JSON, code, and documentation.

---

## Terms

### gross (lordo)

The sum of all monetary pay items for a period before any deduction.
Includes base salary, seniority increments, allowances, overtime,
night/holiday supplements, bonuses, and contractual renewal arrears.
Does NOT include non-cash benefits (fringe, welfare) or employer-only costs.

`period_gross = CASH_EARNINGS ledger total`

### cash (netto monetario in entrata)

Synonym for gross in the context of pay items that represent actual monetary
outflows from the employer to the worker.  Non-cash benefits (fringe,
welfare) must never contribute to cash earnings even when they have a taxable
component.

### taxable (imponibile fiscale)

The base on which IRPEF and its surcharges (addizionali) are computed.
Derived annually as: `recurring_gross × N_months − employee_INPS_annual`.
One-off events (overtime, bonuses) are added on their own taxable amount
after deducting the INPS due on them.  Non-cash benefits may contribute to
the taxable base when the exempt threshold is exceeded (see `fringe` below).

### withheld (ritenuta)

The IRPEF amount actually deducted from the worker's net pay in a given
period.  Distinct from `liability`: withheld is the cash collected by the
employer; liability is what is legally owed for the year.

`withheld = ORDINARY_TAX ledger total for the period`

### liability (debito fiscale annuo stimato)

The estimated annual IRPEF owed, computed as:
`irpef_gross_annual − work_income_deduction − family_deductions − credits`.
This is an estimate: it may differ from the final tax settled at year-end
or at termination.

### accrual (maturazione / competenza)

Recognition of a right or obligation in the period it is earned or incurred,
regardless of when the cash is paid.  TFR, extra months (tredicesima,
quattordicesima), and leave accrue in each payroll period.

`TFR_ACCRUAL ledger account`  
`ExtraMonthAccrual` pay item (to be introduced in PR-11)

### settlement (liquidazione / pagamento / conguaglio)

The cash event that discharges an accrued obligation.  TFR settlement occurs
at termination; extra-month settlement occurs when the contract schedules
payment (typically November/December for tredicesima).  IRPEF conguaglio is
the year-end or termination settlement of the difference between liability
and withheld YTD.

`TFR_SETTLEMENT ledger account`

---

## Derived identities (invariants)

These equalities must hold after every period calculation and are enforced by
`reconcile()`:

| Label | Equation |
|---|---|
| I9 — net | `CASH_EARNINGS + CREDITS + TFR_SETTLEMENT − EMPLOYEE_CONTRIBUTIONS − ORDINARY_TAX − SURTAX − SEPARATE_TAX = period_net` |
| I12 — employer cost | `CASH_EARNINGS + EMPLOYER_CONTRIBUTIONS + TFR_ACCRUAL = period_employer_cost` |
| I13 — gross | `CASH_EARNINGS = period_gross` |
| L3, L4 (contributions) | every `EMPLOYEE_CONTRIBUTIONS` and `EMPLOYER_CONTRIBUTIONS` entry `>= 0`; corrections are a distinct movement, not a negative ordinary contribution |

---

## Anti-patterns

- **gross includes fringe/welfare**: fringe benefits and welfare are classified
  as `NON_CASH` or `EXEMPT`; they must not post to `CASH_EARNINGS`.
- **withheld == liability**: withholding is a period instalment; it diverges
  from annual liability whenever YTD state changes (conguaglio).
- **annual ÷ 12 = period**: period calculations must be autonomous, not
  divisions of an annual figure.
- **max(0, liability − withheld)**: the clamp prevents modelling refunds;
  conguaglio may be negative (a credit to the worker).
