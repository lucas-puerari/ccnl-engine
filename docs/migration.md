# Migration guide

Changes are listed newest first. Older changes are on
[Migration guide: earlier releases](migration-earlier.md) and
[Migration guide: inputs and legacy APIs](migration-legacy.md).

## Scripts and demo laid out by operational domain

| Before | After |
|---|---|
| `scripts/ci/`, `scripts/data/`, `scripts/docs/`, `scripts/packaging/` packages | `scripts/{structure,provenance,knowledge,documentation,quality,distribution}/`, namespace directories without `__init__.py`. For example `scripts/structure/check.py` (was `scripts/ci/check_structure.py`), `scripts/provenance/check.py` (`check_provenance.py`), `scripts/knowledge/manifest.py` (`build_manifest.py`), `scripts/knowledge/update.py` (`rehash_ccnl.py`), `scripts/documentation/generate_contract_pages.py` (`gen_contract_pages.py`), `scripts/quality/smoke_test.py` (`smoke_wheel.py`), `scripts/distribution/build.py` (the hatch build hook). The Makefile, the workflows and the docs call the new paths |
| Baselines `scripts/ci/structure_baseline.json`, `scripts/ci/provenance_baseline.json`, `scripts/ci/layout_inventory*.json` | `scripts/structure/baseline.json`, `scripts/provenance/baseline.json`, `scripts/structure/inventory.json` and `inventory_rules.json` |
| Demo translations in `demo/i18n/` | `demo/localization/`; the built demo still serves them under `i18n/` |

## Payroll laid out by domain

| Before | After |
|---|---|
| `payroll` organised by layer (`domain`, `service`, `application` with `handlers`, `period`, `year`, `withholding`, `amounts`, `invariants`) | Organised in sixteen subdomains with role-named files: `payroll/{accrual,amount,assurance,capability,contribution,employment,event,family,ledger,period,sickness,state,taxation,termination,withholding,year}/`, for example `payroll/period/services.py` (`calculate_period`), `payroll/state/serializers.py` (the state codec), `payroll/taxation/rules_irpef.py`. Moves are one to one; the public namespaces (`ccnl_engine`, `inputs`, `events`, `results`, `catalog`) keep every name |
| Code importing internal payroll paths (`ccnl_engine.payroll.domain...`, `ccnl_engine.payroll.service...`, `ccnl_engine.payroll.application...`) | Internal paths are not public API and have no shim: import from the public namespaces, or from the new module the inventory `scripts/structure/inventory.json` names |

## Domains outside payroll laid out by domain

| Before | After |
|---|---|
| `contract`, `tax`, `knowledge`, `provenance`, `diff`, `shared` and `api` organised by layer (`domain`, `service`, `application`) | Organised by domain, with role-named files: `contract/<subdomain>/models.py`, `tax/<subdomain>/loaders.py`, `comparison/ruleset/services.py`, `provenance/{ruleset,source}/models.py`, the shared `errors.py`, `primitives.py` and `validation.py` at the root, the facade in `api.py`. Moves are one to one; the public namespaces (`ccnl_engine`, `inputs`, `events`, `results`, `catalog`) keep every name |
| `from ccnl_engine.knowledge import __version__` | `from ccnl_engine import bundle_version`; the value also lives in `ccnl_engine.knowledge.facade.__version__`. `ccnl_engine.knowledge` is now a package marker |
| Code importing internal paths (`ccnl_engine.contract.domain...`, `ccnl_engine.tax.service...`, `ccnl_engine.shared.domain...`) | Internal paths are not public API and have no shim: import from the public namespaces, or from the new module the inventory `scripts/structure/inventory.json` names |

## Knowledge bundle by dataset, with a manifest

| Before | After |
|---|---|
| JSON resources under seven `knowledge/<x>/data/` packages (`ccnl`, `tax`, `inps`, `surtax`, `capabilities`, `limitations`, `policies`), found by globbing each directory | One tree `knowledge/<domain>/<dataset>/<year>/<scope>.json` (`contract/agreement/<slug>.json`, `taxation/annual/<year>/<sector>.json`, `social_security/contribution/<year>/<sector>.json`, `surtax/regional/<year>.json`, ...), indexed by `knowledge/manifest.json`. The 174 files are moved one to one, content unchanged |
| A loader read any file present in its package directory | `ccnl_engine.knowledge.loaders_manifest`: a loader reads only a path the manifest lists (`read_resource`, `resources`); the wheel carries every listed resource as `<path>.gz`. `scripts/knowledge/manifest.py --check` fails CI when the manifest drifts |
| Code reading `importlib.resources.files("ccnl_engine.knowledge.ccnl.data")` | Those packages no longer exist; read `ccnl_engine.knowledge.loaders_manifest.read_resource("contract/agreement/<slug>.json")` or use the public loaders |

## Carenza by event and yearly comporto

