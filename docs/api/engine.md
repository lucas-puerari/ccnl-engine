# Engine

Core computation functions and types.

See [Guide: Employment types](../domain/employment-types.md) and
[Guide: Pay components](../engine/pay-components.md) for worked examples.

## Entry points

::: ccnl_engine.engine.payroll.service.orchestrator
    options:
      members:
        - estimate_annual
        - compute_month
        - compute

## Calculation

Both `estimate_annual()` and `compute_month()` return a `Calculation` that
bundles the engine version, the ruleset revisions used, a snapshot of the
inputs, and the resulting `PayrollResult` (`.result`).

::: ccnl_engine.engine.payroll.domain.calculation
    options:
      members:
        - Calculation
        - InputSnapshot

## Input models

::: ccnl_engine.engine.payroll.domain.scenario
    options:
      members:
        - AnnualPayrollScenario
        - PayPeriod
        - PayrollScenario
        - Employee
        - Employment
        - Employer
        - Jurisdiction
        - Agreement

::: ccnl_engine.engine.payroll.domain.employee
    options:
      members:
        - SeniorityByCount
        - SeniorityByDate
        - SeniorityByMonths
        - RalOverride
        - DestinationRalOverride

## PayrollResult

::: ccnl_engine.engine.payroll.domain.payroll_result
    options:
      members:
        - PayrollResult
