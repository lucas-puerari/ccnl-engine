# Decisions

`result.decisions` explains a payslip line by line. Every amount the run
posts to the ledger rests on at least one `CalculationDecision`: the
capability that decided, the rule and rule version applied, its source, the
normalized inputs and the amount. The reconciliation invariant
`amount_has_decision` fails the run when a posted amount has none.

| Field | Content |
|---|---|
| `capability` | Catalog feature, e.g. `base_salary`, `irpef`, `overtime` |
| `status` | `final`, `provisional`, `incomplete` or `rejected` |
| `reason_code` | Why the capability decided as it did, e.g. `withheld` |
| `rule`, `rule_version` | Payable rule applied and its ruleset version |
| `source` | Normative source of the rule, when the bundle records one |
| `inputs` | Normalized inputs, decimals and strings |
| `amount` | Amount the decision produced, `None` when it yields none |
| `origin` | `engine` (a bundled or statutory rule) or `caller_supplied` |

## Base stages

Every run records one decision per base stage. The rule is the payable rule
of the stage as the capability report lists it, and the source is its
provenance location; decisions other capabilities take on the same amounts
are referenced, not repeated.

| Capability | Reason codes | Rule | Main inputs | Amount |
|---|---|---|---|---|
| `base_salary` | `pay_chain_applied` | `<ccnl>:levels[<code>].base_salary[<tranche>]` | `minimum`, `seniority`, `allowances`, `allowance_codes`, `apprenticeship` | Gross of the pay chain |
| `inps_employee` | `rates_applied`, `domestic_hourly_rates` | `<inps>:inps`, `<inps>:apprentice` or `<inps>:domestic_contributions` | `base`, `ytd_base`, `ivs_ceiling` (`applied`, `not_applied`, `undetermined`), `rate` | Worker contributions; `None` and `incomplete` when `ivs_ceiling` is `undetermined` |
| `inps_employer` | as above | as above | as above, with the employer `rate` | Employer contributions, as above |
| `ivs_ceiling_eligibility` | `first_enrolment_after_1995`, `contributory_option`, `enrolled_before_1996`, `ceiling_not_reached`, `required_fact_missing` | `<inps>:inps.ceiling` | `first_enrolled_on`, `contributory_option`, `cohort_start`, `legal_basis`, `ceiling`, `ytd_base`, `period_base`, `ceiling_applies`; with `required_fact_missing` also `employee_capped`, `employee_uncapped`, `employer_capped`, `employer_uncapped` | `None` |
| `tfr` | `accrued` | `<tax>:tfr` | `base`, `accrual_divisor`, `account` | TFR accrued, in the company or in the pension fund |
| `irpef` | `withheld`, `refunded`, `nothing_due` | `<tax>:irpef_brackets` | `projected_taxable`, the annual components, `withholding_due`, `withholding_slots`, `decisions` | IRPEF of the run before the pay cap |

The `ivs_ceiling_eligibility` decision is recorded on every run whose INPS
rules carry a massimale, not on domestic CCNLs: it says why the massimale
applies or not (L. 335/1995 art. 2 c. 18), with the massimale and its INPS
source from the bundle. Without a contribution history it is
`ceiling_not_reached` while both branches coincide, and `required_fact_missing`
(`incomplete`) once the run crosses the massimale.

The `apprenticeship` input of `base_salary` names the
`apprenticeship_scaling` decision when a percentage apprenticeship scaled
the chain; `seniority` has its own decision when the months of service are
given. The IRPEF amount is the conguaglio YTD share of the run before the
pay cap: when the pay does not cover it, a `withholding_shortfall` decision
records what was carried to the next runs. Its `decisions` input names the
credit decisions the annual tax was netted with (family deductions,
ulteriore detrazione, trattamento integrativo, foreign tax credit). An
employer that is not a withholding agent keeps its `not_withholding_agent`
decision for `irpef` and records no other.

## Caller-supplied values

Some events carry a rate or an amount the engine applies as given, where
the bundle could hold a rule. Each such event records one decision with
`origin` `caller_supplied`, no `source`, the rule
`request:events[<index>].<Event>` at version `request`, and in its inputs
the `fields` taken from the caller, their values and, when the bundle has
one, the comparable bundled value.

