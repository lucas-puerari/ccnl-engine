# Migration guide

Changes are listed newest first. Older changes are on
[Migration guide: earlier releases](migration-earlier.md) and
[Migration guide: inputs and legacy APIs](migration-legacy.md).

## ENAM of the teachers and a level for the diplomati of the secondaria

| Before | After |
|---|---|
| `istruzione-ricerca-aran` level `DOCENTE_INFANZIA_PRIMARIA` also held the docenti diplomati of the secondaria di II grado | They have their own level `DOCENTE_DIPLOMATO_SECONDARIA` (same minimum); `DOCENTE_INFANZIA_PRIMARIA` keeps the infanzia and primaria |
| No ENAM | A permanent worker on a level of the new `CCNLParameters.enam_levels` pays 1% of 80% of the minimum (component `enam_employee`, `InpsRates.public_enam`), with the open limitation `enam_base` |

## Assicurazione Sociale Vita of public employees

| Before | After |
|---|---|
| No ASV (ex ENPDEP) contribution | New `EmployerProfile.public_life_insurance` and `CCNLMeta.public_life_insurance`: when owed, the components `life_insurance_employee` (0.027%) and `life_insurance_employer` (0.093%) on the pension base; on a CCNL of the public administrations that does not fix it, `None` gives the `missing_fact` issue `public_life_insurance_unknown` |

## Allowances left out of the TFR base

| Before | After |
|---|---|
| `Allowance.tfr_relevant` false was ignored: the TFR, the funds on the TFR base and the end-of-service base of a public employee counted the allowance (`autoferrotranvieri-internavigatori`, `poste-italiane-k700`, the two dirigenze sanitarie) | They leave it out (`MonthlyPayChain.tfr_excluded_total`); `Allowance.contribution_relevant` false, which nothing used and the INPS base ignored, is rejected |

## Reduction of the gross under the TFR of public employees

| Before | After |
|---|---|
| The 2.50% of a public employee under `tfr_inps` was the employee contribution `tfr_reduction_employee` | It is a negative earning `public_tfr_reduction` (new pay item `PublicTfrReduction`, policy `it/deduction/public_tfr_reduction`): it lowers the gross and the employer cost, which now equals that of the TFS, and stays out of the INPS and TFR bases; `tfs` on a fixed term or a member of a pension fund, and any regime outside the public administrations, raise `InvalidInputError` |

## Credit contribution of public employees

| Before | After |
|---|---|
| No credit contribution | Every run on a CCNL of the public administrations withholds 0.35% of the pension base for the Gestione unitaria delle prestazioni creditizie (component `credit_employee`, `InpsRates.public_credit`) |

## End-of-service contributions of public employees

| Before | After |
|---|---|
| A public employee paid no TFS or TFR contribution to INPS and accrued a private TFR in the company | The new `Employment.public_end_of_service` (`PublicEndOfService`: `tfs`, `tfr_inps`, `tfr_employer`) sets the ENPAS or INADEL contributions (new components `tfs_employee`, `tfs_employer`, `tfr_reduction_employee`, `tfr_employer`) and whether the run accrues the TFR; `None` on a CCNL of the public administrations gives the `missing_fact` issue `public_end_of_service_unknown` |

## INPS rates of the public administrations by pension fund

| Before | After |
|---|---|
| Every CCNL of the public administrations paid the CTPS rates (8.80% employee, 24.20% employer) | The CCNL names its fund in the new `meta.public_pension_fund`; CPDEL (funzioni locali, sanità and their dirigenze) and CPS (dirigenza medica e veterinaria) pay 8.85% and 23.80% (`InpsRates.public_funds`) |

## Seniority conversion of a worker already in service

| Before | After |
|---|---|
| `seniority_to_fund` dropped every increment from the pay | A new hire (`seniority_converted_on` `None`) converts from the hire; a worker in service states the date of the request in the new `PensionFundEnrolment.seniority_converted_on`, and the increments matured by then stay in the pay (Previambiente art. 65 lett. A) bis c. 6) |

## Seniority increments converted into Previambiente contributions

| Before | After |
|---|---|
| The option of art. 65 lett. A) bis of the CCNL Servizi Ambientali could not be stated | `PensionFundEnrolment.seniority_to_fund` (default `False`): the pay chain holds no seniority increment and the employer pays the fund the increments matured, at most 10, at the amounts of the new `EmployerFund.seniority_conversion`; a fund without one rejects the option |

## Conferring the TFR alone to a pension fund

