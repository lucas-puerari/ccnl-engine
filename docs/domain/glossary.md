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
Projected annually as: YTD taxable, plus the current run, plus the recurring
gross of the withholding slots still to come, minus the employee INPS on
them.  On the last slot the projection is the final taxable income.
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

### extra-month entitlement (mensilità equivalenti)

Equivalent months of pay granted per year: 12 regular months plus the
extra months, possibly fractional (13.5 means a full tredicesima and half a
quattordicesima).  It says how much is paid, never how many payslips are
issued.  Read from the CCNL `parameters.additional_months`.

`ExtraMonthEntitlement`, `WorkCalendar.entitlement`

### payroll run count (numero di cedolini)

Number of payslips issued in the year: 12 regular runs plus one run per
extra month, whatever its fraction.  With 13.5 equivalent months the year
has 14 runs.

`PayrollRunCount`, `PayrollSchedule.run_count`

### withholding schedule (piano delle ritenute)

The ordered IRPEF withholding slots of the year, one per payslip.  The
annual projection spreads the tax still due over the slots not yet closed,
and the last slot performs the conguaglio on the final taxable income
(art. 23 c. 3 DPR 600/1973).  Surtax and somma esente are split per slot.
Never derived from the entitlement.

`WithholdingSchedule`, `WithholdingSlot`, `PeriodCalculationRequest.withholding_schedule`

### calendar override (deroga al calendario)

A calendar that replaces the one derived from the CCNL, with a domain
reason and a note.  `PAYMENT_MONTH` moves when an extra month is paid, its
12-month accrual window ending in the payment month, and keeps the
entitlement unchanged; `MORE_FAVOURABLE_TREATMENT`
records an agreement granting more than the CCNL (art. 2077 c.c.).  No
reason allows dropping or lowering an extra month the CCNL grants.

`CalendarOverride`, `CalendarOverrideReason`, `YearCalculationResult.calendar`

### calculation status (stato del calcolo)

How far a result can be relied upon, from least to most severe:
`final`, `provisional`, `incomplete`, `rejected`.  A period status is the
worst status among its issues (`final` when there are none); a year status is
the worst status among its periods.  An unknown normative input must never
yield a `final` result.

`CalculationStatus`, `PeriodCalculationResult.status`

### calculation issue (anomalia di calcolo)

A condition that lowers the status of a result, identified by a stable
lower snake case `code` (for example `regional_surtax_unknown`), with a message,
the status it implies and, when one applies, its normative source.

`CalculationIssue`, `PeriodCalculationResult.issues`

### calculation decision (decisione di calcolo)

What one capability actually decided in a run: its status, a stable
`reason_code`, the normalized inputs it used, the rule and rule version
applied, the normative source and the resulting amount (`None` when unknown).
A capability that ran and found nothing due still decides: amount 0 and a
reason such as `income_above_upper_threshold`.  The capability trace is
built from the decisions.

`CalculationDecision`, `PeriodCalculationResult.decisions`,
`YearCalculationResult.decisions`

### capability trace (traccia di esecuzione)

The state of each catalog feature in one run, derived from what executed and
never from the request: computed, partial, unresolved, skipped or not
applicable.  A feature decided by a `final` decision is computed, by a
`provisional` one partial, by an `incomplete` or `rejected` one unresolved;
an event feature is computed only when an event handler posted a non-zero
amount or took a decision.  The capability report lists the features the
catalog promises whose trace falls short, an unresolved one included.

`DecisionTrace`, `TraceState`, `CapabilityReport`, `CapabilityGapKind`

### worker category decision (decisione sulla categoria)

The calculation decision recording the worker category used for pay and
contributions and its origin: `declared` on the employment, or
`fixed_by_level` when the level admits a single category.  No decision is
taken when no category applies.

`CalculationDecision`, `WorkerCategory`

### tax credit decision (decisione sulle detrazioni)

The calculation decision of the ulteriore detrazione
(`ulteriore_detrazione_lavoro`) or of the trattamento integrativo
(`trattamento_integrativo`): the annual entitlement and the reason code of
the rule branch that produced it, e.g. `full_amount`, `tapered_amount`,
`deductions_not_above_irpef`.  Taken on every run whose tax year rules put
the credit in force.

`CalculationDecision`, `CreditOutcome`

### surtax decision (decisione sulle addizionali)

The `CalculationDecision` of the regional or municipal surtax
(`addizionale_regionale`, `addizionale_comunale`) for a jurisdiction named in
the request.  It separates a surtax not due by rule (`no_irpef_due`,
`below_exemption_threshold`: final, amount 0), a table applied
(`table_applied`, `advance_applied`: final) and a well-formed code without a
table row (`table_unknown`: incomplete, amount `None`, issue
`regional_surtax_unknown` or `municipal_surtax_unknown`).  The region is the
ISO 3166-2:IT code (`IT-45`), with `IT-BZ` / `IT-TN` for the autonomous
provinces.  A malformed code is invalid input, not an unknown table.

`CalculationDecision`, `REGION_CODES`, `PeriodCalculationRequest.regione`,
`PeriodCalculationRequest.comune_belfiore`

### preferential tax regime (regime di imposta sostitutiva)

A statutory flat tax that replaces IRPEF and its surtaxes on the pay items it
covers, for the tax years it is in force, within an optional annual cap, and
only for workers meeting its requirements: prior-year employment income not
above a ceiling, employment sector, no written renunciation.  Parameters and
normative source are data in the tax bundle.

`PreferentialTaxRegime`, `RinnovoRules`

### regime cap account (plafond annuo del regime agevolato)

The year-to-date part of a regime's annual cap already taxed at the
substitute rate.  For the night, holiday and shift supplement regime
(L. 199/2025 art. 1 cc. 10-11, cap 1,500 EUR) it lives in the tax year state
and carries over between runs of the tax year; each supplement only gets the
substitute rate on what is left, the excess is ordinary income.  It restarts
with the next tax year.

`RegimeCapAccount`, `PayrollState.ytd.work_time_regime`

### tax year state (progressivi dell'anno fiscale)

Run counters, withholding slots and year-to-date accounts of one tax year:
earnings, fringe, tax withheld, trattamento integrativo, somma esente and the
regime cap account.  It restarts at zero when the next tax year opens.

`TaxYearState`, `PayrollState.ytd`

### employment obligations (obbligazioni del rapporto)

What a run owes or is owed beyond the tax year that created it, carried from
run to run until settled.  Today: installment recoveries of trattamento
integrativo (D.L. 3/2020 art. 1 c. 3), each bound to the tax year whose
conguaglio opened it.  Installments posted in a later year do not enter the
credit account of that year.

`EmploymentObligations`, `RecoveryObligation`, `PayrollState.obligations`

### year close (chiusura dell'anno fiscale)

The transition from the state after the last run of year N to the opening
state of N+1: fresh tax year state, obligations carried.  Rejected when a
withholding slot of N is still open.

`close_tax_year`, `PayrollEngine.close_tax_year`

### opening balances (progressivi di subentro)

Year-to-date totals and running recoveries computed by a previous payroll
provider, validated and turned into the state of the first run the engine
computes.

`OpeningBalances`

### regime eligibility (spettanza del regime agevolato)

The outcome of checking a pay item against a preferential regime:
`eligible` (substitute rate on the eligible amount, ordinary on any excess
over the cap), `ineligible` (ordinary) or `unknown` when a required fact is
missing (ordinary, and a provisional issue).  A definite ineligibility wins
over a missing fact.  Recorded as a calculation decision with a stable
`reason_code`, e.g. `prior_income_above_ceiling`.

`RegimeEligibility`, `assess_regime`

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
