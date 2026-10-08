# Migration guide

Changes are listed newest first. Older changes are on
[Migration guide: earlier releases](migration-earlier.md) and
[Migration guide: inputs and legacy APIs](migration-legacy.md).

## Fon.Te. rates on the TFR base

| Before | After |
|---|---|
| Fund rates applied to the INPS base only; no fund in Commercio, Turismo, Pubblici esercizi or Agenzie di viaggio, so an enrolment there raised `InvalidInputError` | `EmployerFund.contribution_base` (`FundContributionBase.INPS_BASE`, the default, or `TFR_BASE`); Fon.Te. (`"FONTE"`, employer 1.55%, employee at least 0.55%, on the TFR base) on those five CCNLs |

## Partial years also leave out runs without a seniority amount

| Before | After |
|---|---|
| A competence year left out only the runs before the base salary of the level; a seniority table starting later raised `MissingRuleError` (grafica editoria with a recognised seniority, January to June 2026) | The runs before the seniority amount of the level are also left out when the employment states a seniority, each with a `run_not_computed` blocker |

## Tredicesima of the CCNL Terziario on Christmas Eve

| Before | After |
|---|---|
| The tredicesima of a Commercio competence year was paid on `payment_day` of December, after the December run, and settled the conguaglio | Paid on 24 December (CCNL Terziario art. 220, "in coincidenza con la vigilia di Natale"); the December run of the 28th is the last payment of the year and settles the conguaglio |
| `CCNLParameters.fourteenth_payment_day` only | New `CCNLParameters.thirteenth_payment_day`; a date the plan names, or a calendar override, still wins |

## Results pickle and states persist as JSON

| Before | After |
|---|---|
| `PeriodResult` could not be pickled or deep-copied (`mappingproxy` in its capability report and decision inputs), so a batch could not fan runs out to worker processes | Those mappings are immutable `dict`s: a result pickles and deep-copies equal |
| No public way to persist a `PeriodState` but pickle | `ccnl_engine.inputs.period_state_to_json(state)` and `period_state_from_json(text)`: tagged JSON with `PeriodState.SCHEMA_VERSION`; reading rejects another version and any type outside the payroll domain with `InvalidInputError` |

## Input bounds and the gross actually paid

| Before | After |
|---|---|
| `PayrollRun.regular(10000, 12)` was accepted and `PeriodInput` raised a bare `ValueError` | A year outside 1970-9998 raises `InvalidInputError` on the run, the run id and the plan |
| `OvertimeEvent.hours` had no upper bound | At most 744 hours (a month of 31 days), else `InvalidInputError` |
| `CompetenceYearPlan.periods` and `payment_dates` kept the caller's dict | The plan keeps its own copy |
| `period_gross` includes sick pay on top of the contractual pay, the days not paid being in `unpaid_absence_deduction` | New `PeriodResult.paid_gross`: `period_gross - unpaid_absence_deduction`, the gross the payslip pays |

## One CCNL identifier and the levels of a CCNL

| Before | After |
|---|---|
| `Employment.ccnl_slug` took the bundle file name only (`"anas.json"`), `list_contracts()` and `inspect_ruleset()` the id only (`"anas"`) | Every entry point takes the id with or without `.json`; `Employment.ccnl_slug` stores the file name |
| The levels of a CCNL were readable only through internal loaders | `PayrollEngine.list_levels(ccnl_id)` returns a `LevelSummary` (`code`, `description`, `category`) per level, exported by `ccnl_engine.catalog` |

## Supported tax years in the catalog

| Before | After |
|---|---|
| A payment of a tax year without bundled tables raised `UnsupportedTaxYearError` with a generic remediation | The error carries `supported`, the tax years the bundle ships, and names them in its remediation |
| No public way to know the bundled tax years before a run | `ccnl_engine.catalog.supported_tax_years()` |

## Pension fund enrolment needed on every CCNL with a negotiated fund

| Before | After |
|---|---|
| `pension_fund=None` blocked only on the three CCNLs whose fund data the bundle holds | It blocks on every CCNL but domestic work (`missing_fact pension_fund`): most CCNLs have a negotiated fund the bundle does not hold, and an enrolled worker's contributions and TFR destination are then undetermined |
| A run on another CCNL left the enrolment unread | State `NoPensionFund()` for a worker not enrolled; an enrolment in a fund whose data the bundle does not hold raises `InvalidInputError` |

## Extra months at the termination of chained runs