| Before | After |
|---|---|
| `PensionFundEnrolment.employee_rate` 0 was below the minimum of every fund with one | Zero states the TFR alone: no contribution of either side, the TFR to the fund, the contractual contribution of a worker not enrolled voluntarily (Previambiente c. 12); `tfr_to_fund` must be `True`, and a public employee cannot |

## Espero and Perseo Sirio on every CCNL of the public administrations

| Before | After |
|---|---|
| No fund on the other CCNLs of the public administrations | `"PERSEO_SIRIO"` (1% + 1% of the TFR base) on `funzioni-locali-aran`, `sanita-aran` and the dirigenza areas; `"ESPERO"` on `istruzione-ricerca-aran`; both on `dirigenza-istruzione-ricerca-aran`. Their TFR conferred stays notional |

## Perseo Sirio and the notional TFR of public employees

| Before | After |
|---|---|
| No fund on `funzioni-centrali-aran` | `"PERSEO_SIRIO"` on the TFR base: employer 1%, employee at least 1% |
| A public employee's TFR conferred to a fund was posted to `pension_fund_tfr` | It stays on the account the run accrues it on: INPS accrues it notionally (`tfr_to_fund` of the decision is `notional`) |

## Previambiente on the CCNL Servizi Ambientali

| Before | After |
|---|---|
| No fund on `igiene-ambientale-utilitalia` | `"PREVIAMBIENTE"`: 2.033% employer, employee at least 1.30%, on the new `contribution_base` `conventional` stated by the new `PensionFundEnrolment.conventional_base` (`None` gives the `missing_fact` issue `pension_fund_conventional_base_unknown`); 22 EUR (30.50 EUR from 2027) more for an enrolled worker (`EmployerFund.enrolled_monthly`); contractual 5 EUR, 15 EUR not enrolled (`ContractualFundContribution.not_enrolled_monthly`), none for a fixed term not enrolled (`permanent_only`) |
| `ContractualFundContribution.part_time_proportional` `false` meant no rule | `None` (the default) means no rule; `false` now states the full amount for a part-time worker |
| `EmployerFund` without a rule for the pay of the month | `paid_month_only`: nothing on a month without pay, the open limitation `fund_paid_month` on a month paid in part |

## No ERC for an employment started after December 2020

| Before | After |
|---|---|
| `Employment.erc_amount` left `None` was a missing fact on every Byblos run and tredicesima of `grafica-editoria-aieg` | An employment whose `employment_period.started_on` is after 31 December 2020 has no ERC (it was counted on the tredicesima of December 2020): `None` counts as zero there |

## ERC paid with the tredicesima of the CCNL grafici editoriali

| Before | After |
|---|---|
| The Elemento di Raccordo Contrattuale was not paid | The run that pays or liquidates the tredicesima of `grafica-editoria-aieg` pays `Employment.erc_amount` x its months / 12 as the new pay item `raccordo_element_earning` (policy `it/earning/raccordo_element`: IRPEF and INPS, no TFR); `None` gives that run the `missing_fact` issue `erc_unknown`; new `CCNLParameters.raccordo_element` |

## Byblos on the CCNL grafici editoriali and the ERC

| Before | After |
|---|---|
| No fund on `grafica-editoria-aieg` | `"BYBLOS"` on the TFR base: employer 1.9%, 1.4% for a holder of the ERC; employee at least 1% |
| No input for the Elemento di Raccordo Contrattuale | `Employment.erc_amount` (annual ERC, zero for none); `None` gives an enrolled Byblos run the `missing_fact` issue `pension_fund_erc_unknown`; new `EmployerFund.erc_holder_rate` |

## Byblos on the CCNL Esercizi cinematografici, on twelve monthly payments

| Before | After |
|---|---|
| No fund on `esercizi-cinematografici-anec` | `"BYBLOS"` on the TFR base: employer 1%, employee at least 1%, on the twelve monthly payments; new `EmployerFund.extra_months` (default `true`), false when an extra-month run owes no contribution |

## Byblos on the CCNL carta e cartotecnica

| Before | After |
|---|---|
| No fund on `carta-cartone-assocarta` | `"BYBLOS"` on the TFR base: employer 1.5%, 1.7% from January 2027; employee at least 1% |

## Level III minimum of the building PMI from March 2027

| Before | After |
|---|---|
| Level 3 of `edilizia-pmi-confapi-aniem` from 1 March 2027: 1551.88 | 1511.88, the nuovo minimo of Allegati A and B of the CCNL armonizzato 15/04/2025 |

## Fondapi on the building PMI