| Before | After |
|---|---|
| A per-episode sickness rule counted its comporto on one episode and paid the same carenza to every event | New `SicknessRules.comporto_calendar_year` (the comporto sums the sick days of the calendar year) and `carenza_by_event` (`CarenzaByEvent`: lower carenza from the n-th event of the year); `SicknessEpisode.short_absence_exempt` also marks the events a CCNL leaves out of that count |
| Commercio: 180-day comporto per episode, carenza always at 100% | Art. 186: 180 days in the calendar year; Art. 187: carenza at 100% for the first two events of the year, 66% for the third, 50% for the fourth, none from the fifth. An unstated exemption pays the higher carenza with a `sickness_short_absence_exemption_unknown` issue; a history known after 1 January raises `sickness_history_unknown`. The net daily pay remains an open limitation |

## Day-gated sick pay, Commercio reviewed

| Before | After |
|---|---|
| A sickness rule could gate its integration rate by month of sickness only | New `SicknessRules.day_bands` (`SicknessDayBand`: `day_from`, `day_until`, `integration_rate`), applied by the day of the episode before any month tier |
| Commercio sickness paid 100% from day 4 (`assumed`) | Art. 187: 100% carenza, 75% for days 4-20, 100% from day 21, `derived`; the net daily pay, the carenza by event of the calendar year and the yearly comporto stay an open limitation, so a run with sickness is still not payable. Commercio becomes `reviewed` |

## Sourced 2026 INPS rates of edilizia, credito and apprentices

| Before | After |
|---|---|
| Edilizia employer: 28.46% up to 15 employees, 29.06% up to 50, 29.50% above, one rate for every category | Operai 33.68% / 34.28% / 34.28% (CIGO edile 4.70%, malattia 2.22%), impiegati and quadri 28.46% / 29.06% / 29.36%, dirigenti 26.96% (Assimpredil ANCE tables 1/2026 and 2/2026). A level with no category takes the operai rate with an `employer_rate_category_assumed` blocker: declare `Employment.category` |
| Credito employer: 26.76% for every category | Operai 29.31% (malattia 2.55%); impiegati, quadri and dirigenti 26.76% |
| Apprentices of every sector: employer 11.61% (3.11% / 4.61% in the first two years up to nine employees), worker 5.84%, at every headcount | New `headcount_shares` of the apprentice block: the CIGO, CIGS or FIS share by headcount, added to every employer period and to the worker rate (INPS circ. 76/2022). Industria 13.31% up to 15 (4.81% / 6.31% up to nine), 13.91% up to 50, 14.21% above, worker 6.14% above 15; terziario 11.94% up to 5, 12.14% up to 15, 12.74% above, worker 6.01% / 6.11% / 6.41%; edilizia 16.31% up to 15 (7.81% / 9.31% up to nine), 16.91% above, worker 6.14% above 15. Agricoltura, artigianato and credito unchanged |

## Signed sources for Commercio and Metalmeccanico

| Before | After |
|---|---|
| Commercio paid the terzo elemento nazionale (2.07) to every level | Paid only where no provincial third element is in force (Art. 215): new `EmployerProfile.provincial_pay_element`. `False` pays it, `True` leaves it out, `None` leaves it out with a `missing_fact provincial_pay_element` blocker. State it on every Commercio employer |
| Commercio minimi, contingenza, terzo elemento, function allowances, extra months, accrual rule and overtime bands `assumed` from aggregators | `derived` from the signed accordo integrativo of 28/03/2024 and the Testo Unico 2019, each with page, quote and sha256. The level VII "Altri el." allowance is coded `ALTRI_ELEMENTI` instead of `IND_FUNZIONE` |
| Commercio sickness paid 100% from day 4, labelled `derived` | `assumed`, with an open limitation: Art. 187 integrates to 75% of the net daily pay for days 4-20 and reduces the carenza by event; a run with sickness is not payable until the rule is modelled |
| Metalmeccanico minimi stopped at the June 2026 tranche | Tranches of 1 June 2027 and 2028 from the agreement of 22/11/2025 (minimums the June IPCA check can raise); minimi, overtime bands, extra months, accrual rule, seniority, divisor and daily quota cited to the signed texts; readiness `reviewed` |
| Metalmeccanico leave: 25 days from 36 months | Art. 10: 20 days, 21 over 10 years of service, 25 over 18 |
| Metalmeccanico overtime without the 2025 exempt-quota supplement | Open limitation `overtime_exempt_quota_supplement`: a run with overtime is not payable |

## Concia UNIC reviewed, quota of 1/25

| Before | After |
|---|---|
| Concia UNIC computed partly employed months and sick days on a quota of 1/26, though the CCNL states 1/25 | New `DailyDivisorMethod.BY_25`: the quota is 1/25 of the monthly pay, and since the CCNL does not say which days of a month are payable, a partly employed month and the sick days of a month are not computed (`sickness_daily_quota_missing`, partial month not payable) |
| Concia UNIC `exploratory`, its accrual rule missing | `reviewed` with `confidence` `verified`: every minimum and IPO checked against Allegato n. 1 of the signed rinnovo, the accrual rule and the values the rinnovo does not hold (EDR, function allowance, divisors, tredicesima, sickness, seniority) cited to the page of the MySolution summary that holds them. `operational` mode still blocks it with `ruleset_not_production` |
| The Concia sickness limitation applied from 60 months of seniority | From 36 months, where the CCNL's second seniority tier starts |