| Before | After |
|---|---|
| A tredicesima paid before the termination month, then the regular run of the termination month, liquidated the ratei of the same window again | The run of the termination month leaves that extra month out and records the incomplete issue `extra_month_paid_before_termination` |
| Chained runs counted only the absences of the termination run in the ratei they liquidated | The run records the provisional issue `termination_window_absences_unknown` when earlier months of the window were closed before it |
| CCNL Agenti immobiliari FIAIP: the quattordicesima of a competence year was paid on `payment_day` of June | Paid on 1 July (art. 169, recorded as `assumed`: the clause is not located in a bundled source) |

## Somma esente in its own ruleset

The somma esente bands of L. 207/2024 art. 1 cc. 4-5 (7.1% up to €8,500,
5.3% up to €15,000, 4.8% above, reddito complessivo up to €20,000) moved
from the eight `estimated` sector tax files to
`knowledge/tax/data/somma-esente-2026.json`, an `official_primary` ruleset
whose record is `derived`, quoting the Gazzetta Ufficiale text. The values
are unchanged, so no amount changes; the `rule_source_weak` blocker on
`somma_esente` is gone.

| Before | After |
|---|---|
| Rule `tax/2026/<sector>:somma_esente`, `assumed` | Rule `tax/2026/somma-esente:somma_esente`, `derived`; `result.rulesets` lists `tax/2026/somma-esente` when the capability runs |
| `YearRulesRaw.somma_esente` read from the sector file | Field removed: a sector file with a `somma_esente` block does not validate; `load_year_rules` takes it from `load_somma_esente_rules(year)` |
| `SommaEsenteRules(bands, provenance)` | Also `ruleset`, the identity of the year file |

## NASpI surcharge of fixed-term contracts

