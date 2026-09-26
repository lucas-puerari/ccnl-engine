# Confidence

A payroll result carries two independent reliability signals. Neither is set
by the caller.

| Signal | Answers |
|---|---|
| `result.status` | Can this payslip be paid as computed? |
| `result.capability_report` | Did every capability the fiscal-year catalog declares actually run, and how well are the rules it read backed by sources? |

Both read the provenance status of the payable rules a run executed (see
[Provenance](provenance.md)), each in its own way:

- a rule with status `missing` makes the result `incomplete` through a
  `rule_source_missing` issue that names the rule;
- the weakest status of each executed capability (`verified`, `derived`,
  `assumed` or `missing`) is in `result.capability_report.rule_sources`.

An `assumed` rule does not lower `result.status` or the report
`confidence`. Across the 1 126 bundled levels, run for March 2026 with 20
employees, every run reads at least one `assumed` rule (the somma esente cut
points are reconstructions, and 121 of 125 CCNLs cite no clause for their
number of monthly payments). Making `assumed` provisional, or lowering the
confidence for it, would mark every result the same way and tell the caller
nothing; the per-capability status tells which amounts rest on assumptions.
No bundled rule is `missing`, so no bundled result is incomplete for lack of
a source.

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

Issues that lower the status include:

| Code | Status | When |
|---|---|---|
| `rule_source_missing` | `incomplete` | An executed capability read a payable rule whose provenance status is `missing` |
| `employer_rate_category_assumed` | `provisional` | The sector sets INPS employer rates by worker category (artigianato: impiegati and quadri 24.71%), the level fixes no category and none was declared, so the general rate (26.93%, the operai rate) applied |

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

`rule_sources` maps each executed capability that reads bundled rules to the
weakest provenance status among them. Capabilities computed only from
caller-declared amounts do not appear.

## Using both signals

```python
from datetime import date

from ccnl_engine import (
    CalculationStatus,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)

engine = PayrollEngine.bundled()
result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )
)

if result.status is not CalculationStatus.FINAL:
    for issue in result.issues:
        print(issue.code, issue.status, issue.message)

report = result.capability_report
print(report.status, report.confidence)
for gap in report.gaps:
    print(gap.feature, gap.kind.value)
for capability, status in report.rule_sources.items():
    print(capability, status.value)
```
