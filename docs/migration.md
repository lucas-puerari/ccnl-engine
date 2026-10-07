# Migration guide

Changes are listed newest first. Older changes are on
[Migration guide: earlier releases](migration-earlier.md) and
[Migration guide: inputs and legacy APIs](migration-legacy.md).

## A month of sickness deducts at most its pay

| Before | After |
|---|---|
| Each INPS band of a `SicknessEpisode` was rounded on its own: a whole month of sickness, or a month crossing the 180-day INPS cap, deducted one cent more than the pay and raised `InvalidInputError` | The pay of the sick days is rounded once on the days of the month counted so far; the sick days of a month never deduct more than its pay. The `absence_deduction` and the INPS share of an episode can move by one cent |
| Two episodes in the same month each counted up to a monthly pay: 1-15 and 16-31 July 2026 (27 working days by 26) raised `InvalidInputError` | The episodes of a run are taken by first day, whatever their order in the facts; the days past the pay left by the earlier ones are dropped, and the month deducts at most its pay |

## Payability is fail-closed on unknown residence and family

A capability the registry declares required (`applicability_facts`) must be
ruled out by a decision of the run or decided on the supplied facts; a
default no longer rules it out. Amounts are unchanged.

| Before | After |
|---|---|
| `PeriodFacts.regione` or `comune_belfiore` left `None` skipped the surtax as not applicable, without a blocker | A `requirement_unresolved` blocker on `addizionale_regionale` (`facts.regione`) or `addizionale_comunale` (`facts.comune_belfiore`) when the employer withholds; coverage `incomplete` |
| `PeriodFacts.family_composition` left `None` skipped the art. 12 TUIR deductions without a blocker | A `requirement_unresolved` blocker on `family_deductions` (`facts.family_composition`); pass `FamilyComposition()` for a worker with no dependant |
| `CapabilityReport` had gaps only | `CapabilityReport.unresolved`, a tuple of `UnresolvedRequirement` (exported by `ccnl_engine.results`) |
| `BlockerCode` without a requirement member | `BlockerCode.REQUIREMENT_UNRESOLVED` (`"requirement_unresolved"`) |

A household employer, not a withholding agent, decides that no surtax and no
deduction is due: its runs need neither fact.

## Surtax table entries and ulteriore settlement moved

Two internal modules were split. Names exported from `ccnl_engine` and its
namespaces are unchanged, and so are amounts.

| Before | After |
|---|---|
| `ccnl_engine.tax.domain.surtax_rules.RegionaleEntry`, `ComunaleEntry`, `RegionalDeduction`, `ComunaleDeduction`, `WholeIncomeRate`, `WithholdingCalendar`, `SurtaxBracket` | `ccnl_engine.tax.domain.surtax_tables` |
| `ccnl_engine.payroll.service.ulteriore_recovery.UlterioreSettlement`, `settle_ulteriore` | `ccnl_engine.payroll.service.ulteriore_settlement` |

`SurtaxRules`, `RegionaleRaw` and `ComunaleRaw` stay in `surtax_rules`.

## Public names grouped in four namespaces

The root `ccnl_engine` keeps the common path only; every other public name
moved to one namespace. There is no alias: an import from the old place
raises `ImportError`. Amounts are unchanged.