The surcharge of L. 92/2012 art. 2 c. 28 was a flat 1.4% on every
`FixedTerm`. It now adds 0.5% per renewal, is not charged in the cases of
c. 29 nor to the operai agricoli (c. 3), and blocks the run while a fact it
depends on is unknown (see
[Employment types](domain/employment-types.md#naspi-surcharge)).

| Before | After |
|---|---|
| `Employment.contract_type` defaulted to `Permanent()` | Required: pass `Permanent()`, `FixedTerm(...)` or `Apprentice(...)` |
| `FixedTerm()` had no field and always charged 1.4% | `FixedTerm(renewals=..., naspi_exclusion=...)`; `NaspiExclusion` exported by `ccnl_engine.inputs`. `None`, the default of both, is unknown: a `missing_fact renewals` or `naspi_exclusion` blocker and no amount on the `inps_employer` decision |
| A fixed-term operaio agricolo paid 1.4% | No surcharge; a level of the agricoltura sector whose category is open has a `missing_fact category` blocker |
| A domestic fixed term always took the fixed-term hourly rate | An excluded one (e.g. `REPLACEMENT`) takes the permanent rate; renewals add nothing |
| The `inps_employer` decision of a fixed term had no surcharge input | Inputs `naspi_surcharge`, `naspi_surcharge_rate`, `naspi_renewals`; issue `naspi_surcharge_undetermined` |
| `YearRules` and the tax data files had `fixed_term_additional_rate` alone | Also `fixed_term_renewal_increment` (required) and `fixed_term_exempt_categories`, under the same provenance record |

## Renewal regime assessed on the minimo

L. 199/2025 art. 1 c. 7 taxes at 5% the 2026 increments of renewals signed
from 2024 to 2026, which a renewal usually pays inside the minimo. The
engine assessed the regime only on a `BonusEvent` of kind
`contract_renewal`; see
[Substitute-tax regimes](engine/substitute-tax-regimes.md#increments-paid-inside-the-minimo).

| Before | After |
|---|---|
| A 2026 run whose minimo comes from a table dated 2024-2026 took no `rinnovo_substitute_tax` decision and taxed the minimo as ordinary income in silence, whatever the 2025 income | It takes one (`inputs["paid_in"] == "minimum"`, amount zero): `final` when a known fact excludes the worker; otherwise `provisional`, with a `missing_fact` blocker naming `employment_income` or `sector`, or, for a worker who meets the requirements, a `calculation_issue` blocker `rinnovo_minimum_increment_unquantified` |
| `PriorYearTaxFacts()` left a 2026 private run payable as far as the renewal regime went | State `PriorYearTaxFacts(employment_income=...)` and `Employment.sector`; a worker who waived the regime in writing states `waived_regimes={SubstituteTaxRegime.RINNOVO}` |

## Stating a fact never adds a blocker its default lacks

Several defaults selected a branch without a blocker, so the true fact was the
only path that blocked. Each default now means "not known" and blocks where
the fact decides an amount (see
[Defaults of the public inputs](trust/confidence.md)).

| Before | After |
|---|---|
| `Employment.pension_fund=None` meant not enrolled | `None` means not known: on a CCNL with a fund (Tabacco, Tessile PMI, Vetro meccanizzato) the `pension_fund_contribution` decision is `incomplete` (`required_fact_missing`) and the run has a `missing_fact pension_fund` blocker. State `NoPensionFund()` (from `ccnl_engine.inputs`) for a worker who is not enrolled |
| `Employment.roles` defaulted to `frozenset()` | Defaults to `None`, not known: on a level with an allowance restricted to a role the allowance is left out and the run has a `missing_fact roles` blocker. Pass `frozenset()` for a worker who holds no role |
| `AbsenceEvent.suspends_accrual` defaulted to `False` | Defaults to `None`, not known: its days count as accruing, and a tredicesima or quattordicesima whose months they could change is `provisional` with a `missing_fact suspends_accrual` blocker. Pass `False` for an ordinary unpaid absence |
| `weekly_hours` without `full_time_weekly_hours` paid full time silently | Still paid full time, with a `missing_fact full_time_weekly_hours` blocker, domestic CCNLs included. Pass the full time of the contract |
| A somma esente due carried the `provisional` issue `somma_esente_income_assumed` | The 20,000 EUR limit reads the income beyond this employment from `current_year`: stated, no issue; not stated, the `incomplete` issue `somma_esente_income_unknown` and a `missing_fact current_year` blocker; with employment income of other employers, the `provisional` issue `somma_esente_band_assumed` |
| `PUBLIC_FACTS` without these facts | `"full_time_weekly_hours"`, `"pension_fund"`, `"roles"`, `"suspends_accrual"` |

## Federmeccanica sickness counted over several episodes

Metalmeccanici Federmeccanica no longer pays every sick day in full for 180
days of an episode. It follows Sez. Quarta Titolo VI Art. 2: by seniority,
122, 153 or 214 days of a treatment chain in full and the rest at 80%,
comporto of 183, 274 or 365 days over three years, chain restarted after 61
days of work, and the first three days of the fourth and later short
absences of a year at 66% and 50%. Amounts change past day 122 of a chain,
and days past the comporto are left out sooner.

| Before | After |
|---|---|
| `SicknessRules` tiers and comporto per episode only | Also `SicknessRules.cumulation` (`SicknessCumulation`, `SicknessSeniorityBand`, `ShortAbsenceReduction`); a rule sets one model |
| `SickPayRules` in `payroll.domain.sick_days` | `payroll.domain.sick_pay_rules.SickPayRules`, with `worker` (`SicknessWorker`) |
| An import listed earlier sickness without saying from when | `OpeningBalances.sickness_known_from`; left `None`, the episodes cover the tax year only and a run that could pass a threshold has a `missing_fact` blocker. `EmploymentAccrualState.sickness_known_from` carries it; `PeriodState.SCHEMA_VERSION` 12 |
| No way to state a short-absence exemption | `SicknessEpisode.short_absence_exempt` (`None`: not stated) |
| A month whose payable days differ from the divisor was deducted silently (24/26 of a February) | `provisional` issue `sickness_month_quota_mismatch` |
| An `AbsenceEvent` on a sick day was deducted twice; beside sick days over the pay it raised `InvalidInputError` | `InvalidInputError` on a sick day; issue `sickness_with_unpaid_absence` beside sick days; `OutOfScopeError` (`sickness_with_unpaid_absence`) over the pay |

## Withholding of each run under art. 23 DPR 600/1973

The IRPEF of a run before the conguaglio changes; the IRPEF of the year,
settled by the conguaglio, does not (see
[Withholding of a run](engine/fiscal.md#withholding-of-a-run)).

| Before | After |
|---|---|
| Every run withheld an even share of the projected annual IRPEF still due, plus the extra annual tax of its one-off income | A regular month withholds on its own taxable with the brackets divided by twelve, less the art. 13 deduction and the ulteriore detrazione for its days and the art. 12 deductions of its month (art. 23 c. 2 lett. a); the IRPEF withheld so far no longer changes it |
| A tredicesima or quattordicesima withheld the share of a regular month | It withholds on the monthly brackets with no deduction (lett. b); so do a `BonusEvent` of kind `bonus` or `productivity_bonus` taxed ordinarily and the PdR above its cap, apart from the pay of the month |
| A dependant from July lowered every run of the year | The art. 12 deduction counts from the month its conditions arise (art. 12 c. 3 TUIR) |
| The ulteriore detrazione was recognized on every slot, the tredicesima included | It is recognized on the regular months, for their days |
| A bonus that lifted the income above the band of the ulteriore detrazione took back what earlier runs had recognized (`recovered_by_withholding`) | No run takes it back before the conguaglio, which recovers it under L. 207/2024 art. 1 c. 7, in ten installments above 60 EUR |
| `compute_tax(..., net_without_one_off=, ulteriore_without_one_off=)` | `compute_tax(..., period=PayPeriod(...))`, from `payroll.service.period_withholding`; `child_months` is `child_due_months` and returns the months, `DependentDeduction.months` is a property of `due_months` (internal modules) |

## Art. 13 minimum proportioned in the withholding

The withholding agent proportions the minimum of the art. 13 TUIR deduction
(€690, €1,380 for a fixed term) to the days of work, as the Certificazione
Unica 2026 instructions require (punto 367); the tax return grants it
whole. With the 2026 amounts the minimum for the days never exceeds €1,955
for the days, so payroll deducts €1,955 × days / 365 again up to €15,000,
and a short employment withholds more IRPEF than before. A new `irpef`
decision records the part of the minimum left to the tax return (see
[Fiscal rules](engine/fiscal.md)).

| Before | After |
|---|---|
| Metalmeccanico C3, 10 July to 20 September 2026 (73 days), open-ended: deduction €690.00 | Deduction €391.00 (1,955 × 73 / 365); decision `minimum_proportioned_to_days`, `tax_return_balance` €299.00 |
| Same, `FixedTerm()`: deduction €1,380.00, net IRPEF €0.00, no trattamento | Deduction €391.00; gross tax above €391.00 − €15.00, so trattamento €240.00 (1,200 × 73 / 365); `tax_return_balance` €989.00 |
| `irpef` decisions of a run: one, `withheld`, `refunded` or `nothing_due` | Also `minimum_proportioned_to_days` (no amount) when the whole minimum exceeds the deduction of the withholding |

## Negative net, arrears of the year and a conguaglio without residence

| Before | After |
|---|---|
| A run whose deductions other than IRPEF and surtax exceeded its pay without unpaid absences (e.g. a large fringe benefit on a part-time salary) raised `DataIntegrityError` (`net_pay_non_negative`) | `OutOfScopeError`, reason `negative_net`, feature `net_pay`, with or without absences; the reason was `withholding_shortfall` with absences |
| `ArrearsEvent` was always taxed separately at `separate_tax_rate`; `reference_period` was not read | `reference_period` of an earlier tax year than the run: separate taxation at `separate_tax_rate` (art. 17 c. 1 lett. b TUIR); of the tax year of the run: ordinary IRPEF with the run, the rate is not used; `None`: separate taxation as before with a `missing_fact reference_period` blocker; a later year: `InvalidInputError`. Each arrears event records a `contract_renewal_arrears` decision with reason `separate_taxation`, `ordinary_taxation` or `reference_period_unknown` |
| A conguaglio of a withholding run without `regione` or `comune_belfiore` closed a state that opened the next year without a blocker | Its `closing_state.history_known` is `False`: every later run, the next tax year included, has the `missing_fact opening_state` blocker until it is recomputed with the residence |

## INPS base raised to the minimum

The INPS base was the pay of the run even below the minimum daily pay of
D.L. 463/1983 art. 7 c. 1 (EUR 58.13 a day for 2026, INPS circ. 6/2026). A
full month of a full-time worker is now contributed on at least 26 x 58.13
= EUR 1,511.38, a part-time one on the hourly minimum (EUR 8.72 for a
40-hour week) times its hours; apprentices and operai agricoli are
excluded (art. 7 c. 5). Where the bundle cannot fix the minimum and the
base is below it, the INPS decisions are `incomplete`
(`minimum_base_undetermined`) and the result is not payable.

| Before | After |
|---|---|
| `inputs["base"]` of the INPS decisions was the pay chain plus the events | It is that amount raised to the minimum; the amount before is `actual_base`, with `minimum_base`, `minimum_base_bound`, `minimum_base_reason` |
| Contributions, the TFR 0.50% IVS, the IRPEF taxable and the year-to-date INPS base read the pay | They read the raised base; the gross and the TFR quota do not change |
| No issue for a base below the minimum | Issue `inps_minimum_base_undetermined` when the minimum cannot be fixed; with `fact="category"` for an agricultural level whose category is open, so state `Employment.category` |
| `InpsRates` had no minimum | `InpsRates.minimum_base`, a `MinimumBaseRule` (`daily`, `week_days`, `monthly_days`, `hourly`, `exempt_categories`, `provenance`), from the `minimum_base` block of the INPS data files |

## Extra months at the termination on chained runs, adjustment sequence

| Before | After |
|---|---|
| `calculate_period` on the regular run of the termination month paid no ratei of the extra months due after the termination; `PayrollRun.fourteenth(2026, 11)` for a Commercio worker leaving in November was refused as already closed by June | The run that pays the termination month liquidates them, as `calculate_competence_year` does: extra-month earnings `ratei at termination: n/12` |
| A tredicesima or quattordicesima run in or after the termination month paid the ratei of its own window | Refused with `InvalidInputError` when the run of the termination month liquidates that extra month: compute that run instead |
| One adjustment run per month: a second correction was refused as already closed | `PayrollRun.adjustment(year, month, sequence=2)`, run id `"2026-12-adjustment-2"`; `PayrollRun` and `PayrollRunId` have a `sequence` field, 1 by default and above 1 only for an adjustment |
| `PayrollRunId.order_key` and `payment_key` of three items | Four: the sequence is the last |
| `PeriodState.SCHEMA_VERSION` 10 | 11: a run id carries its `sequence`; a persisted state of version 10 reads 1 for every run |
| The Commercio quattordicesima of a competence year was paid on `payment_day` of June | Paid on 1 July (CCNL Terziario art. 221, new `parameters.fourteenth_payment_day`), unless `payment_dates` names its date or the plan overrides the calendar; the run stays `2026-06-fourteenth` |

## Days of a same-year rehire

The art. 13 deduction, the ulteriore detrazione and the trattamento
integrativo count the days of every employment whose income the
withholding projects (see [Fiscal rules](engine/fiscal.md)).

| Before | After |
|---|---|
| Metalmeccanico C3 from 1 January to 31 March 2026, rehired on 1 June with the state March closed: 214 days | 90 + 214 = 304 days; a run's lett. a) minimum is €1,380 when any employment of the year is `FixedTerm`, not only the run's |
| `TaxCashState(...)` | New field `employment_spells`, a tuple of `EmploymentSpell` (`first_day`, `last_day`, `fixed_term`, exported by `ccnl_engine.inputs`) of its tax year; `PeriodState.SCHEMA_VERSION` 10 |
| `OpeningBalances(...)` | New field `employment_spells`, `()` by default: the spells of an earlier employment of the year the imported totals hold |
| `EmploymentPeriod.days_in_year(year)` | Removed: `spell_days()` counts the union of the spells of the year |
| A regular run after a termination run of its competence year: `InvalidInputError` "run ... is out of order" | `InvalidInputError` naming the termination run that ended the employment; open a rehire with `PeriodState.zero()` |

## Conditions of a dependant are facts

A dependant whose art. 12 TUIR conditions are not stated no longer takes a
deduction, and the fringe-benefit threshold follows the family composition.
Amounts are unchanged for a dependant whose conditions are all stated (see
[Family deductions](engine/fiscal.md#family-deductions-art-12-tuir)).

| Before | After |
|---|---|
| `Dependent.own_income` defaulted to `0`, `residency_eligibility` and `cohabiting` to `True`, `allocation_pct` to `100` | Each defaults to `None`, unknown: a dependant that may qualify takes no deduction, the `family_deductions` decision is `required_fact_missing` and the run has a `missing_fact` blocker naming the field. Only the conditions art. 12 reads for the relationship count: `cohabiting` for an ascendant, `allocation_pct` for a child or an ascendant |
| `Dependent.dependent_from` / `dependent_until` defaulted to `None` (open) | Required keyword arguments; `None` still states an open end |
| `Dependent(relationship=SPOUSE, allocation_pct=50)` halved the spouse deduction | Rejected: the spouse deduction of lett. a is not shared; `None` or `100` |
| `PeriodFacts.has_dependent_children` (and `PeriodCalculationRequest.has_dependent_children`) selected the 2,000 EUR fringe threshold | Removed: the threshold is 2,000 EUR when a child of `family_composition` is within the own-income limit of art. 12 c. 2 in the year. Unknown (no composition, or a child's `own_income` unknown) applies 1,000 EUR, and when the choice changes the taxable amount the decision is provisional with a `fringe_threshold_undetermined` issue |
| `PUBLIC_FACTS` without these facts | `"own_income"`, `"residency_eligibility"`, `"cohabiting"`, `"allocation_pct"` |

## Unknown residence recorded as an undetermined surtax

Amounts are unchanged.

| Before | After |
|---|---|
| A withholding run with `PeriodFacts.regione` or `comune_belfiore` left `None` took no decision on that surtax; only the `requirement_unresolved` blocker named the fact, and `assurance.calculation` could stay `final` | A `residence_unknown` decision on `addizionale_regionale` or `addizionale_comunale` (incomplete, amount `None`, `inputs["fact"]` = `facts.regione` or `facts.comune_belfiore`): `assurance.calculation` is `incomplete`, with a `calculation_issue` and a `capability_not_computed` blocker besides `requirement_unresolved` |

## TFR revaluation and Fondo Tesoreria

The December run decides the revaluation of the TFR fund at 31 December,
and every run says where the TFR goes. Amounts posted to the ledger are
unchanged.

| Before | After |
|---|---|
| No revaluation: the `tfr` decision of December was `final` | A `tfr_revaluation` decision on the December regular run and on the run that ends the employment; state `Employment.tfr_fund`, a `TfrFundBalance` (exported by `ccnl_engine.inputs`), or the run has a `missing_fact` `tfr_fund` blocker unless the employment starts in the year |
| The TFR outside a pension fund always posted to `tfr_accrual` | `Employment.tfr_treasury_fund`: `True` posts it to the new `tfr_treasury_fund` account (in the employer cost), `False` to `tfr_accrual`; `None` posts to `tfr_accrual` with a `missing_fact` `tfr_treasury_fund` blocker |
| `AccountKind` had 21 members | 22, with `TFR_TREASURY_FUND` |
| An apprentice's TFR was `provisional` with the `tfr_apprentice_additional_ivs_undetermined` issue | Final, with no deduction: the 0.50% is not due on an apprentice (INPS circ. 70/2007, note 5) |

## Opening state and other-employment bases are facts

A run opened without the history of its employment, or whose contributions
could depend on an unknown INPS base of other employments, is no longer
payable. Amounts are unchanged
(see [Opening state and imported balances](engine/opening-state.md)).

| Before | After |
|---|---|
| `PeriodState.zero()` (the default of `PeriodInput.opening_state`, or `None` in a plan) opened any run without a blocker | The zero state is the fact only for the first run of an employment whose `employment_period` starts in the run month; otherwise a `missing_fact opening_state` blocker, on every run that descends from it too |
| `PeriodState(accrual, cash)` | New field `history_known` (`True` unless the engine marks a state opened without its history); `SCHEMA_VERSION` 9 |
| `InpsBaseYtd.other_employers` defaulted to `0` | `None` is unknown: a `missing_fact other_employers` blocker when the INPS rules carry a massimale the worker may be subject to or a 1% threshold; `Decimal(0)` states none |
| `CurrentYearTaxFacts(tax_year, other_employment_income, other_income, ...)` | New required `other_employment_inps_base`, after `other_employment_income`; `employment_only()` states zero. It replaces the base the opening state carries for its competence year |
| `OpeningBalances(tax_year=..., ...)` with `inps_bases`, `recoveries`, `surtax_obligations` defaulted to `()` | The three are required keyword arguments; every competence year of `payments` and `competence_runs` needs its `InpsBaseYtd` |
| `PUBLIC_FACTS` without these facts | `"opening_state"` and `"other_employers"` |

## Validity windows and partial years

| Before | After |
|---|---|
| `ContractSummary` told nothing about the dates the bundle covers | `ContractSummary.validity`, a `ValidityWindow` (exported by `ccnl_engine.catalog`): the dates on which every rule of the CCNL has a value |
| `calculate_competence_year` and `calculate_tax_year` raised `MissingRuleError` when a run of the year had no base salary (ANAS, Igiene ambientale Utilitalia, Lavanderie industriali Assosistema and Metalmeccanico Confimi from January 2026) | The run is left out and listed in `uncovered_runs` (`UncoveredRun`, exported by `ccnl_engine.results`) with a `run_not_computed` blocker; the other runs are computed and the year is not payable. A year with no run in force still raises `MissingRuleError` |
| `BlockerCode` without a member for a run left out | `BlockerCode.RUN_NOT_COMPUTED` (`"run_not_computed"`) |

## Additional 1% IVS charged month by month and settled in December

The additional 1% IVS of D.L. 384/1992 art. 3-ter was charged only once the
year-to-date INPS base passed the annual band. It is now charged each month
on the pay of the month above the monthly threshold and settled on the year
in December, in the month the employment ends and on a termination run
(INPS circ. 6/2026 par. 5; msg. 5327/2015 par. 2.3). Amounts change: a
month above EUR 4,685 pays the 1% even early in the year, a month below it
pays none even past EUR 56,224, and December settles the difference.

| Before | After |
|---|---|
| `InpsRates.employee_additional_rate`, `employee_additional_threshold` (and the same keys in the INPS data files) | `InpsRates.employee_additional`, an `AdditionalIvsRule` with `rate`, `annual_threshold`, `monthly_threshold` and `provenance` |
| Component `addizionale_1pct` on the excess of the YTD base | `addizionale_1pct` on the excess of the month; `addizionale_1pct_conguaglio` on the settling runs, negative for a credit |
| `InpsBaseYtd(year, own, other_employers)` | Also `additional_ivs`, `other_employers_additional_ivs`, `month`, `month_base`; `plus(amount, month, additional_ivs)` |
| An imported base of other employers needed nothing else | A run settling the 1% with `other_employers > 0` needs `other_employers_additional_ivs` (from their CU, `Decimal(0)` if they withheld none); left `None` it has a `missing_fact` blocker |
| Every `employee_contributions` entry was at least zero | An entry may go down to the credit of `addizionale_1pct_conguaglio`; `EarningsYtd.inps_employee` may be negative when a December paid in the next tax year gives back more than that year withheld |

## Minimum of the art. 13 deduction

Up to €15,000 of income the art. 13 TUIR deduction is at least €690, or
€1,380 for a `FixedTerm` contract (c. 1 lett. a), and the minimum is not
proportioned to the days. Short employments now withhold less IRPEF, and the
trattamento integrativo test up to €15,000 compares the gross tax with the
deduction after the minimum.

| Before | After |
|---|---|
| Metalmeccanico C3, 10 July to 20 September 2026 (73 days), open-ended: deduction €391.00, net IRPEF €821.88 | Deduction €690.00, net IRPEF €522.88 |
| Same, `FixedTerm()`: deduction €391.00, trattamento €240.00 | Deduction €1,380.00, net IRPEF €0.00; gross tax €1,212.88 is not above €1,380 − €15, so no trattamento |
| `WorkDeductionRules` without a minimum | `WorkDeductionRules.minimum`, a `WorkDeductionMinimum` (`open_ended`, `fixed_term`, `provenance`), read from `work_deduction.minimum` of the tax rulesets |
| `net_irpef(taxable, rules, family_deductions=..., eligible_work_days=...)` | Also `fixed_term=` (required); `compute_tax(..., fixed_term=False)` and `work_income_deduction(..., fixed_term=False)` |

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
| `ccnl_engine.inputs` | `Apprentice`, `CalendarOverride`, `CalendarOverrideReason`, `ContributableHours`, `ContributionHistory`, `CurrentYearTaxFacts`, `DeferredShortfall`, `Dependent`, `DependentRelationship`, `EmployerActivity`, `EmploymentPeriod`, `EmploymentSector`, `EngineMode`, `FamilyComposition`, `FixedTerm`, `ForeignTaxPaid`, `IncomeEstimateQuality`, `InpsBaseYtd`, `NoPensionFund`, `OpeningBalances`, `PaymentId`, `PayrollRunId`, `PensionFundEnrolment`, `PeriodState`, `Permanent`, `PriorYearTaxFacts`, `RecoveryObligation`, `RecoveryPlan`, `SeniorityFact`, `SenioritySource`, `ShortfallDeferralRequest`, `SubstituteTaxRegime`, `SurtaxComponent`, `SurtaxObligation`, `WeeklyHours`, `WorkCalendar`, `WorkerCategory` |
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
