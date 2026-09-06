# Engine

Core computation functions and types.

See [Guide: Employment types](../guide/employment-types.md) and
[Guide: Pay components](../guide/pay-components.md) for worked examples.

## compute

::: ccnl_engine.payroll.service.orchestrator
    options:
      members:
        - compute

## Input models

::: ccnl_engine.payroll.domain.employee
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

::: ccnl_engine.payroll.domain.employer
    options:
      members:
        - Employer

## Payslip

::: ccnl_engine.payroll.domain.payslip
    options:
      members:
        - Payslip
