# Work rules (L3)

Variable work data for a payroll run (overtime, absences, sick leave,
supplements, benefits, bonuses) is passed as work events in
`PeriodFacts.events`: on `PeriodInput.facts` for one run, or in
`CompetenceYearPlan.periods` keyed by month or by run id for a year. Events are part
of the run and change the
result according to the treatment in the table below. For example, overtime
raises `period_gross`; an unpaid absence is reported in
`unpaid_absence_deduction`; a bilateral fund contribution changes only
`period_net` and `period_employer_cost`. Each event appears as pay items in
`result.pay_items`.

Import event types from the `ccnl_engine` package, like every other public name.

```python
--8<-- "docs/examples/12_work_rules.py"
```

---

## Event types

All events are frozen dataclasses. Every event carries an `event_date`;
amounts are `Decimal` values in EUR, validated on construction.

| Event | Fields | Treatment |
|---|---|---|
| `OvertimeEvent` | `hours`, `hourly_rate`, `multiplier` (default `None`: from the CCNL band), `kind` (`OvertimeKind`, default `WEEKDAY`) | Pay `hours × hourly_rate × multiplier`; subject to INPS, IRPEF and TFR |
| `NightShiftEvent` | `supplement_amount` | Night-work supplement; INPS and IRPEF |
| `HolidayWorkEvent` | `supplement_amount` | Public holiday or weekly rest-day supplement; INPS and IRPEF, no TFR |
| `ShiftWorkEvent` | `supplement_amount` | Shift allowance; INPS and IRPEF, no TFR |
| `AbsenceEvent` | `hours`, `hourly_rate`, `end_date`, `suspends_accrual` | Unpaid absence deducted from pay; reduces the INPS and TFR base |
| `SicknessEpisode` | `episode_id`, `started_on`, `ended_on`, `relapse_of` | Sickness episode; the engine derives the deduction, INPS indemnity, CCNL integration and carenza pay of the days in the run's month; see [Sickness](#sickness) |
| `SickLeaveEvent` | `amount`, `sick_days`, `waiting_period_days` | Sick pay the caller computed: an override of the engine, never payable; INPS and IRPEF, no TFR |
| `FringeEvent` | `amount` | Fringe benefit (art. 51 c. 3 TUIR); exempt while the year total stays within the threshold, then the whole year total is taxable; see [Fringe benefits](#fringe-benefits) |
| `WelfareEvent` | `amount` | Welfare benefit; exempt from INPS and IRPEF, no TFR |
| `BonusEvent` | `amount`, `kind`, `agreement_signed_on` | One-off bonus; `kind` selects ordinary IRPEF, the PdR regime or the renewal regime |
| `BilateralFundEvent` | `employee_amount`, `employer_amount` | Bilateral or health fund contribution; see [Pay components](pay-components.md#bilateral-funds-fondi-bilaterali) |
| `ArrearsEvent` | `amount`, `separate_tax_rate`, `reference_period` | Renewal arrears under tassazione separata (art. 17 TUIR) |
| `TerminationTFREvent` | `amount`, `separate_tax_rate` | TFR settlement at cessazione (art. 19 TUIR) |

### Overtime multiplier

D.Lgs. 66/2003 art. 5 c. 5 leaves the overtime supplement to the CCNL and
sets no statutory rate, so the engine has no default multiplier.

| `multiplier` | CCNL band of `kind` | Paid with | Decision and status |
|---|---|---|---|
| `None` | present | `1 + band` | `overtime` decision `ccnl_overtime_band_applied`, origin `engine`, citing the band and its source |
| `None` | absent | nothing: `InvalidInputError` | the run is rejected; pass an explicit multiplier |
| explicit | equal to a band | the caller's value | `caller_supplied` decision only |
| explicit | different | the caller's value | `caller_supplied` decision and a `provisional` issue `caller_multiplier_differs_from_ccnl` with both values |
| explicit | absent | the caller's value | `caller_supplied` decision only |

A caller-supplied multiplier, matching a band or not, is a
`caller_supplied_rule` blocker: the result is not payable until the value is
validated outside the engine.

`kind` selects the band: `WEEKDAY` (straordinario diurno), `NIGHT`,
`HOLIDAY` or `NIGHT_HOLIDAY`, matched against the `applies_to_kinds` of the
CCNL `work_rules.time_supplements.overtime_bands`. The band used is the
first tier: the percentage band with code `OT_*` that has no hour threshold
and no context condition. When the CCNL also has bands that start beyond a
daily or weekly hour threshold (commercio: 15% up to 48 weekly hours, 20%
beyond; metalmeccanico: 25% for the first two hours, 30% beyond), the event does not carry the hours of the week, so the first tier
is applied to every hour and the run is `provisional` with issue
`overtime_tier_not_applied`: pass an explicit multiplier for the hours
beyond the threshold (a multiplier equal to a higher tier raises no
difference issue). A CCNL whose bands for the kind all start beyond a
threshold, are paid in EUR per hour, or are not in force on the event date
gives no multiplier. The derived band is a payable rule of `overtime`: its
provenance status is reported in `capability_report.rule_sources`.

```python
from datetime import date
from decimal import Decimal

from ccnl_engine import OvertimeEvent, OvertimeKind

# Metalmeccanico OT_NOTTURNO 50%: 2 h x 15.00 EUR x 1.50 = 45.00 EUR.
night = OvertimeEvent(
    date(2026, 3, 10), Decimal(2), Decimal("15.00"), kind=OvertimeKind.NIGHT
)
```

### Other rates and amounts are caller inputs

`OvertimeEvent.hourly_rate`, the `supplement_amount` of night, holiday and
shift events, and the `separate_tax_rate` of arrears and TFR settlements come
from the caller.

### Sickness

A `SicknessEpisode` is one illness: a stable `episode_id`, the first and
last day on the certificates and, for a relapse (*ricaduta*), the
`relapse_of` id of the episode it continues. Pass the same episode, same id
and start, to every regular run whose month it touches; a later run may
extend `ended_on`. Only the run that posts the monthly pay of its month
(a regular run, or a termination run when the regular run is not closed)
accepts an episode, so no day is paid twice.

Each calendar day has an index in the episode, counted on from the episode
it continues for a relapse. The index sets:

| Days | INPS (D.L. 663/1979, conv. L. 33/1980) | Worker receives |
|---|---|---|
| 1-3 (carenza) | nothing | CCNL `carenza_integration_rate` |
| 4-20 | 50% | the higher of the CCNL tier rate and the INPS rate |
| 21-180 | 66.66% | the same |
| past `max_duration_days` (comporto) | left out, `incomplete` issue | left out |

INPS pays at most 180 days a calendar year, counted over every recorded
episode. INPS covers the worker by the rules of
`knowledge/inps/data/sick-pay-rates.json`: operai of industry and the
terziario and impiegati of the terziario (secondary source), operai of the
building and artisan sectors, quadri of the terziario and apprentices
(unverified); not impiegati and quadri of industry (secondary source),
dirigenti, public employees or domestic workers (unverified). Each rule
names its source in the file. Without a rule the cover is unknown: the days
are paid at the CCNL rate only and a `provisional` issue
`sickness_inps_cover_unknown` names the fact `category` when the level does
not fix it. The CCNL tier is the one of the month of sickness (30 days) the
day falls in, so a month that crosses a tier threshold pays each day its own
rate.

The payable days of each class are counted with the CCNL daily quota of an
unpaid absence (`work_rules.absence_rules.daily_divisor_method`), the same
count as a hire or termination month, and never exceed one monthly pay. The
run deducts the daily pay of the sick days (`absence_deduction`) and pays
back the INPS share as `sickness_inps_item` (outside the contribution base,
the days are covered by figurative contributions) and the employer share
and carenza pay as `sickness_item`. TFR keeps the full monthly pay (art.
2120 c. 3 c.c.).

The closing state records each episode up to its last processed day
(`EmploymentAccrualState.sickness_episodes`); `OpeningBalances` takes the
same records for a worker taken over from another provider. Each episode
records one `sickness` decision with the classified days in its inputs.

| Missing | Effect |
|---|---|
| CCNL `work_rules.sickness_rules` | Nothing posted; `incomplete` issue `sickness_rule_missing` |
| CCNL daily quota | Nothing posted; `incomplete` issue `sickness_daily_quota_missing` |

Two engine limitations stay open: the INPS share uses the CCNL daily quota
of the month instead of the INPS daily base of the month before
(`sickness_inps_daily_base`), and CCNL tiers and comporto count one relapse
chain, not the CCNL window across episodes (`sickness_cumulation_window`).

`SickLeaveEvent` remains as an explicit override: an amount the caller
computed. It records a caller-supplied `sickness` decision, so the result is
never payable.

### Absences are bounded by the pay of the run

Unpaid absences (`AbsenceEvent`, and the deduction of a
`SicknessEpisode`) that deduct more than the monthly pay of the run raise
`InvalidInputError` before any amount is computed: check the hours and the
hourly rate. Absences below the pay can still leave less than the IRPEF and
surtax due on the run (the withholding follows the projected annual income).
The taxes are then withheld up to the pay left and the rest is carried to
the next runs of the tax year
([Fiscal](fiscal.md#pay-that-does-not-cover-the-tax)). A run whose other
deductions (INPS, substitute tax, recovery installments) exceed the pay
left still raises `OutOfScopeError` with reason `withholding_shortfall`.

### Fringe benefits

For tax years 2025 to 2027 goods and services granted to the worker are
exempt from IRPEF and INPS up to 1,000 EUR in the year, or 2,000 EUR when the
worker has a fiscally dependent child (art. 12 c. 2 TUIR) and declares it to
the employer with the child's tax code (L. 207/2024 art. 1 cc. 390-391,
derogating TUIR art. 51 c. 3). Set `PeriodFacts.has_dependent_children` on
every run of the year once the declaration is made; the engine does not
derive it from `family_composition`.

The threshold is all or nothing (AdE circ. 4/E of 16 May 2025, par. 2.7): an
amount equal to the threshold is still exempt, but once the year total
exceeds it the whole amount of the year is taxable, not only the excess. The
year total comes from `opening_state.cash.fringe`, so chain the closing state
of each run into the next. The benefit that crosses the threshold makes the
earlier exempt amounts of the year taxable in its run. For example, 600 EUR
in February is exempt; another 600 EUR in March brings the year to 1,200 EUR
and makes 1,200 EUR taxable in March; a further 300 EUR in April is taxable
on its own.

Each `FringeEvent` reports:

- on its `FringeBenefitItem`: `threshold_annual`, `ytd_total` (year total
  including the benefit) and `taxable_amount` (which can exceed `amount` on
  the crossing benefit);
- a `fringe_benefit` decision in `result.decisions`, with reason
  `within_threshold`, `above_threshold` or `above_threshold_retroactive`,
  the threshold and the children condition, the year totals, the
  `retroactive_amount` and the taxable amount as `amount`.

### Substitute-tax regimes

The prior-year employment income and the written waivers that decide
eligibility for the substitute-tax regimes are declared once, in
`PriorYearTaxFacts` on the input, not on each event. The sector is declared on
`Employment` and the employer activity on `EmployerProfile`. An unknown fact
means ordinary taxation; for night, holiday and shift supplements and for
renewal increments the result is then provisional. A renewal increment
(`BonusEvent` with `kind="contract_renewal"`) carries the signing date of its
renewal in `agreement_signed_on`. See
[Substitute tax regimes](substitute-tax-regimes.md).

---

## Reading the result

Each event produces pay items and ledger entries on the period result. A
condition that lowers the reliability of the result (for example an unknown
prior-year income) is reported in `result.issues` and blocks
`result.is_payable`. See [Results and calculation status](../api/engine.md#results-and-calculation-status).