| Before | After |
|---|---|
| No fund on `edilizia-pmi-confapi-aniem` | Fondapi: 10 EUR x parametro / 100 a month for every worker (10.00 to 20.00 on levels 1 to 7), and 1.10% employer and at least 1.10% employee on the TFR base for an enrolled one, with the open limitation `contractual_fund_partial` for a partial month and part time |

## Fondapi on the chemical PMI with employer rate tiers

| Before | After |
|---|---|
| No fund on `chimica-affini-pmi-unionchimica` | `"FONDAPI"` on the TFR base: employer 1.66%, 2.00% from an employee rate of 1.60%, employee at least 1.06%; new `EmployerFund.employer_rate_tiers` (`EmployerRateTier`: `employee_from`, `rate`) |

## Fondapi on the minimum of the textile and metalworking PMI

| Before | After |
|---|---|
| No fund on `metalmeccanico-confapi` and `tessile-pmi-uniontessile` | `"FONDAPI"` on the contractual minimum (2.00% employer; employee at least 1.20% or 1.60%; a higher metalworking rate on the TFR base), with the open limitation `fondapi_base_elements` for the EDR and the other elements the bundle pay lacks |

## Prevedi contractual contribution of the operai

| Before | After |
|---|---|
| An operaio of the building CCNLs had the issue `contractual_fund_not_computed` | New `PeriodFacts.ordinary_hours_worked`: the hourly Prevedi amount of the level times the hours, rounded to the euro; `None` gives the missing fact `ordinary_hours_worked`. `ContractualFundContribution.hourly_by_level`, `hourly_categories`, `apprentice_hourly` |

## Cometa on the contractual minimum

| Before | After |
|---|---|
| No fund on `metalmeccanico-federmeccanica`; a fund base was the INPS or the TFR base | `"COMETA"` (2%, 2.2% for a young member, employee at least 1.2%) on the new base `FundContributionBase.CONTRACTUAL_MINIMUM`; `EmployerFund.employee_base_above_minimum` and `young_member_rate`; `PensionFundEnrolment.young_member` (`None`: missing fact on a fund with a young member rate) |
| `EmployerFund`, `FundContributionBase` in `contract.domain.compensation` | In `contract.domain.fund_contribution` |

## Prevedi contractual contribution of the impiegati

| Before | After |
|---|---|
| `ContractualFundContribution` had an amount per level only | New fields `categories`, `apprentice_monthly`, `minimum_days_in_month`, `extra_months`, `part_time_proportional`, `minimum_fixed_term_months` |
| No contractual contribution on `edilizia-ance` and `edilizia-artigianato-cna` | Prevedi for the impiegati and quadri (CNCE vademecum rules); an operaio has the incomplete issue `contractual_fund_not_computed`, an open category `contractual_fund_category_unknown` |

## Contractual fund contribution owed for every worker

| Before | After |
|---|---|
| A fund contribution was posted only for a worker enrolled in it | New `CCNLParameters.contractual_fund_contribution` (fund code and an amount a month per level): owed whatever `Employment.pension_fund` states, posted to `pension_fund_employer` with its solidarity; decision reason `contractual_only` for a worker not enrolled, input `contractual` otherwise. `PensionContribution.terms` is `None` for a contractual contribution alone |
| No fund on `materiali-costruzione-lapidei-confapi` | Fondapi: 5 EUR x parametro / 100 a month for every worker, and 2.40% employer and at least 1.40% employee on the TFR base for an enrolled one |

## Prevedi on the building CCNLs

| Before | After |
|---|---|
| No fund on `edilizia-ance` and `edilizia-artigianato-cna`: an enrolment raised `InvalidInputError` | `"PREVEDI"`: employer 1% and employee at least 1% of the TFR base (Scheda 'I destinatari e i contributi', option A); the contributo contrattuale owed for every worker is a separate change |

## Days without pay leave the days of the deductions

| Before | After |
|---|---|
| An unpaid absence never changed the days of the art. 13 deductions, the ulteriore detrazione and the trattamento integrativo | New `AbsenceEvent.no_pay_due`: `True` (aspettativa senza assegni) removes its days (AdE circ. 15/E/2007 par. 1.5.1), `False` (a strike) keeps them, `None` keeps them with a `missing_fact` blocker `no_pay_due` on a withholding run |
| `EmploymentSpell(first_day, last_day, fixed_term)` | New field `unpaid_days`, kept across the runs of the tax year; `PeriodState.SCHEMA_VERSION` 13 |

## Hourly pay of a flat-pay regime