| Module | Names |
|---|---|
| `ccnl_engine` (unchanged) | `CcnlEngineError`, `CompetenceYearPlan`, `CompetenceYearResult`, `DataIntegrityError`, `EmployerProfile`, `Employment`, `Headcount`, `InvalidInputError`, `MissingRequiredFactError`, `MissingRuleError`, `OutOfScopeError`, `PayrollEngine`, `PayrollRun`, `PeriodFacts`, `PeriodInput`, `PeriodResult`, `TaxYearPlan`, `TaxYearResult`, `UnknownCcnlError`, `UnknownLevelError`, `UnsupportedTaxYearError`, `engine_version` |
| `ccnl_engine.inputs` | `Apprentice`, `CalendarOverride`, `CalendarOverrideReason`, `ContributableHours`, `ContributionHistory`, `CurrentYearTaxFacts`, `DeferredShortfall`, `Dependent`, `DependentRelationship`, `EmployerActivity`, `EmploymentPeriod`, `EmploymentSector`, `EngineMode`, `FamilyComposition`, `FixedTerm`, `ForeignTaxPaid`, `IncomeEstimateQuality`, `InpsBaseYtd`, `OpeningBalances`, `PaymentId`, `PayrollRunId`, `PensionFundEnrolment`, `PeriodState`, `Permanent`, `PriorYearTaxFacts`, `RecoveryObligation`, `RecoveryPlan`, `SeniorityFact`, `SenioritySource`, `ShortfallDeferralRequest`, `SubstituteTaxRegime`, `SurtaxComponent`, `SurtaxObligation`, `WeeklyHours`, `WorkCalendar`, `WorkerCategory` |
| `ccnl_engine.events` | `AbsenceEvent`, `ArrearsEvent`, `BilateralFundEvent`, `BonusEvent`, `FringeEvent`, `HolidayWorkEvent`, `NightShiftEvent`, `OvertimeEvent`, `OvertimeKind`, `ShiftWorkEvent`, `SickLeaveEvent`, `SicknessEpisode`, `TerminationTFREvent`, `WelfareEvent`, `WorkEvent`, plus `PeriodId` (new) |
| `ccnl_engine.results` | `BlockerCode`, `CalculationDecision`, `CalculationIssue`, `CalculationStatus`, `CapabilityGap`, `CapabilityScope`, `CoverageStatus`, `DecisionOrigin`, `EvidenceStatus`, `LimitationStatus`, `ModelLimitation`, `MonetaryImpact`, `Payability`, `RemittanceColumn`, `RemittanceLine`, `ResultAssurance`, `ResultBlocker`, plus `AccountKind` (new) |
| `ccnl_engine.catalog` | `CapabilityCatalog`, `CapabilityEntry`, `CapabilityImplementation`, `CcnlId`, `ContractSummary`, `RulesetAssurance`, `RulesetIdentity`, `RulesetKind`, `RulesetReadiness`, `VerificationStatus`, `get_ccnl`, `search_ccnls` |

| Before | After |
|---|---|
| `from ccnl_engine import Permanent, SeniorityFact, OvertimeEvent, ResultBlocker, get_ccnl` | `from ccnl_engine.inputs import Permanent, SeniorityFact`, `from ccnl_engine.events import OvertimeEvent`, `from ccnl_engine.results import ResultBlocker`, `from ccnl_engine.catalog import get_ccnl` |
| `ccnl_engine.events` removed in favour of the root (see "Legacy modules and aliases removed") | `ccnl_engine.events` is again the one public home of the work events |
| `ArrearsEvent.reference_period` built from `ccnl_engine.payroll.domain.period_payroll.PeriodId` | `from ccnl_engine.events import PeriodId` |
| `RemittanceLine.account` and `LedgerEntry.account` typed by an internal enum | `from ccnl_engine.results import AccountKind` to name or compare an account |
| `OpeningBalances(...).to_state()` | `PayrollEngine.import_opening_balances(OpeningBalances(...))`, which also checks the input; `to_state()` is removed |
| `ccnl_engine.payroll.application.mode_input` (internal) | `ccnl_engine.payroll.application.facade_input` |

To migrate, split each `from ccnl_engine import (...)` by the table above.
Modules below the five public ones are internal.

## Apprenticeship pay components

Apprentice pay now follows the CCNL on every component it touches.