## Incremental assurance of a resumed year

| Before | After |
|---|---|
| The assurance of a `CompetenceYearResult` or `TaxYearResult` combined the runs it computed, without saying so; with no run computed (a plan retried on its closing state) `is_payable`, `blockers` and `assurance` raised `ValueError` | The assurance is documented as incremental: it covers `assessed_payments`, the payments computed by the call, and not those the opening state already closed. With no run computed it is not payable (`missing` evidence, a `rule_source_weak` blocker, in `operational` mode also `ruleset_not_production`) |
| `PaymentsResult` without the mode of its runs | New field `mode`, the `EngineMode` the payments were computed under |

## Strict INPS sick-pay table

| Before | After |
|---|---|
| `InpsSickPayRates` and its loader defaulted `carenza_days` to 3, `annual_max_days` to 180, `bands` and `coverage` to empty | All four are required (`bands` and `coverage` with at least one entry); a sick-pay file missing one, or with a value the model rejects, raises `DataIntegrityError` naming the file. A custom `KnowledgeRepository` building `InpsSickPayRates` must state every field |

## Conflicting rulesets in a year

| Before | After |
|---|---|
| A year listed each ruleset `id@version` once, keeping the first run's content even when a later run read a different hash, kind, readiness or confidence | Rulesets are listed once per distinct content; an `id@version` read with two contents adds a `ruleset_conflict` blocker (`BlockerCode.RULESET_CONFLICT`, detail `id@version`) and the year is not payable |

## Persisted state bound to the engine and bundle

| Before | After |
|---|---|
| `period_state_to_json` wrote the schema version only; a state written by another engine or knowledge bundle of the same schema was read | The JSON also carries `engine_version` and `bundle_version`; `period_state_from_json` rejects a state of another engine or bundle with `InvalidInputError`: recompute the runs or import the totals with `OpeningBalances` |
| Types were tagged with their module path and resolved by import | Types are tagged with their class name from the registry `STATE_TYPES`; `PeriodState.SCHEMA_VERSION` 14, a state of version 13 is not read |
| A malformed tagged value could raise `KeyError` or `TypeError` | Every malformed payload raises `InvalidInputError` |

## INPS base to the whole euro

| Before | After |
|---|---|
| The INPS base of a run was the pay to the cent | Private sectors round it to the whole euro, half up (INPS circ. 208/2001), as the payslips print it, and charge each share on it; the Gestione Dipendenti Pubblici keeps the cents (`InpsRates.base_whole_euro`, false in the public administration file). The year-to-date base, the massimale, the minimale and the additional 1% read the rounded base |

## Industria INPS rates by category

| Before | After |
|---|---|
| Industria employer: 30.13% up to 15 employees, 30.20% up to 50, 30.50% above, one rate for every category, with a FIS share and the gross CUAF | Operai 30.68% / 31.28% / 31.58%, impiegati and quadri 28.46% / 29.06% / 29.36% (IVS, NASpI, CUAF 0.68%, CIGO 1.70% or 2.00%, CIGS above 15, Fondo Garanzia TFR, maternita, malattia of the operai); no FIS (the industria is within the CIGO) |
| A level with no category took the single rate | It takes the operai rate with an `employer_rate_category_assumed` blocker: declare `Employment.category` (Metalmeccanico Federmeccanica levels fix none) |

## FIS and CIGS in the terziario INPS rates

| Before | After |
|---|---|
| Terziario: two tiers, 9.19% / 28.98% up to 50 employees and 9.49% / 29.58% above, no FIS share | Three tiers from INPS circ. 117/2022 all. 1 and D.Lgs. 148/2015: up to 5 employees 9.36% / 29.31%, 6 to 15 9.46% / 29.51%, above 15 9.76% / 30.11% (FIS at every size, CIGS above 15) |
| No FIS cut | New `EmployerProfile.fis_reduction`: an employer of up to five that has not applied for the assegno for 24 months pays the FIS cut by 40% (art. 29 c. 8-bis), 9.29% / 29.18%; unknown, the full rate and a `missing_fact fis_reduction` blocker |
| The massimale shared the record of the rates | `InpsRates.ceiling_provenance` backs it on its own (INPS circ. 6/2026) |

## Provisional 2027 tax, INPS and surtax tables

| Before | After |
|---|---|
| `supported_tax_years()` was `(2026,)`; a payment of tax year 2027 (a December 2026 paid after 12 January included) raised `UnsupportedTaxYearError` | `(2026, 2027)`: the 2027 tables carry the 2026 values over, flagged `RulesetIdentity.provisional`; a run that reads them is computed and not payable, with the open limitation `provisional_ruleset` (tax) or `provisional_inps_ruleset` (INPS). A payment of 2028 still raises `UnsupportedTaxYearError` |
| `tax/data/variable-pay-rules.json` | `tax/data/variable-pay-rules-<year>.json`, one file per year; `load_variable_pay_rules` of a year without a file raises `UnsupportedTaxYearError` |

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