| Before | After |
|---|---|
| The reduced-hours conviventi divided their flat monthly pay by 130 hours (the 30-hour ceiling) whatever the hours: the INPS hourly bracket of a worker at 10 hours was the first (5.67 EUR) | The divisor of a run is `weekly_hours` x 52 / 12 on a CCNL with `flat_pay_max_weekly_hours`: 737.39 / 43.33 = 17.02 EUR, the third bracket |

## Ulteriore detrazione on the reddito complessivo

| Before | After |
|---|---|
| The ulteriore detrazione of L. 207/2024 art. 1 c. 6 read the employment income of this employer only | It reads the reddito complessivo: this employment plus the income `current_year` states beyond it, the exempt share of c. 9 included; without `current_year` while it is due, issue `ulteriore_income_unknown`. Exempt regime income also makes the somma esente band provisional (`somma_esente_band_assumed`) |

## Somma esente on the income of each run

| Before | After |
|---|---|
| Before the conguaglio a run paid the annual somma esente still due divided by the slots left | A run pays the percentage of the projected annual income times the taxable it pays (AdE circ. 4/E/2025 par. 1.2), capped at what is still due; new component `somma_esente_period` and decision input `period_share`. Equal amounts for a constant pay, different for a hire in the year, a tredicesima or a bonus |

## Reduced-hours conviventi of the CCNL lavoro domestico

| Before | After |
|---|---|
| A convivente under art. 14 c. 2 (levels B, B super, C, up to 30 weekly hours) had no file: the convivente file scaled Tabella A to the hours | New CCNL file `lavoro-domestico-convivente-orario-ridotto` with Tabella B, paid in full whatever the hours up to 30 (`CCNLParameters.flat_pay_max_weekly_hours`); more hours raise `InvalidInputError` |
| A convivente with fewer than 54 agreed hours under art. 14 c. 1 was paid the linear share of Tabella A, payable | Same amount, with the open limitation `lavoro-domestico-convivente/part_time_scaling`: not payable until a source gives the rule |
| `list_contracts()` followed the file names | Sorted by `ccnl_id`, as documented |

## Exempt income of the impatriati and researcher regimes in the somma esente

| Before | After |
|---|---|
| `CurrentYearTaxFacts` had no place for the exempt share of the impatriati and researcher regimes, which L. 207/2024 art. 1 c. 9 counts in the reddito complessivo of the somma esente | New required field `CurrentYearTaxFacts.exempt_regime_income` (`>= 0`; `employment_only` states zero), added to the reddito complessivo of the somma esente only (`somma_esente_income`), not to that of the family deductions |

## Fonchim on the TFR base, with its insurance contribution

| Before | After |
|---|---|
| FONCHIM on vetro: employer 1.50% (2.00% from 2027) of the INPS base, no employee minimum | 1.75% (2.25% from 2027) of the TFR base, the 0.25% insurance contribution included, and an employee minimum of 1.50%: an enrolment at 1.2% now raises `InvalidInputError` |
| No fund on `chimica-farmaceutica-federchimica` | `"FONCHIM"`: employer 2.35% (2.10% + 0.25%), employee at least 1.20%, on the TFR base |

## Fondapi on the food PMI, not on the textile PMI

| Before | After |
|---|---|
| `"FONDAPI"` on `tessile-pmi-uniontessile` at 1.90% then 2.00% of the INPS base | Removed: Fondapi computes it on minimo tabellare + EDR, a base the engine does not compute, so an enrolment raises `InvalidInputError` |
| No fund on `alimentari-pmi-unionalimentari` | `"FONDAPI"`: employer 1.20%, employee at least 1.00%, on the TFR base |

## Alifond on the TFR base and on the food industry

| Before | After |
|---|---|
| ALIFOND on Tabacco computed on the INPS base, so a bonus or overtime raised the contributions; no fund on Alimentari Federalimentare | ALIFOND computes on the TFR base, as note (1) of its Scheda 'I destinatari e i contributi' states; `"ALIFOND"` (employer 1.50%, employee at least 1%) on `alimentari-federalimentare` |

## Fon.Te. employer rates of tourism and apprentices

| Before | After |
|---|---|
| Fon.Te. charged the employer 1.55% on every CCNL that has it | 0.55% on Turismo (Confcommercio, Federalberghi), Pubblici esercizi FIPE and Agenzie di viaggio FIAVET, and 1.05% for apprentices of Commercio, as Allegato 1 of the Fon.Te. nota informativa sets; new `EmployerFund.apprentice_rate` |

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
