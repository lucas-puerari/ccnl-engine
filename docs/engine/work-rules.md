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
| `ArrearsEvent` | `amount`, `separate_tax_rate`, `reference_period` | Renewal arrears; see [Renewal arrears](#renewal-arrears) |
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

from ccnl_engine.events import OvertimeEvent, OvertimeKind

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
| past the comporto | left out, `incomplete` issue | left out |

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
not fix it. For most CCNLs the tier is the one of the month of sickness
(30 days) the day falls in, so a month that crosses a tier threshold pays
each day its own rate, and the comporto ends past `max_duration_days` of
the episode and its relapses. A CCNL that counts several episodes sets a
cumulation instead ([below](#sickness-counted-over-several-episodes)).

The payable days of each class are counted with the CCNL daily quota of an
unpaid absence (`work_rules.absence_rules.daily_divisor_method`), the same
count as a hire or termination month, and never exceed one monthly pay,
however many episodes the month holds: the episodes of a run are taken by
first day, whatever their order in the facts, and the days past the pay
left by the earlier ones are dropped. Their pay is rounded once on the days
counted so far, not band by band, so the sick days of a month never deduct
more than the monthly pay. The run deducts the daily pay of the sick days (`absence_deduction`) and pays
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
(`sickness_inps_daily_base`), and, for a CCNL without a cumulation, tiers
and comporto count one relapse chain, not the CCNL window across episodes
(`sickness_cumulation_window`).

#### Sickness counted over several episodes

`work_rules.sickness_rules.cumulation` holds the rules of a CCNL that
counts the sickness of several episodes. Metalmeccanici Federmeccanica
(Sez. Quarta Titolo VI Art. 2) is the first:

| Seniority | Full pay | Then | Comporto breve |
|---|---|---|---|
| up to 3 years | first 122 days of the chain | 80% | 183 days |
| 3 to 6 years | first 153 days | 80% | 274 days |
| over 6 years | first 214 days | 80% | 365 days |

- The chain sums the days of consecutive episodes; it restarts for an
  episode that starts after at least 61 calendar days of work.
- The comporto counts the sick days of the three years that end on the
  day; a day past it is left out with an `incomplete` issue (the comporto
  prolungato and the days added for a certified disability are not
  modelled).
- From the fourth short absence (at most 5 days) of a calendar year, the
  first three days are paid 66%, from the fifth 50%, unless the CCNL
  exempts the absence (`SicknessEpisode.short_absence_exempt`).
- The band is the one of the seniority on the first day of the episode.

A fact the engine does not know raises a `provisional` issue, a blocker,
only when it could change a day the run pays:

| Issue | When | Settled by |
|---|---|---|
| `sickness_history_unknown` | days before the recorded history could pass a threshold | `OpeningBalances.sickness_known_from` (the hire date when the imported episodes are complete), or `Employment.employment_period` |
| `sickness_seniority_unknown` | the counts pass the days of the first band | `Employment.seniority` |
| `sickness_short_absence_exemption_unknown` | a short absence could be reduced | `SicknessEpisode.short_absence_exempt` |
| `sickness_seniority_band_changes` | the band changes within the days paid | not modelled |
| `sickness_hospital_stay_not_modelled` | a day is paid at 80% (a hospital stay over 10 days is paid in full) | not modelled |
| `sickness_fixed_term_proportion` | a fixed-term contract (periods scaled to its length) | not modelled |

An import without `sickness_known_from` lists the sickness of its tax year
only, from 1 January; the engine's own chained state lists every sick day
of the employment.

#### A month whose days differ from the divisor

No CCNL text in the bundle says how a month of sickness is deducted when
its payable days differ from the divisor, so the run raises the
`provisional` issue `sickness_month_quota_mismatch` when every payable day
of a fully posted month is sick yet part of the pay is left (24/26 of a
February by 26), or a payable day is worked yet the sick days deduct the
whole pay (sick 1 to 30 of a 31-day month by 30).

`SickLeaveEvent` remains as an explicit override: an amount the caller
computed. It records a caller-supplied `sickness` decision, so the result is
never payable.

### Absences are bounded by the pay of the run

Unpaid absences that deduct more than the monthly pay of the run raise
`InvalidInputError` before any amount is computed: check the hours and the
hourly rate. The sick days of `SicknessEpisode` are capped at the monthly
pay by construction ([Sickness](#sickness)). An `AbsenceEvent` on a day of
an episode raises `InvalidInputError`; on another day of the month it is
deducted at the caller's rate beside the sick days at the CCNL quota, with
the `provisional` issue `sickness_with_unpaid_absence`, and when the two
exceed the pay the run raises `OutOfScopeError` with reason
`sickness_with_unpaid_absence`. Absences below the pay can still leave less than the IRPEF and
surtax due on the run (the withholding follows the projected annual income).
The taxes are then withheld up to the pay left and the rest is carried to
the next runs of the tax year
([Fiscal](fiscal.md#pay-that-does-not-cover-the-tax)). A run whose other
deductions (INPS, substitute tax, recovery installments) exceed the pay
left still raises `OutOfScopeError` with reason `withholding_shortfall`.

### Fringe benefits

For tax years 2025 to 2027 goods and services granted to the worker are
exempt from IRPEF and INPS up to 1,000 EUR in the year, or 2,000 EUR when the
worker has children "che si trovano nelle condizioni previste dall'articolo
12, comma 2" TUIR and declares them to the employer with their tax codes
(L. 207/2024 art. 1 cc. 390-391, derogating TUIR art. 51 c. 3). The engine
derives the condition from `PeriodFacts.family_composition`: declare every
child, a minor too, as a `Dependent` once the worker has made the
declaration. A child counts when its dependency interval touches the tax
year and its `own_income` is within the limit of art. 12 c. 2 (2,840.51
EUR, 4,000 EUR for a child who turns at most 24 in the year); the age band
and the residency condition of the art. 12 deduction do not apply. When the
condition is unknown (no family composition, or a child's `own_income` left
`None` and no other child within the limit) the 1,000 EUR threshold is
applied and, if the 2,000 EUR one would tax another amount, the decision is
`provisional` with an `incomplete` issue `fringe_threshold_undetermined`
(`fact="own_income"` when a composition is given), so the run is not
payable.

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

### Renewal arrears

Art. 17 c. 1 lett. b TUIR taxes separately the "emolumenti arretrati per
prestazioni di lavoro dipendente riferibili ad anni precedenti" received
by effect of a collective agreement; art. 21 c. 1 sets the rate on half
the income of the two years before the year of receipt, which the engine
does not know: the caller supplies it as `separate_tax_rate`.
`reference_period` is compared with the tax year of the run (a December
paid by 12 January belongs to its year):

| `reference_period` | Taxation | `contract_renewal_arrears` decision |
|---|---|---|
| An earlier tax year | Separate, `amount x separate_tax_rate` on `separate_tax` (code 1002) | `separate_taxation`, final |
| The tax year of the run | Ordinary IRPEF with the run; the rate is not used | `ordinary_taxation`, final |
| `None` | Separate, as a simulation, with an `arrears_reference_period_unknown` issue and a `missing_fact reference_period` blocker | `reference_period_unknown`, incomplete |
| A later year | `InvalidInputError` | |

The arrears enter the INPS base of the run in every case.

---

## Reading the result

Each event produces pay items and ledger entries on the period result. A
condition that lowers the reliability of the result (for example an unknown
prior-year income) is reported in `result.issues` and blocks
`result.is_payable`. See [Results and calculation status](../api/engine.md#results-and-calculation-status).