| Event | Capability | Reason | Caller fields | Bundle value for comparison |
|---|---|---|---|---|
| `OvertimeEvent` | `overtime` | `caller_supplied_rate` | `hourly_rate`, and `multiplier` when given | Bands of the event's `kind` `bundle_band[<code>]`, `caller_supplement` (multiplier minus 1, when given), `bundle_hourly_divisor` |
| `NightShiftEvent` | `night_work` | `caller_supplied_amount` | `supplement_amount` | Night bands |
| `HolidayWorkEvent` | `holiday_work` | `caller_supplied_amount` | `supplement_amount` | Holiday bands |
| `ShiftWorkEvent` | `shift_work` | `caller_supplied_amount` | `supplement_amount` | Per-shift allowances |
| `AbsenceEvent` | `absence` | `caller_supplied_rate` | `hourly_rate` | `bundle_hourly_divisor` |
| `SickLeaveEvent` | `leave` | `caller_supplied_amount` | `amount` | None |
| `SicknessCaseEvent` | `sickness` | `caller_supplied_rate` | `gross_daily`, `inps_daily_rate`, `integration_rate`, `carenza_integration_rate` | `bundle_integration_rate`, `bundle_carenza_integration_rate` |
| `ArrearsEvent` | `contract_renewal_arrears` | `caller_supplied_rate` | `separate_tax_rate` | None |
| `TerminationTFREvent` | `termination_tfr` | `caller_supplied_rate` | `separate_tax_rate` | None |
| `BilateralFundEvent` | `bilateral_funds` | `caller_supplied_amount` | `employee_amount`, `employer_amount` | None |
| `BonusEvent` | `bonus` | `caller_declared_amount` | `amount` | None |
| `WelfareEvent` | `welfare` | `caller_declared_amount` | `amount` | None |

A band of kind `percentage` holds the supplement (`0.15` for 15%), not the
multiplier, so an overtime decision also records `caller_supplement`. A
comparable value missing from the bundle reads `not_in_bundle`. A bonus or
welfare amount is a declared fact, not a rule: its decision attributes the
amount and is not reported as caller-supplied. A fringe benefit keeps its
own `fringe_benefit` decision.

The amounts always follow the caller's values; the bundled value is shown
for comparison only. For overtime the caller's multiplier prevails over the
CCNL band; when it matches no band of the event's kind the run is
`provisional` with issue `caller_multiplier_differs_from_ccnl`. An overtime
event without a multiplier is paid with the CCNL band: the handler records
an engine decision `ccnl_overtime_band_applied` citing the band, and the
caller-supplied decision lists `hourly_rate` only. See
[Work rules](../engine/work-rules.md#overtime-multiplier).

A caller-supplied decision does not trace its capability: the event traces
it as before, computed when it had an effect. The capability report lists
the fields in `caller_supplied`, apart from `rule_sources`, and never
reports such a capability as `verified` or `derived`. Each capability in
`caller_supplied` is a `caller_supplied_rule` blocker: the result is not
payable until the values are validated outside the engine (see
[Assurance](confidence.md#payability-rules)). In the
[capability matrix](../contracts/capability-matrix.md) these capabilities
are labelled `caller-supplied`.

```python
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    OvertimeEvent,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)

engine = PayrollEngine.bundled()
result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=PeriodFacts(
            events=(
                OvertimeEvent(
                    date(2026, 3, 10), Decimal(10), Decimal("15.00"), Decimal("1.25")
                ),
            )
        ),
    )
)
for decision in result.decisions:
    print(decision.capability, decision.origin.value, decision.reason_code)
print(result.capability_report.caller_supplied)
# {'overtime': ('hourly_rate', 'multiplier')}
print([(b.code.value, b.feature) for b in result.blockers if b.feature == "overtime"])
# [('caller_supplied_rule', 'overtime')]
```

The overtime decision of this run records the caller's multiplier `1.25`
(`caller_supplement` `0.25`) next to the metalmeccanico weekday bands
`OT_DIURNO` `0.25` and `OT_DIURNO_EXTRA` `0.30`; the overtime paid is
10 * 15.00 * 1.25 = 187.50. The multiplier matches a band, so no
`caller_multiplier_differs_from_ccnl` issue is raised; a multiplier of
`1.40` would raise it.

## Attribution invariant

`amount_has_decision` maps each non-zero ledger entry to the capabilities
that can post it and requires a decision of at least one of them in the
run.

- An entry on `CASH_EARNINGS`, `NON_CASH_BENEFITS` or
  `EMPLOYEE_DEDUCTIONS` maps by its pay-item kind: the base salary,
  allowances and extra-month ratei to `base_salary`, an overtime earning to
  `overtime`, an absence deduction to `absence` or `sickness`.
- Any other entry maps by its account: `EMPLOYEE_CONTRIBUTIONS` to
  `inps_employee`, `ORDINARY_TAX` to `irpef`, `withholding_shortfall` or
  `shortfall_deferral`, `SURTAX` to the regional and municipal surtax or
  to `withholding_shortfall` for surtax carried from an earlier run,
  `TFR_ACCRUAL` to `tfr`.

An entry whose kind or account maps to no capability is a violation too, so
a new posting has to name the capability that decides it. The mapping is in
`ccnl_engine.payroll.application.invariants.attribution`.
