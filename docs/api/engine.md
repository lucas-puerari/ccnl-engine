# Engine

Core computation functions and types.

See [Guide: Employment types](../guide/employment-types.md) and
[Guide: Pay components](../guide/pay-components.md) for worked examples.

## compute

::: ccnl_engine.engine.payroll.service.orchestrator
    options:
      members:
        - compute

## Calculation

`compute()` returns a `Calculation` that bundles the engine version, the
ruleset revisions used, a snapshot of the inputs, and the resulting `PayrollResult`
(`.result`). Attribute reads are forwarded onto the `PayrollResult`, so
`calculation.net_annual` works too.

::: ccnl_engine.engine.payroll.domain.calculation
    options:
      members:
        - Calculation
        - InputSnapshot

## Input models

::: ccnl_engine.engine.payroll.domain.employee
    options:
      members:
        - Employee
        - ContractPosition
        - WorkArrangement
        - TaxProfile
        - SalaryOverrides
        - SeniorityByCount
        - SeniorityByMonths
        - RalOverride
        - DestinationRalOverride

::: ccnl_engine.engine.payroll.domain.employer
    options:
      members:
        - Employer

## PayrollResult

::: ccnl_engine.engine.payroll.domain.payroll_result
    options:
      members:
        - PayrollResult