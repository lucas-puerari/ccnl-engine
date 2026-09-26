# Work rules (L3)

Variable work data for a payroll run (overtime, absences, sick leave,
supplements, benefits, bonuses) is passed as work events on
`PayrollRequest.events`, or per month and per run on `PayrollYearRequest`
(`period_events`, `per_run_events`). Events are part of the run and change the
result according to the treatment in the table below. For example, overtime
raises `period_gross`; an unpaid absence is reported in
`unpaid_absence_deduction`; a bilateral fund contribution changes only
`period_net` and `period_employer_cost`. Each event appears as pay items in
`result.pay_items`.

Import event types from `ccnl_engine.events`, the stable public path.

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
| `NightShiftEvent` | `supplement_amount`, `prior_income`, `substitute_tax_waived` | Night-work supplement; INPS and IRPEF |
| `HolidayWorkEvent` | `supplement_amount`, `prior_income`, `substitute_tax_waived` | Public holiday or weekly rest-day supplement; INPS and IRPEF, no TFR |
| `ShiftWorkEvent` | `supplement_amount`, `prior_income`, `substitute_tax_waived` | Shift allowance; INPS and IRPEF, no TFR |
| `AbsenceEvent` | `hours`, `hourly_rate`, `end_date`, `suspends_accrual` | Unpaid absence deducted from pay; reduces the INPS and TFR base |
| `SickLeaveEvent` | `amount`, `sick_days`, `waiting_period_days` | Employer-paid sick leave, net of the carenza days; INPS and IRPEF, no TFR |
| `SicknessCaseEvent` | `case` (a `SicknessCase`) | Sickness episode from which the engine derives the absence deduction, INPS indemnity and employer integration |
| `FringeEvent` | `amount` | Fringe benefit (art. 51 c. 3 TUIR); the exemption threshold is applied cumulatively over the year |
| `WelfareEvent` | `amount` | Welfare benefit; exempt from INPS and IRPEF, no TFR |
| `BonusEvent` | `amount`, `kind`, `prior_income`, `substitute_tax_waived` | One-off bonus; `kind` selects ordinary IRPEF, the PdR regime or the renewal regime |
| `BilateralFundEvent` | `employee_amount`, `employer_amount` | Bilateral or health fund contribution; see [Pay components](pay-components.md#bilateral-funds-fondi-bilaterali) |
| `ArrearsEvent` | `amount`, `separate_tax_rate`, `reference_period` | Renewal arrears under tassazione separata (art. 17 TUIR) |
| `TerminationTFREvent` | `amount`, `separate_tax_rate` | TFR settlement at cessazione (art. 19 TUIR) |

### Rates and amounts are caller inputs

The engine does not look up the overtime band or the supplement amount for
the CCNL: `OvertimeEvent.hourly_rate` and `multiplier`, and the
`supplement_amount` of night, holiday and shift events, come from the caller.
The same holds for the `separate_tax_rate` of arrears and TFR settlements.

### Substitute-tax regimes

`prior_income` on `BonusEvent`, `NightShiftEvent`, `HolidayWorkEvent` and
`ShiftWorkEvent` is the employment income that decides eligibility for the
relevant substitute-tax regime. `None` means unknown: the amount is taxed as
ordinary income. For night, holiday and shift supplements and for renewal
increments the result is then provisional. See
[Substitute tax regimes](substitute-tax-regimes.md).

---

## Reading the result

Each event produces pay items and ledger entries on the period result. A
condition that lowers the reliability of the result (for example an unknown
`prior_income`) is reported in `result.issues` and reflected in
`result.status`. See [Results and calculation status](../api/engine.md#results-and-calculation-status).
