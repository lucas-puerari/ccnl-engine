# Work rules (L3)

Variable work data for a payroll run (overtime, absences, sick leave,
supplements, benefits, bonuses) is passed as work events in
`PeriodFacts.events`: on `PeriodInput.facts` for one run, or in
`YearInput.periods` keyed by month or by run id for a year. Events are part
of the run and change the
result according to the treatment in the table below. For example, overtime
raises `period_gross`; an unpaid absence is reported in
`unpaid_absence_deduction`; a bilateral fund contribution changes only
`period_net` and `period_employer_cost`. Each event appears as pay items in
`result.pay_items`.

Import event types from the `ccnl_engine` package, like every other public name.

```python
--8<-- "docs/examples/12_work_rules.py"
```

---

## Event types

All events are frozen dataclasses. Every event carries an `event_date`;
amounts are `Decimal` values in EUR, validated on construction.

| Event | Fields | Treatment |
|---|---|---|
| `OvertimeEvent` | `hours`, `hourly_rate`, `multiplier` (default `1.25`) | Pay `hours × hourly_rate × multiplier`; subject to INPS, IRPEF and TFR |
| `NightShiftEvent` | `supplement_amount` | Night-work supplement; INPS and IRPEF |
| `HolidayWorkEvent` | `supplement_amount` | Public holiday or weekly rest-day supplement; INPS and IRPEF, no TFR |
| `ShiftWorkEvent` | `supplement_amount` | Shift allowance; INPS and IRPEF, no TFR |
| `AbsenceEvent` | `hours`, `hourly_rate`, `end_date`, `suspends_accrual` | Unpaid absence deducted from pay; reduces the INPS and TFR base |
| `SickLeaveEvent` | `amount`, `sick_days`, `waiting_period_days` | Employer-paid sick leave, net of the carenza days; INPS and IRPEF, no TFR |
| `SicknessCaseEvent` | `case` (a `SicknessCase`) | Sickness episode from which the engine derives the absence deduction, INPS indemnity and employer integration |
| `FringeEvent` | `amount` | Fringe benefit (art. 51 c. 3 TUIR); exempt while the year total stays within the threshold, then the whole year total is taxable; see [Fringe benefits](#fringe-benefits) |
| `WelfareEvent` | `amount` | Welfare benefit; exempt from INPS and IRPEF, no TFR |
| `BonusEvent` | `amount`, `kind`, `agreement_signed_on` | One-off bonus; `kind` selects ordinary IRPEF, the PdR regime or the renewal regime |
| `BilateralFundEvent` | `employee_amount`, `employer_amount` | Bilateral or health fund contribution; see [Pay components](pay-components.md#bilateral-funds-fondi-bilaterali) |
| `ArrearsEvent` | `amount`, `separate_tax_rate`, `reference_period` | Renewal arrears under tassazione separata (art. 17 TUIR) |
| `TerminationTFREvent` | `amount`, `separate_tax_rate` | TFR settlement at cessazione (art. 19 TUIR) |

### Rates and amounts are caller inputs

The engine does not look up the overtime band or the supplement amount for
the CCNL: `OvertimeEvent.hourly_rate` and `multiplier`, and the
`supplement_amount` of night, holiday and shift events, come from the caller.
The same holds for the `separate_tax_rate` of arrears and TFR settlements.

### Absences are bounded by the pay of the run

Unpaid absences (`AbsenceEvent`, and the absence part of a
`SicknessCaseEvent`) that deduct more than the monthly pay of the run raise
`InvalidInputError` before any amount is computed: check the hours and the
hourly rate. Absences below the pay can still leave less than the IRPEF and
surtax due on the run (the withholding follows the projected annual income).
The taxes are then withheld up to the pay left and the rest is carried to
the next runs of the tax year
([Fiscal](fiscal.md#pay-that-does-not-cover-the-tax)). A run whose other
deductions (INPS, substitute tax, recovery installments) exceed the pay
left still raises `OutOfScopeError` with reason `withholding_shortfall`.

### Fringe benefits

For tax years 2025 to 2027 goods and services granted to the worker are
exempt from IRPEF and INPS up to 1,000 EUR in the year, or 2,000 EUR when the
worker has a fiscally dependent child (art. 12 c. 2 TUIR) and declares it to
the employer with the child's tax code (L. 207/2024 art. 1 cc. 390-391,
derogating TUIR art. 51 c. 3). Set `PeriodFacts.has_dependent_children` on
every run of the year once the declaration is made; the engine does not
derive it from `family_composition`.

The threshold is all or nothing (AdE circ. 4/E of 16 May 2025, par. 2.7): an
amount equal to the threshold is still exempt, but once the year total
exceeds it the whole amount of the year is taxable, not only the excess. The
year total comes from `opening_state.ytd.fringe`, so chain the closing state
of each run into the next. The benefit that crosses the threshold makes the
earlier exempt amounts of the year taxable in its run. For example, 600 EUR
in February is exempt; another 600 EUR in March brings the year to 1,200 EUR
and makes 1,200 EUR taxable in March; a further 300 EUR in April is taxable
on its own.

Each `FringeEvent` reports:

- on its `FringeBenefitItem`: `threshold_annual`, `ytd_total` (year total
  including the benefit) and `taxable_amount` (which can exceed `amount` on
  the crossing benefit);
- a `fringe_benefit` decision in `result.decisions`, with reason
  `within_threshold`, `above_threshold` or `above_threshold_retroactive`,
  the threshold and the children condition, the year totals, the
  `retroactive_amount` and the taxable amount as `amount`.

### Substitute-tax regimes

The prior-year employment income and the written waivers that decide
eligibility for the substitute-tax regimes are declared once, in
`PriorYearTaxFacts` on the input, not on each event. The sector is declared on
`Employment` and the employer activity on `EmployerProfile`. An unknown fact
means ordinary taxation; for night, holiday and shift supplements and for
renewal increments the result is then provisional. A renewal increment
(`BonusEvent` with `kind="contract_renewal"`) carries the signing date of its
renewal in `agreement_signed_on`. See
[Substitute tax regimes](substitute-tax-regimes.md).

---

## Reading the result

Each event produces pay items and ledger entries on the period result. A
condition that lowers the reliability of the result (for example an unknown
prior-year income) is reported in `result.issues` and reflected in
`result.status`. See [Results and calculation status](../api/engine.md#results-and-calculation-status).
