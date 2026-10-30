# Limitation reconciliation

Review of 2026-10-30. Every weak payable rule and every open limitation of
the bundle was linked to a census row and to the work item that closes it
(`scripts/census/generate.py`, see [Model completeness](completeness.md)).
Each of the 437 open limitations the CCNL files declared that day was then
checked against the current code and data. A note is **valid** when it
still describes what the engine does, a **duplicate** when another open
limitation of the same CCNL tracks the same gap, and **superseded** when
the code or the data now handles it. The review judged only whether a
note is still true of the engine, not the contract reading behind it.

| Capability | Notes | Valid | Duplicate | Superseded |
|---|---:|---:|---:|---:|
| `base_salary` | 147 | 147 | 0 | 0 |
| `seniority` | 105 | 104 | 1 | 0 |
| `inps_employer`, `inps_employee` | 55 | 50 | 2 | 3 |
| other capabilities | 130 | 129 | 1 | 0 |
| **Total** | **437** | **430** | **4** | **3** |

## Closed

Each closed note keeps its text; its limitation is `resolved` and its
`remediation` states why, with the evidence. The bundle had 444 open
limitations before the review (437 of the CCNLs, 7 of the engine) and 437
after it (430 of the CCNLs, 7 of the engine).

| Limitation | Outcome |
|---|---|
| `assicurazioni-ania/inps_credit_rate_unverified` | Duplicate of `assicurazioni-ania/inps_sector_rates_unsourced` |
| `bancari-abi/inps_credit_rate_unverified` | Duplicate of `bancari-abi/inps_sector_rates_unsourced` |
| `ceramica-industria-confindustria/apprentice_seniority_amount` | Duplicate of `ceramica-industria-confindustria/apprentice_seniority` |
| `lavoro-domestico-non-convivente/domestic_oncological_comporto` | Duplicate of `lavoro-domestico-non-convivente/oncological_comporto` |
| `forze-polizia-ordinamento-civile/ctps_rates_proxy` | Superseded: the CTPS rates are verified on the INPS page of the public employees' contributions |
| `legno-lapidei-artigianato-confartigianato/null_category_operaio_rate` | Superseded: the category the employment declares selects the rate, and an undeclared one is flagged on the run |
| `operai-agricoli-florovivaisti/mountain_zone_reductions` | Superseded: `EmployerProfile.agricultural_zone` applies the zone cuts of INPS circ. 43/2026 |

Kept open although a reviewer proposed to close them:

- `tessile-moda-artigianato-confartigianato/level_category_unconfirmed`:
  the run is now flagged when no category is declared, but the levels of
  the file still have no category, the gap the note tracks.
- `terziario-confesercenti/sunday_overtime`: Sunday overtime declared as
  rest-day overtime takes the 30% band (test `terziario_sunday_30`); the
  note is narrowed to the worker whose weekly rest falls on another day,
  whose Sunday overtime takes 15% while Art. 149 may pay 30%.

## Valid with stale wording (T09.04)

These notes still hold, but part of their text described an engine that has
changed since. Their text and remediation were rewritten on 2026-10-30
(work item T09.04), each marked "review of 2026-10-30"; the limitation ids
and their status are unchanged.

| Limitation | What is out of date |
|---|---|
| `cooperative-consorzi-agricoli/operai_seniority_over_five` | Per-category seniority tables now exist; the gap is data only |
| `telecomunicazioni-asstel/industria_tax_sector_unverified` | Quotes superseded industria rates |
| `vigilanza-privata-assiv/terziario_tax_sector_unverified` | Quotes superseded terziario rates |
| `lavoro-domestico-convivente/hourly_inps_bracket_unvalidated`, `lavoro-domestico-convivente-orario-ridotto/hourly_inps_bracket_unvalidated` | Reads as a description of the current engine; the validation is still due |
| `metalmeccanico-confapi/ordinary_hours_premiums` | The holiday and compensatory-rest premiums are now modelled |
| `metalmeccanico-confapi/sickness_rules` | The net-pay gross-up is now modelled |
| `chimica-farmaceutica-federchimica/ordinary_hours_premiums` | The holiday and day-shift premiums are now modelled |
| `chimica-farmaceutica-federchimica/overtime_base_and_categories` | Bands by level and superminimi in the hourly base are now modelled |
| `impianti-sportivi-sport/integration_75_days_4_20` | Sickness rules can now hold day bands |
| `impianti-sportivi-sport/pre_2015_superminimo_missing`, `impianti-sportivi-sport/pre_2015_fourteenth_missing` | Allowances can now depend on the date in service |
| `sanita-privata-aiop-aris/part_time_supplementary_rate`, `studi-professionali-confprofessioni/part_time_supplementary` | Supplementary hours are now an overtime kind |
| `terziario-confesercenti/sickness_net_basis`, `dmo-federdistribuzione/sickness_net_basis` | Exempt events are now an input of the episode |
| `lavoro-domestico-*/oncological_comporto` | Serious illness is now an input of the episode |
| `acconciatura-estetica-confartigianato/gruppo_1_reduced_duration` | The data already shortens the track; the note and the data disagree |
| `cemento-calce-gesso-industria/apprenticeship_full_pay_passthrough` | Under-classification is now relative to the destination level |
| `agenti-immobiliari-fiaip/quadri_function_allowance` | Role and months per year are now allowance fields |
| `turismo-federalberghi/extra_months_during_leave` | The caller can suspend the accrual; the CCNL rule is still not applied |
| `trasporto-ferroviario-agens/pre_june_2025_tables` | A run before the first table now fails instead of reading the nearest one |

Pairs kept apart, worth a reading of the text: the renewal tranches and
the annual ISTAT update of the domestic minimi
(`tranches_from_2027` and `annual_minimi_not_updated`), and the two
pre-2015 personal elements of `impianti-sportivi-sport`.

## Simplifications without a limitation

The same day, the 66 `simplification` notes that declared no limitation and
the 8 `missing` notes were checked: a simplification that can change an
amount and is not tracked hides a gap from the completeness report.

| Verdict | Notes | Outcome |
|---|---:|---|
| No amount: the engine refuses the case (no track, no table before the first date, no band) or the note changes nothing computed | 58 | Kept as they are |
| Untracked gap | 12 | Now open limitations, with their capability, impact, trigger and remediation |
| Obsolete | 3 | Rewritten: `ortofrutticoli-agrumari` (salary tables now verified) and `pulizia-artigianato-confartigianato` (an ambiguous track is now refused) became `info` notes; `agenzie-viaggio-fiavet` says which work rules now exist |
| Duplicate | 1 | Removed: `ortofrutticoli-agrumari` restated the assumed sickness integration that `assumed_sickness_integration_rates` tracks |

The new limitations: `assicurazioni-ania/funzionari_economic_allowance`,
`autorimesse-ic35/meal_voucher`, `autorimesse-ic35/long_week_divisors`,
`ced-assoced/conditional_allowances_title_xxiii`,
`concia-unic/rol_not_accrued`,
`dirigenza-sanitaria-medico-veterinaria-aran/approximate_hourly_divisor`,
`impianti-sportivi-sport/long_week_divisor_195`,
`istruzione-ricerca-aran/teacher_hourly_divisor`,
`panificazione-artigianato-confartigianato/special_allowance_in_base`,
`panificazione-artigianato-confartigianato/err_unsourced`,
`radiotelevisive-radiofonico/inps_rates_reused_unverified` and
`radiotelevisive-televisivo/inps_rates_reused_unverified`. The open
limitations of the bundle go from 437 to 449: the gaps were there, now they
are counted.
