# Engine

Core computation functions and types.

See [Guide: Employment types](../domain/employment-types.md) and
[Guide: Pay components](../engine/pay-components.md) for worked examples.

## Entry point

::: ccnl_engine.api.facade
    options:
      members:
        - PayrollEngine

## Inputs

`calculate_period` takes a `PeriodInput`, `calculate_year` a `YearInput`.
Both group the facts by owner and are validated when built:

| Model | Holds |
|---|---|
| `Employment` | CCNL slug, level, contract type, category, `EmploymentPeriod`, weekly and full-time `WeeklyHours`, `SeniorityMonths`, roles, IVS ceiling status, sector (`None` means unknown) |
| `EmployerProfile` | `Headcount` (required, no size is assumed) and activity (`None` means unknown) |
| `PriorYearTaxFacts` | prior-year employment income and the regimes waived in writing, read by every substitute-tax regime and the PdR |
| `PeriodFacts` | events, contributable hours, region and Belfiore code, family composition, dependent children of one run |

::: ccnl_engine.payroll.domain.inputs
    options:
      members:
        - PeriodInput
        - PeriodFacts

::: ccnl_engine.payroll.domain.year_input
    options:
      members:
        - YearInput

::: ccnl_engine.payroll.domain.employment
    options:
      members:
        - Employment

::: ccnl_engine.payroll.domain.employment_facts
    options:
      members:
        - EmploymentPeriod
        - WeeklyHours
        - SeniorityMonths
        - ContributableHours

::: ccnl_engine.payroll.domain.employer
    options:
      members:
        - EmployerProfile
        - Headcount

::: ccnl_engine.payroll.domain.prior_year
    options:
      members:
        - PriorYearTaxFacts

::: ccnl_engine.tax.domain.preferential_regime
    options:
      members:
        - EmploymentSector
        - EmployerActivity
        - SubstituteTaxRegime

::: ccnl_engine.payroll.domain.run
    options:
      members:
        - PayrollRun
        - PayrollRunId

## Year calendar

`YearInput` derives the calendar from the CCNL when `calendar_override` is
omitted. A different calendar is accepted only as a validated
`CalendarOverride`.

::: ccnl_engine.payroll.domain.calendar_override
    options:
      members:
        - CalendarOverride
        - CalendarOverrideReason

::: ccnl_engine.contract.domain.category
    options:
      members:
        - WorkerCategory

## Results and calculation status

Every period result carries `issues` and a derived `status`; the year result
exposes the worst status of its periods and their issues in payment order,
each issue once: one repeated on every run (same `code` and `message`) is
listed at its first run.
A result is `final` only when no capability raised an issue.

| Status | Meaning |
|---|---|
| `final` | Every capability decided from known rules and facts. |
| `provisional` | Computed, but a decision rests on an assumption that may change the amounts. |
| `incomplete` | At least one amount could not be determined; do not pay as is. |
| `rejected` | The inputs cannot produce a meaningful result. |

```python
from ccnl_engine import CalculationStatus

result = engine.calculate_period(period_input)
if result.status is not CalculationStatus.FINAL:
    for issue in result.issues:
        print(issue.code, issue.status, issue.message)
```

Compare statuses with `severity` or `CalculationStatus.worst()`: the string
values do not sort in severity order.

An `incomplete` result still carries amounts, but at least one of them is
missing, not zero: for example a surtax whose table is unknown is withheld
as 0 and flagged by the issue `regional_surtax_unknown` or
`municipal_surtax_unknown`.  `result.decisions` records what each capability
decided, e.g. the surtax and tax credit decisions described in
[Fiscal computation](../engine/fiscal.md#surtax-decisions).  The year result
exposes the decisions of its periods in payment order.

### Capability report

`result.capability_report` compares what the run executed with the capability
catalog of the tax year.  Each feature is traced from what actually ran,
never from the presence of an input:

- the core stages (base salary, INPS, TFR, IRPEF) run on every period;
- an event feature (overtime, welfare, ...) is computed only when one of its
  events posted a non-zero amount or took a decision, otherwise skipped;
- every other feature follows its decisions: `final` is computed (a zero
  amount with its reason counts), `provisional` is partial, `incomplete` or
  `rejected` is unresolved, and no decision is not applicable.

A feature the catalog promises is a gap when it is absent
(`feature_absent`), not computed (`not_computed`), unresolved (`unresolved`,
e.g. a surtax without a table), or only partial where the catalog promises
it computed (`promised_computed_got_partial`).

::: ccnl_engine.payroll.domain.period
    options:
      members:
        - PeriodResult

::: ccnl_engine.payroll.application.calculate_year
    options:
      members:
        - YearResult

::: ccnl_engine.payroll.domain.decisions
    options:
      members:
        - CalculationStatus
        - CalculationIssue
        - CalculationDecision
