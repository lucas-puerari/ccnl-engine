# Engine

Core computation functions and types.

See [Guide: Employment types](../domain/employment-types.md) and
[Guide: Pay components](../engine/pay-components.md) for worked examples.

## Entry point

::: ccnl_engine.api.facade
    options:
      members:
        - PayrollEngine

## Request and run

::: ccnl_engine.api.requests
    options:
      members:
        - PayrollRequest
        - PayrollRun
        - EmploymentFacts

::: ccnl_engine.payroll.domain.employer
    options:
      members:
        - Employer
        - Headcount

::: ccnl_engine.engine.contract.domain.category
    options:
      members:
        - WorkerCategory

## Results and calculation status

Every period result carries `issues` and a derived `status`; the year result
exposes the worst status of its periods and their issues in payment order.
A result is `final` only when no capability raised an issue.

| Status | Meaning |
|---|---|
| `final` | Every capability decided from known rules and facts. |
| `provisional` | Computed, but a decision rests on an assumption that may change the amounts. |
| `incomplete` | At least one amount could not be determined; do not pay as is. |
| `rejected` | The inputs cannot produce a meaningful result. |

```python
from ccnl_engine import CalculationStatus

result = engine.calculate(request)
if result.status is not CalculationStatus.FINAL:
    for issue in result.issues:
        print(issue.code, issue.status, issue.message)
```

Compare statuses with `severity` or `CalculationStatus.worst()`: the string
values do not sort in severity order.

::: ccnl_engine.payroll.domain.decisions
    options:
      members:
        - CalculationStatus
        - CalculationIssue
        - CalculationDecision