| Before | After |
|---|---|
| A percentage track reduced the apprentice seniority amount by the percentage | The apprentice amount (`seniority_increments.apprentice_amount`) is paid in full: it is already the apprentice one. `apprenticeship_scaling` lists `seniority` under `unscaled` |
| A `midpoint_to_destination` period averaged the base salary only; the allowances stayed those of the pay level | The period pays the mean of the whole monthly pay of the two levels: base salary and every active fixed allowance (one level's allowance counts as zero on the other). Each allowance is rounded to the cent; the base takes the rest, so the total is the rounded mean of the totals |
| Engine limitations `apprenticeship_midpoint_allowances` and `apprentice_seniority_simplified` open, recorded on every affected run | Both `resolved`. A CCNL whose rule is unsourced carries its own open limitation, recorded on the same path: `<ccnl_id>/apprenticeship_midpoint_components` (Legno Federlegno) and `<ccnl_id>/apprentice_seniority` (CCNLs with level increments and no apprentice amount) |
| A percentage track reduced every allowance whose `apprenticeship_pct_relevant` flag the data leaves at its default, silently | Same amounts, plus the open engine limitation `apprenticeship_pct_undeclared_components` (`monetary_impact` `unknown`), so the run is not payable until the CCNL flag is sourced. `Allowance.apprenticeship_pct_declared` tells a declared flag from a default |

- Federterme L5 apprentices in the second half of the track now earn the
  Art. 13 lett. g midpoint of the whole pay (March 2026: 1,405.31 instead of
  1,404.10).
- Percentage apprentices of the five Confartigianato CCNLs with an apprentice
  seniority amount (acconciatura-estetica, comunicazione, legno-lapidei,
  panificazione, tessile-moda) receive the full amount once increments
  mature.

## Sickness episodes computed by the engine

Sickness is a native capability. The engine pays the sick days of an
episode from the CCNL sickness and absence rules and the INPS rules of the
bundle, over as many runs as the episode lasts.

| Before | After |
|---|---|
| `SicknessCaseEvent(event_date, case=SicknessCase(...))` with caller `gross_daily`, `working_days`, `waiting_period_days`, `inps_daily_rate`, `integration_rate` | `SicknessEpisode(episode_id, started_on, ended_on, relapse_of=None)`: the engine derives the days, carenza, INPS band and CCNL tier |
| `SicknessCase.cumulative_sick_days_ytd > 0` raised `OutOfScopeError` (`cumulative_tiers_not_implemented`) | Earlier days come from the episode dates and from `EmploymentAccrualState.sickness_episodes`; nothing to pre-compute |
| INPS indemnity posted as `sickness_item`, inside the contribution base | `sickness_inps_item` (policy `it/indemnity/sickness_inps`), outside the contribution base; employer integration and carenza pay stay `sickness_item` |
| `SickLeaveEvent` traced as capability `leave`, reason `caller_supplied_amount` | Capability `sickness`, reason `caller_override`: an explicit override, never payable |
| Capability `sickness` `partial`, `leave` `caller_supplied` | `sickness` `native`; `leave` `unsupported` (`outside_input`: no event computes paid leave) |
| `PeriodState.SCHEMA_VERSION` 7 | 8: the accrual state carries `sickness_episodes`; `OpeningBalances.sickness_episodes` imports them |

- Pass the same `SicknessEpisode` (same id and start) to every regular run
  whose month it touches. Adjustment and extra-month runs reject it.
- A relapse needs `relapse_of` naming an episode an earlier run recorded.
- A worker whose level does not fix the category gets a `provisional`
  issue `sickness_inps_cover_unknown` with `fact="category"`: set
  `Employment.category`. `"category"` is a new entry of `PUBLIC_FACTS`.
- The INPS second-band rate in the bundle is now 0.6666 (66.66%), with the
  source D.L. 663/1979, conv. L. 33/1980.

## Partial hire and termination months prorated by the CCNL daily quota

The regular run of a month the employment covers only in part pays the CCNL
daily quotas of its employed days instead of the full monthly pay. The quota
is `work_rules.absence_rules.daily_divisor_method` of the CCNL (`by_26`,
`by_30` or `by_hourly`); see the engine guide for how days are counted.

| Before | After |
|---|---|
| Full monthly pay with a provisional `partial_month_not_prorated` issue (year plans only; `calculate_period` paid the full month silently) | Prorated pay in `calculate_period` and in both year plans; the issue code is gone |
| `base_salary` decision reason `pay_chain_applied` on every run | `pay_chain_prorated` on a prorated run, with `employed_from`, `employed_until`, `divisor_method`, `payable_days`, `divisor` inputs |
| A CCNL without a daily quota paid the full month | No pay posted; `base_salary` decision `provisional`, reason `partial_month_rule_missing`, no amount; `incomplete` issue `partial_month_rule_missing`; not payable |

- Termination and adjustment runs no longer repeat the monthly pay. A
  termination run after the regular run of its month, and every adjustment
  run, post only their own items (`base_salary` reason
  `monthly_pay_posted_by_another_run`, amount 0.00); a termination run with
  no regular run of its month before it pays the month, prorated. Callers
  who relied on the termination or adjustment run carrying a month of pay
  must declare those amounts as events.
- A caller who prorated `period_gross` itself must stop: the engine now
  prorates the pay chain, so the TFR, INPS and IRPEF of the run follow.
- An unpaid absence that deducts more than the prorated pay is rejected
  (`InvalidInputError`), as on a full month.

## Art. 12 family deductions on the reddito complessivo

The family deductions follow the text in force of art. 12 TUIR: the spouse
increase bands of lett. b, the four-decimal ratios of c. 4, months of
dependency counted from dated conditions (c. 3), and the reddito complessivo
of the year instead of the income of this employment alone.

| Before | After |
|---|---|
| `Dependent.months_dependent` (a count, 1-12) | `Dependent.dependent_from` / `dependent_until` (dates, `None` for open); the months are derived, both ends included |
| `Dependent(relationship=CHILD)` without `birth_date` was treated as eligible | Rejected: a child needs its `birth_date`; the age band 21-29 is checked every month |
| The employment income of the run stood for the reddito complessivo | `PeriodInput.current_year` (also `CompetenceYearPlan.current_year`, `TaxYearPlan.current_year`): `CurrentYearTaxFacts(tax_year, other_employment_income, other_income, main_dwelling_income, estimated_on, quality)`; `CurrentYearTaxFacts.employment_only(tax_year, estimated_on)` for no other income |
| Spouse deduction 690 flat from 15,000 to 40,000 | 690 plus 10-30 in the five bands from 29,000 to 35,200 (lett. b) |
| Ratios not truncated; spouse with no income 800 | Ratios truncated to four decimals; no deduction with no income (c. 4) |
| Under-24 own-income limit of 4,000 for children under 24 | For children who turn at most 24 in the year |
| `family_deductions` decision always `final`, rule `art12-tuir` | `final`, or `provisional` with `required_fact_missing` (no amount; incomplete issue `family_income_unknown`, `fact="current_year"`) or `estimated_income_at_conguaglio`; rule `tax/<year>/family-deductions` |
| `family_deductions` capability `partial` (a `partial_implementation` gap) | `native` |
| `compute_family_deductions(...)` returned a 4-tuple, from `payroll.service.family_deductions` | `payroll.service.family.deductions.compute_family_deductions` returns `FamilyDeductions` (one `DependentDeduction` per dependent); spouse, children and ascendants in `payroll.service.family.{spouse,children,ascendants}` |
| `SpouseDeductionRules.breakpoints`, `DeductionBreakpoint` | Statutory parameters on `SpouseDeductionRules`, the bands in `FamilyDeductionRules.spouse_increases`, `ratio_decimals` |

- New public names: `CurrentYearTaxFacts`, `IncomeEstimateQuality`;
  `FamilyComposition.sole_parent`.
- A run with a dependent entitled in some month and no `current_year` of its
  tax year is not payable: state the other income, zero included.

## Competence and tax year plans, conguaglio by payment

A year is now planned two ways: by competence (the runs of one year) and by
tax year (the payments cashed in one year, late payments of an earlier
competence year included). The conguaglio is the payment that leaves no
slot of the tax year unpaid, read from the payments closed, never from a
count.

| Before | After |
|---|---|
| `YearInput` | `CompetenceYearPlan`: same fields and checks (`periods`, `default_facts`, seniority at the first run month, `payment_day` 1-28), plus `payment_dates` (a date per run, keyed like `periods`); field paths read `CompetenceYearPlan.*`, feature `competence_year_plan` |
| `engine.calculate_year(YearInput(...))` → `YearResult` | `engine.calculate_competence_year(CompetenceYearPlan(...))` → `CompetenceYearResult`; runs paid in the next tax year (December after 12 January) open it after the conguaglio of the year |
| none | `engine.calculate_tax_year(TaxYearPlan(tax_year, competence_years, opening_state))` → `TaxYearResult` (`payments`, `conguaglio`) |
| `engine.close_tax_year(year.closing_state)` | Still available; `result.next_opening_state` does it when the year is complete |
| `TaxCashState.withholding_payments_closed` (stored) and `withholding_slots` | `withholding_payments_closed` is read from `payments`; `withholding_slots` is gone; `TaxCashState.conguaglio` is the payment that settled the year and `is_complete` tests it |
| `RunContext.takes_last_slot` from `remaining == 1` | The payment settles when no other slot of its schedule is unpaid; `PeriodInput.planned_payments` states the payments still planned (`()` makes the payment the conguaglio) |
| A standalone run projected the full standard calendar from a count | It projects the standard runs of the tax year not yet paid, in months of the employment |
| `YearInput.opening_state` had to close no run of the year | A plan resumed on a state that closed some of its payments with the same `PaymentId` skips them; another date is rejected (feature `accrual_state`); totals without payments are rejected |
| Runs of a competence year closed in order: regular before extra months | Only regular months are ordered; tredicesima and quattordicesima are independent, nothing closes after the termination run; payments of a tax year close in date order |
| `EarningsYtd.inps_base` | `state.accrual.inps_bases` (`InpsBaseYtd(year, own, other_employers)`, per competence year, kept across tax years); the INPS rules of a run are those of its competence year |
| `OpeningBalances(withholding_payments_closed=..., inps_base=...)`, `.to_state()` | `engine.import_opening_balances(OpeningBalances(payments=..., competence_runs=..., inps_bases=...))`; new `regional_settled`, `municipal_settled`, `credit_recovery_shortfall`; totals need their `payments` |
| `WithholdingSchedule` in `payroll.domain.schedule`, positions by count | `payroll.domain.withholding_schedule`, slots of `PaymentId`, `position(payment, paid)` |

- `PeriodState.SCHEMA_VERSION` is 7. The engine ships no migrator: to
  reuse a persisted state of version 6, move
  `cash.earnings.inps_base` into `accrual.inps_bases` as the `own` base of
  the tax year (exact unless a payment of another competence year was
  made in it), drop `withholding_payments_closed` and `withholding_slots`,
  and set `cash.conguaglio` to the last slot-consuming payment when
  `withholding_payments_closed` had reached `withholding_slots`. A state
  with totals and no payment ids now projects the whole standard calendar
  of the year: list its payments, or import them with `OpeningBalances`.
- New public names: `CompetenceYearPlan`, `CompetenceYearResult`,
  `TaxYearPlan`, `TaxYearResult`, `InpsBaseYtd`. Removed: `YearInput`,
  `YearResult`.
- A late December of 2025 paid in 2026 reads the 2025 INPS tables, which
  the bundle does not hold: it raises `UnsupportedTaxYearError`.

## Competence accrual state and tax cash state

`PeriodState` splits what is accrued from what is paid. A tax year counts
the payments made in it, whatever their competence (TUIR art. 51 c. 1), so
December paid after 12 January no longer exhausts the counters of the next
year.

| Before | After |
|---|---|
| `state.ytd` (`TaxYearState`) | `state.cash` (`TaxCashState`), same YTD accounts |
| `state.obligations` | `state.cash.obligations`; `PeriodState(obligations=...)` becomes `PeriodState(cash=TaxCashState(obligations=...))` |
| `state.ytd.regular_periods_closed` (at most 12 per tax year) | `state.accrual.regular_months(year)`: regular months of a competence year, at most 12 because a run closes once |
| `state.ytd.tax_withholding_periods_closed` (at most 14) | `state.cash.withholding_payments_closed`, no maximum |
| `state.ytd.closed_run_ids` (reset every tax year) | `state.accrual.competence_runs` (kept across tax years) and `state.cash.payments` (`PaymentId` of the tax year) |
| `OpeningBalances(regular_periods_closed=..., tax_withholding_periods_closed=..., closed_run_ids=...)` | `OpeningBalances(withholding_payments_closed=..., payments=(PaymentId.parse("2026-06-regular@2026-06-27"),))` |
| `close_tax_year` reset the closed run ids | `close_tax_year` keeps `state.accrual`: a run closed in N is rejected in N+1 |
| `WithholdingSchedule` slots only of runs of its year | A slot per payment of the tax year, a late run of an earlier competence year included |
| `YearInput.opening_state` closed no run of the tax year | It may hold payments of an earlier competence year already made in the tax year (a late December); they take the first withholding slots |

- `PeriodState.SCHEMA_VERSION` is 6. A persisted state of version 5 maps
  `ytd` to `cash`, moves `obligations` into `cash`, builds
  `accrual.competence_runs` from `closed_run_ids` and `cash.payments` from
  them with their payment dates, and drops `regular_periods_closed`.
- New public name: `PaymentId` (`run_id`, `payment_date`; text form
  `"2026-12-regular@2027-01-13"`).
- A run already closed or out of order in its competence year raises
  `InvalidInputError` with feature `accrual_state` (was `payroll_run`) and
  the message "already closed" (was "already processed"). A payment of a
  run already paid in the tax year raises it with feature
  `tax_cash_state`.
- `TaxCashState`, `EmploymentAccrualState` and `PeriodState` raise
  `InvalidInputError` with the path of the field. A run whose closing state
  breaks their invariants raises `DataIntegrityError`.

## Validated public inputs and one error hierarchy

Every public input is a frozen dataclass validated on construction, its
collections element by element, and every error the engine raises is a
`CcnlEngineError` exported at the root. No `ValueError`, `TypeError`,
`AttributeError` or `decimal` signal reaches the caller for an input or a
data gap.

| Change | What to do |
|---|---|
| `InvalidInputError` no longer subclasses `ValueError` | Catch `InvalidInputError` or `CcnlEngineError`; an `except ValueError` no longer catches rejected input |
| `InvalidInputError.field` | Read the path of the rejected field, e.g. `"PeriodFacts.events[2]"`, `"Employment.roles['x']"`, `"YearInput.periods[6]"`; `remediation` is set whenever `field` is |
| `PeriodFacts(events=...)` accepted any object | Pass only work events; anything else raises `InvalidInputError` naming its position |
| `Employment(roles=...)` accepted any element | Roles are non-blank strings in a `frozenset`; a `set` is rejected |
| `Employment(ccnl_slug=...)` accepted any string | Pass a bundle file name, lower-case letters, digits and hyphens then `.json`; an unknown one raises `UnknownCcnlError` (was `FileNotFoundError`), an unknown level `UnknownLevelError` (was `ValueError`) |
| `Permanent`, `FixedTerm`, `Apprentice`, `Dependent`, `FamilyComposition` were Pydantic models | They are frozen dataclasses: build them with keyword arguments; `model_validate`, `model_dump` and coercion of strings or ints into `Decimal` are gone. `Dependent(relationship="child")` still normalises the string |
| Amounts accepted as `int`, `float` or any `Decimal` | Every amount and rate is a finite `Decimal`, below `1E+9` in magnitude; `NaN`, infinities and floats raise `InvalidInputError` |
| `bool` accepted where an `int` is expected (`YearInput(year=True)`, `months_dependent=True`) | Rejected |
| `datetime` accepted where a `date` is expected | Rejected: a `datetime` does not compare with a `date` |
| `BonusEvent(kind=...)` accepted any string | One of `"bonus"`, `"productivity_bonus"`, `"contract_renewal"` |
| `CalendarOverride(reason="payment_month")` was rejected | Accepted and normalised to the member, like the string values of `RunKind`, `SenioritySource`, `DependentRelationship`, `WorkerCategory`, `EmploymentSector`, `EmployerActivity`, `SubstituteTaxRegime`, `SurtaxComponent`, `OvertimeKind` and the engine mode; `ExtraMonthSchedule.kind` still takes an `ExtraMonthKind` member only |
| `PayrollRun`, `PayrollRunId`, `WorkCalendar`, `ExtraMonthSchedule`, `RecoveryPlan`, `RecoveryObligation`, `SurtaxObligation`, `DeferredShortfall`, `PeriodState` raised `ValueError` | They raise `InvalidInputError` |
| A seniority recognised after the first run raised on the run | `PeriodInput` and `YearInput` reject it on construction (`field="Employment.seniority"`) |
| `YearInput(payment_day=...)` checked by the payment date helper | `InvalidInputError` with `field="YearInput.payment_day"` |
| `OpeningBalances` reasons accepted any string | A lower snake case code such as `"full_amount"` |
| A facade method called with a value of the wrong type raised `AttributeError` | `InvalidInputError` with `field="request"` (or `"closing_state"`, `"ccnl_id"`, `"PayrollEngine.mode"`) |
| `MissingRequiredFactError` was not exported | Import it from `ccnl_engine` |
| `CalculationIssue.fact` `"prior_income"` and `"agreement_signing_date"` | `"employment_income"` and `"agreement_signed_on"`, the public field names; reason codes are unchanged |
| `calculate_year` of a CCNL whose data start during the year failed on `additional_months` | The calendar is read on the first day of the data; a run before it fails on `base_salary`, and a worker hired after it is computed |

## Recognised seniority as a dated fact

Unknown seniority is no longer priced as zero seniority. The months of
service are a fact as of a date, with its source; the engine ages it to
each run and records a `seniority` decision on every run.

| Change | What to do |
|---|---|
| `SeniorityMonths` and `Employment.seniority_months` removed, with `PeriodCalculationRequest.seniority_months` | Pass `Employment(seniority=SeniorityFact(months, as_of, SenioritySource.EMPLOYER_RECORDS))`, or `SeniorityFact.since(recognised_from, source)` from the date the recognised service starts |
| `seniority_months=None` (the old default, which silently paid no increment) | Leave `seniority=None` only when the level pays no seniority increment or service-gated allowance; otherwise the run has a `missing_fact` blocker for `seniority`, a `seniority_unknown` issue and is not payable |
| Zero months | `SeniorityFact(0, as_of, source)`: the decision reason is `zero_confirmed` |
| A constant month count over a year | The fact ages: a `calculate_year` run counts the months completed by the first day of each competence month, so an increment matured during the year is paid from the following month |
| `seniority` decision only with months, reasons `increments_applied` or `no_increment_due` | Always emitted: `not_applicable_by_contract`, `zero_confirmed`, `increments_applied` or `required_fact_missing` (`provisional`, `amount` `None`) |
| Capability registry `required_facts`: `employment.seniority_months` | `employment.seniority` |

## IVS massimale from the contribution history

Whether the IVS massimale applies is no longer a status the caller states:
the engine derives it from the worker's contribution history
(L. 335/1995 art. 2 c. 18). Without the history, a run whose INPS base
crosses the massimale is not payable and names the missing fact.

| Change | What to do |
|---|---|
| `ContributionCeilingStatus` removed, with `Employment.ceiling_status` and `PeriodCalculationRequest.ceiling_status` | Pass `Employment(contribution_history=ContributionHistory(first_enrolled_on=..., contributory_option=...))` |
| `POST_1995` | `ContributionHistory(first_enrolled_on=<first contribution, from 1996>)` |
| `OPTED_IN` | `ContributionHistory(first_enrolled_on=<first contribution>, contributory_option=True)` |
| `NOT_APPLICABLE` | `ContributionHistory(first_enrolled_on=<first contribution, before 1996>)`; supply the history in force for the run (a credit of pre-1996 periods or the option counts only from its effective date) |
| `UNKNOWN` (the old default, which silently computed the uncapped branch) | Leave `contribution_history=None`: up to the massimale nothing changes; beyond it the run has a `missing_fact` blocker for `contribution_history`, an `ivs_ceiling_eligibility_unknown` issue and is not payable |
| New decision `ivs_ceiling_eligibility` on every run whose INPS rules carry a massimale | Read its `reason_code` and `inputs` to see why the massimale applies or not |
| `inps_employee` and `inps_employer` decisions: input `ivs_ceiling_applies` replaced by `ivs_ceiling` (`applied`, `not_applied`, `undetermined`); with `undetermined` the decision is `incomplete` and its `amount` is `None`, so the coverage is `incomplete` with `capability_not_computed` blockers for both | Do not pay the INPS amounts of such a run; the breakdown carries the uncapped simulation |
| `resolve_contributions` takes `ytd_inps_base` and `ivs_ceiling_applies` without defaults | Pass both |

## Model limitations

Known simplifications are typed data. A run records the limitations that
apply to it, and an open one that can move an amount blocks payment.

| Change | What to do |
|---|---|
| `ResultAssurance.limitations` added (`tuple[ModelLimitation, ...]`), also on `YearResult.assurance` | Read it to see which simplifications concern the run |
| `BlockerCode.OPEN_LIMITATION` added (`feature`: capability, `detail`: limitation id) | Branch on it; validate the amount outside the engine or wait for the limitation to be resolved |
| A `simplification` coverage note must state `monetary_impact` (`yes`, `no`, `unknown`); with `yes` or `unknown` it must name its `capability` and declare a `limitation` (`variant`, `applies_when`, `status`, `remediation`) | Add the fields to the note, or the file does not load |
| `KnowledgeRepository.load_engine_limitations()` added | Implement it in a custom repository (delegate to the bundled one) |
| An open limitation with an impact lowers its capability to `partial` in the contracts index and the capability matrix | Nothing |
| New public names `ModelLimitation`, `MonetaryImpact`, `LimitationStatus` | Import them from `ccnl_engine` |

## Capability coverage from one registry

The capability catalog of each fiscal year is now the single source of
coverage. The runtime capability report, the contracts index and the
capability matrix derive from it; CCNL files no longer declare coverage
flags.

| Change | What to do |
|---|---|
| `CapabilityStatus` removed; `CapabilityEntry.status` replaced by `implementation` (`CapabilityImplementation`: `native`, `caller_supplied`, `partial`, `unsupported`) | Read `entry.implementation` |
| `CapabilityEntry` adds `layer`, `applies_when`, `handler`, `evidence`, `variants`, `required_facts` | Nothing, unless you build entries: pass them |
| `CapabilityCatalog.gaps()` removed | Read `result.capability_report.gaps` |
| `CapabilityGap.declared` renamed `implementation` | Rename the attribute |
| Gap kinds: `feature_absent` and `not_computed` replaced by `unsupported`; `promised_computed_got_partial` renamed `partial_result`; `partial_implementation` added | Branch on the new values |
| `CapabilityReport.scope` added (`CapabilityScope`: `applicable`, `not_applicable`, `outside_input`) | Read it to know which capabilities concern the run |
| An unsupported capability is a gap only when it applies: an ordinary month has no gap; the run that closes the employment has `termination_residual_leave` | Expect `coverage == "complete"` on ordinary runs; payability still depends on the other blockers |
| A partial capability that executes (sickness, family deductions, foreign tax credit, pension fund) is a `partial_implementation` gap and blocks payment | Validate those amounts outside the engine |
| `CapabilityReport.evidence_required` and `weak_sources()` added; `rule_source_weak` follows the evidence of each registry entry (`derived` for all today) | Nothing |
| CCNL `coverage.gross`, `coverage.net`, `coverage.work_rules`, `coverage.work_rules_features` removed, and `CoverageStatus`, `WorkRuleFeature` removed from `ccnl_engine.contract.domain.identity` | Derive coverage with `ccnl_engine.payroll.service.capability_coverage.ccnl_capabilities` |
| A `missing` coverage note must name its `capability` | Add `"capability"` to the note |
| New public names `CapabilityImplementation`, `CapabilityScope` | Import them from `ccnl_engine` |
| The contracts index drops the coverage percentage; it shows coverage, sources and readiness as separate columns | Nothing |

## Ruleset readiness and engine modes

Readiness is part of the public API, and the engine takes a mode. Amounts are
unchanged in both modes.

| Change | What to do |
|---|---|
| `CcnlInfo` replaced by `ContractSummary` (adds `readiness`) | Rename the type; read `summary.readiness` |
| `list_ccnls()` removed | Call `PayrollEngine.list_contracts()` |
| `engine.inspect_ruleset(ccnl_id)` added | Returns the `RulesetAssurance` of a CCNL, by slug or CNEL code |
| `result.rulesets` and `assurance.rulesets` hold `RulesetAssurance`, not `RulesetIdentity` | Read `ruleset.identity` for the old value; `id`, `source_hash` and `str()` are unchanged; `kind`, `readiness` and `confidence` are new |
| The CCNL ruleset is always in `result.rulesets` | Nothing |
| `PayrollEngine.bundled(mode=...)` and `PayrollEngine(mode=...)` added; `result.mode`, `assurance.mode` | Default `"simulation"` keeps today's payability; `"operational"` adds a `ruleset_not_production` blocker for a CCNL ruleset that is not `production` |
| `BlockerCode.RULESET_NOT_PRODUCTION` added | Branch on it when running in operational mode |
| New public names `ContractSummary`, `EngineMode`, `RulesetAssurance`, `RulesetKind`, `RulesetReadiness`, `VerificationStatus` | Import them from `ccnl_engine` |
| Docs no longer point to `ccnl.verification.readiness` | Use the public fields above |

## Result assurance replaces the result status

`PeriodResult.status` and `YearResult.status` are removed, with no alias. The
question "can this amount be paid?" now has one answer, `result.is_payable`,
derived from a `ResultAssurance` that also reads the capability report, the
provenance of the executed rules and the caller-supplied rules, which the old
status ignored. See [Assurance](trust/confidence.md).

| Change | What to do |
|---|---|
| `PeriodResult.status`, `YearResult.status` removed | Read `result.is_payable` to decide whether to pay, `result.blockers` for why not, `result.assurance.calculation` for the old worst status of the issues (now also of the decisions) |
| `PeriodResult.assurance`, `is_payable`, `blockers`, `rulesets` and the same on `YearResult` added | A year is payable only when every run is; its blockers and rulesets are listed once |
| `CapabilityReport.confidence` removed; `CapabilityReport.status` is a `CoverageStatus` | Read `result.assurance.coverage`; the values `complete`, `partial`, `incomplete` are unchanged |
| `CalculationIssue.fact` added | An issue about a missing fact names it; it becomes a `missing_fact` blocker |
| New public names `ResultAssurance`, `ResultBlocker`, `BlockerCode`, `CoverageStatus`, `EvidenceStatus`, `Payability`, `RulesetIdentity` | Import them from `ccnl_engine` |

A result that was `final` is not payable when the catalog lists a capability
the run did not compute, an executed rule is `assumed` or `missing`, or the
caller supplied a rule: today no bundled CCNL gives a payable result. Amounts
are unchanged.

## Withholding rule cited per tax year

Art. 23 D.P.R. 600/1973 is in force until 31 December 2026; from 1 January
2027 its rules are art. 33 of the testo unico of D.Lgs. 33/2025 (art. 243 c.
1 as amended by D.L. 200/2025 art. 4 c. 4), with renumbered commi. The
decisions and messages that cite it now take the rule of the tax year they
compute. No amount changes.

| Change | What to do |
|---|---|
| `withholding_shortfall` and `shortfall_deferral` decisions carry a `source` (art. 23 c. 3 DPR 600/1973 for 2026, art. 33 c. 4 D.Lgs. 33/2025 from 2027) | Nothing for 2026: the rule id stays `dpr600-1973-art23-c3`; from 2027 it is `dlgs33-2025-art33-c4` |
| The `withholding_shortfall_unrecovered` and `deferred_shortfall_unrecovered` issues, the household-employer `InvalidInputError` and the `foreign_tax_credit` component `fonte` cite the rule of the tax year | Match on the issue code, not on the message text |
| The source URL of art. 23 c. 1 DPR 600/1973 pins the version in force until 31 December 2026 (`!vig=2026-12-31`); art. 33 D.Lgs. 33/2025 points to Normattiva | Nothing |
