# Confidence

A payroll result carries two independent reliability signals. Neither is set
by the caller.

| Signal | Answers |
|---|---|
| `result.status` | Can this payslip be paid as computed? |
| `result.capability_report` | Did every capability the fiscal-year catalog declares actually run? |

Neither signal reads the `verification_status` of the underlying sources:
an unverified salary table does not lower either one. Source verification is
described in [Provenance](provenance.md).

## Calculation status

`result.status` is a `CalculationStatus`, derived from `result.issues`: the
worst status among the issues, or `final` when there are none.

| Status | Meaning |
|---|---|
| `final` | Every capability decided from known rules and facts. |
| `provisional` | Computed, but a decision rests on an assumption that may change the amounts. |
| `incomplete` | At least one amount could not be determined; do not pay as is. |
| `rejected` | The inputs cannot produce a meaningful result. |

`result.decisions` records what each capability decided and on which rule, so
a `final` result can still be explained line by line.

## Capability report

`result.capability_report` compares the capabilities the fiscal-year catalog
declares as computed or partially computed with what the calculation
observed. Each mismatch is a `CapabilityGap`.

| `status` | `confidence` | When |
|---|---|---|
| `"complete"` | `"high"` | No gaps |
| `"partial"` | `"medium"` | Only gaps where a capability declared computed ran partially |
| `"incomplete"` | `"low"` | Any other gap, such as a declared capability that did not run |

The report describes engine coverage for the year, not the specific payslip:
a result can be `final` while its capability report is `"low"`, because a
declared capability (for example INAIL) is not wired into the period run.

## Using both signals

```python
from datetime import date

from ccnl_engine import (
    CalculationStatus,
    EmploymentFacts,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
)

engine = PayrollEngine.bundled()
result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(),
    )
)

if result.status is not CalculationStatus.FINAL:
    for issue in result.issues:
        print(issue.code, issue.status, issue.message)

report = result.capability_report
print(report.status, report.confidence)
for gap in report.gaps:
    print(gap.feature, gap.kind.value)
```
