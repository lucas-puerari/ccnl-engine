# Migration guide: earlier releases

Continues the [Migration guide](migration.md); the oldest changes are on
[Migration guide: inputs and legacy APIs](migration-legacy.md).

## Accrual threshold and overtime multiplier from the CCNL data

`OvertimeEvent.multiplier` no longer defaults to `1.25`. Without it the
multiplier is `1 + band` of the CCNL overtime band matching the new
`OvertimeEvent.kind`; a CCNL without such a band rejects the run. The
extra-month ratei count a partly worked month with the CCNL clause when the
bundle has the signed text, and with the engine default (at least 15 days)
otherwise. See [Work rules](engine/work-rules.md#overtime-multiplier) and
[Employment period](engine/index.md#employment-period).

| Change | What to do |
|---|---|
| `OvertimeEvent.multiplier` defaults to `None` instead of `1.25`: the CCNL band gives it | Pass `multiplier=Decimal("1.25")` to keep the old amounts; without it the amount changes wherever the CCNL first-tier band is not 25% (commercio OT_DIURNO 15%: 10 h x 15.00 EUR pays 172.50 instead of 187.50); 81 of the 125 bundled CCNLs have a weekday band other than 25% and 17 have none |
| `OvertimeEvent.kind` (`OvertimeKind`: `WEEKDAY`, `NIGHT`, `HOLIDAY`, `NIGHT_HOLIDAY`, default `WEEKDAY`) added after `multiplier` | Set it for night and holiday overtime so the matching band is used |
| An event without a multiplier on a CCNL with no first-tier percentage band of its kind raises `InvalidInputError` (feature `overtime`) | Pass an explicit multiplier |
| An explicit multiplier matching no CCNL band of its kind makes the run `provisional` with issue `caller_multiplier_differs_from_ccnl` | Check the value, or accept the provisional status: the caller's value is still applied |
| A derived multiplier on a CCNL with higher tiers beyond an hour threshold makes the run `provisional` with issue `overtime_tier_not_applied` | Pass an explicit multiplier for the hours beyond the threshold |
| Overtime decision `ccnl_overtime_band_applied` (origin `engine`); the caller-supplied overtime decision lists `hourly_rate` only when the multiplier was derived | Handle the new reason code where reason codes are matched |
| `CCNLParameters.accrual_rule` (`ExtraMonthAccrualRule`: `min_days`, `comparison` `at_least` or `more_than`, `provenance`) added | Nothing: read by the engine |
| `MonthAccrualRule.comparison`, `rule` and `provenance` added; `ExtraMonthAccrual.partial_months` added | A caller building its own rule can pass `comparison=AccrualComparison.MORE_THAN` |
| `base_salary` decision `extra_month_ratei_counted` per rateo an extra-month or termination run pays | Handle the new reason code where reason codes are matched |
| The engine-default threshold is a payable rule with status `missing`: a run whose rateo includes a partly accrued month on a CCNL without the clause adds `rule_source_missing` and is `incomplete` | Treat such ratei as unconfirmed until the CCNL clause is in the bundle; whole months are not affected |
| Payable rules add `accrual_rule` for every CCNL and the first-tier overtime bands (capability `overtime`) | Custom provenance reports read the new paths |
| Metalmeccanico Federmeccanica bands corrected to the signed text (sez. quarta, titolo III, art. 7): `OT_DIURNO` 25% (was 15%), new `OT_DIURNO_EXTRA` 30% beyond two hours a day, `OT_NOTTURNO` 50% (was 20%), `OT_FESTIVO` 55% (was 30%), new `OT_NOTTURNO_FESTIVO` 75%; commercio `OT_NOTTURNO` 50% (was 30%, art. 149) and `OT_NOTTURNO_FESTIVO` removed (the article sets no such rate) | Compare the bands a stored decision recorded; night-holiday overtime on commercio needs an explicit multiplier |

## Year-end shortfall deferral and foreign tax credit

`PriorYearTaxFacts` takes two inputs read on the conguaglio: the worker's
written request to defer the IRPEF the pay cannot cover (art. 23 c. 3 DPR
600/1973) and the foreign taxes paid on employment income of the year
(art. 165 TUIR). Without them every result is unchanged. See
[Fiscal: written deferral](engine/fiscal.md#written-deferral-of-the-year-end-shortfall)
and [Fiscal: foreign tax credit](engine/fiscal.md#foreign-tax-credit-at-the-conguaglio).

| Change | What to do |
|---|---|
| `PriorYearTaxFacts.shortfall_deferral` (`ShortfallDeferralRequest(signed_on)`) added | Pass it when the worker signed the request; a date outside the tax year and the next January and February raises `InvalidInputError` on the conguaglio |
| `EmploymentObligations.deferred_shortfall` (`DeferredShortfall`) holds the IRPEF a conguaglio deferred; `obligations.deferred_of(year)` | Persist it with the state; import a previous provider's deferral with `OpeningBalances.deferred_shortfall` |
| Lines `deferred_irpef_{year}_{run}` and `deferred_irpef_{year}_interest_{run}` on `ORDINARY_TAX`, coded 1066 | Remit them under 1066 with the tax year of the conguaglio as reference year; they are not in `TaxYtd.irpef` |
| A later run of the year of an open deferral counts it as withheld; one that would refund IRPEF raises `OutOfScopeError` (reason `shortfall_deferral_refund`) | Lower the deferral by the refund and settle that run manually |
| `ORDINARY_TAX` admits 1066 besides 1001 | Custom checks of the code of `ORDINARY_TAX` entries must accept it |
| Capability `shortfall_deferral`, reasons `shortfall_deferred`, `deferral_not_possible`, `deferred_shortfall_withheld`, `deferred_shortfall_unrecovered` (provisional, issue of the same code) | Handle them where reason codes are matched |
| `PriorYearTaxFacts.foreign_taxes` (`ForeignTaxPaid(country, income, tax)`, one per State) added | Pass the foreign income that entered the taxable income and the foreign tax paid on it, reduced for art. 165 c. 10 TUIR when needed |
| Tax computation component and capability `foreign_tax_credit`, reasons `credit_applied`, `limited_to_net_tax` | The net IRPEF of the conguaglio and the test of the surtax are after the credit |
| The withholding shortfall decision cites `dpr600-1973-art23-c3` instead of `dlgs33-2025-art33-c4` | Art. 23 DPR 600/1973 is in force until 31 December 2026 |
| `PeriodState.SCHEMA_VERSION` is 5 | A persisted state of version 4 has no deferred shortfall; it reads as none |

## Surtax tables of 2026 rebuilt from the MEF data

`regionale-2026.json` held rows under the wrong region (for example the
Emilia-Romagna rates under Veneto and the Lombardia rates under Toscana).
It is now taken row by row from the MEF 2026 pages, with the income-only
provisions (exemptions, whole-income rates, detrazioni) computed; see
[Fiscal: regional rates of 2026](engine/surtax.md#regional-rates-of-2026).
**This changes the regional surtax of almost every region.** Annual
regional surtax on a taxable income of 30,000 euro:

| Row | Before | After |
|---|---:|---:|
| Abruzzo | 541.00 | 525.00 |
| Basilicata | 369.00 | 369.00 |
| Bolzano | 519.00 | 0.00 |
| Calabria | 714.50 | 519.00 |
| Campania | 369.00 | 708.30 |
| Emilia-Romagna | 408.00 | 506.00 |
| Friuli-Venezia Giulia | 289.50 | 369.00 |
| Lazio | 657.60 | 699.00 |
| Liguria | 759.00 | 408.00 |
| Lombardia | 369.00 | 424.30 |
| Marche | 667.00 | 417.40 |
| Molise | 369.00 | 667.00 |
| Piemonte | 525.00 | 657.60 |
| Puglia | 465.30 | 541.00 |
| Sardegna | 369.00 | 369.00 |
| Sicilia | 369.00 | 369.00 |
| Toscana | 424.30 | 465.30 |
| Trento | 708.30 | 0.00 |
| Umbria | 417.40 | 564.50 |
| Valle d'Aosta | 369.00 | 369.00 |
| Veneto | 506.00 | 369.00 |

At exactly 30,000 euro Trento is still exempt and Lazio still grants its
60 euro detrazione; both end above 30,000.

`comunale-2026.json` now holds the 2026 rates where a delibera was
published (3,339 municipalities) and the 2025 rates, `provisional`, for the
others; it was the 2025 list for every municipality. It has a row for every
municipality of the MEF list, a zero-rate row for those without a surtax,
which were `table_unknown` before.

New reason codes, all `provisional`: `dependent_provisions_not_applied`
(regional, issue `regional_surtax_dependent_provisions_not_applied`) and
`specific_exemptions_not_applied` (municipal, issue
`municipal_surtax_specific_exemptions_not_applied`).
`prior_year_rates_applied` is now decided per municipal row
(`inputs["rates_year"]`). Handle them where reason codes are matched.

## Surtax withheld the year after the conguaglio

The regional and municipal surtax of a tax year is now determined by its
conguaglio and withheld on the payslips of the next year: the regional
surtax and the municipal saldo in up to eleven installments from January
to November, the municipal acconto of the next year in up to nine from
March to November (D.Lgs. 446/1997 art. 50 c. 4; D.Lgs. 360/1998 art. 1
cc. 4-5). The last run of the employment withholds everything at once. It
replaces the equal split of the projected annual surtax over the slots of
the same year. See
[Fiscal: when the surtax is withheld](engine/surtax.md#when-the-surtax-is-withheld).

**This changes net pay.** An employment the engine computes from January
2026 withholds no surtax in 2026 unless the surtax the 2025 conguaglio
determined is imported: the 2026 surtax is deferred to 2027. For a worker
employed in 2025, import the 2025 regional surtax, the 2025 municipal
saldo and the 2026 acconto with `OpeningBalances.surtax_obligations`,
otherwise the payslips of 2026 under-withhold what the law requires.

Commercio L4 resident in Sassari (`IT-88`, `I452`: Sardegna 1.23%, Sassari
0.8% above a 15,000 EUR threshold, both checked against the MEF tables),
bundled 2026 rules, 2027 on the same rules:

| | Before | After, nothing imported | After, 2025 surtax imported |
|---|---|---|---|
| 2026 surtax withheld | 333.64 (23.81 to 23.91 on each of 14 runs) | 0.00 | 462.29 (37.05 in January and February, 43.12 March to October, 43.23 in November, 0 in December and the extra months) |
| 2026 annual net | 20,589.83 | 20,923.47 | 20,461.18 |
| 2027 surtax withheld | 346.29 | 516.94 (2026 saldi 280.11 + 182.18, 2027 acconto 54.65) | |
| 2027 annual net | 21,134.80 | 20,964.15 | |

The imported column assumes 2025 amounts equal to the 2026 ones (regional
280.11, municipal saldo 127.53, acconto 54.65). The annual surtax is higher
than before because the engine used to withhold only the 30% acconto of
the municipal surtax and never its saldo.

| Change | What to do |
|---|---|
| `SurtaxObligation`, `SurtaxComponent` added to the public API; `EmploymentObligations.surtax` holds the surtax still to withhold | Persist it with the state; import the previous provider's amounts with `OpeningBalances.surtax_obligations` |
| `OpeningBalances.municipal_advance_withheld` and `TaxYtd.municipal_advance`: acconto withheld in the year | State it when taking over mid-year: the conguaglio deducts it from the municipal surtax |
| Surtax lines are `surtax_{component}_{reference year}_{run}` (`regional_balance`, `municipal_balance`, `municipal_advance`), coded 3802, 3848, 3847; `surtax_regional_{run}` and `surtax_municipal_{run}` are gone | Match the new ids or read the remittance summary |
| `AccountKind.SURTAX_REFUNDS` added: surtax withheld above what the conguaglio finds due (usually the acconto), given back on `surtax_refund_{run}` | Net = ... + `SURTAX_REFUNDS`; `TaxYtd.surtax` is `SURTAX` less `SURTAX_REFUNDS` |
| `TaxYtd.regional_settled`, `TaxYtd.municipal_settled`: surtax of the year a conguaglio on the last run of the employment withheld | A later termination run in the same year withholds only the difference |
| Surtax reason codes: `advance_applied` removed; `determined_at_conguaglio` on every run before the conguaglio; `prior_year_rates_applied` (provisional, issue `municipal_surtax_prior_year_rates`) while the bundled municipal table holds the rates of the year before; component decisions `deferred_to_installments`, `withheld_at_termination`, `surtax_refunded` and installment reasons | Handle them where reason codes are matched; select the annual decision as the one without `inputs["component"]` |
| The conguaglio of 2026 is `provisional` for a municipality: the bundled table has the 2025 rates | Check the municipal amounts against the 2026 deliberation |
| `PeriodState.SCHEMA_VERSION` is 4 | A persisted state of version 3 has no surtax obligations and no acconto withheld; add them before reuse |

## Credit offsets split from the IRPEF withholding

The ledger now keeps IRPEF withheld, credits paid, credits recovered and
IRPEF refunded on separate accounts, every entry non-negative, and tags
each tax and credit entry with its F24 codice tributo when verified (see
[Ledger accounts and F24 remittance](engine/payroll-state.md#ledger-accounts-and-f24-remittance)).

| Change | What to do |
|---|---|
| `AccountKind.CREDIT_RECOVERIES` added: credits taken back (somma esente, trattamento integrativo, carried installments), positive | Read recoveries there; they are no longer negative `CREDITS` entries |
| `AccountKind.CREDIT_RECOVERY_SHORTFALL` added: recovery the pay could not cover, given back | Read the positive `credit_recovery_shortfall_{run}` line there; a part carried in and withheld is on `CREDIT_RECOVERIES` |
| `AccountKind.TAX_REFUNDS` added: IRPEF refunded by the conguaglio | Move reads of `tax_refund_item` entries from `CREDITS` to `TAX_REFUNDS` |
| `CREDITS` holds only credits paid, never negative | Net = ... + `CREDITS` + `TAX_REFUNDS` + `CREDIT_RECOVERY_SHORTFALL` - `CREDIT_RECOVERIES`; update custom net formulas |
| A trattamento integrativo recovery posts the entry `tratt_integ_recovery_{run}` | The pay item keeps the id `tratt_integ_{run}` and its negative amount |
| The surtax posts `surtax_regional_{run}` and `surtax_municipal_{run}` (pay items too); `surtax_{run}` remains only for a surtax carried in when no annual surtax is left to split on | Match the three ids, or read the `SURTAX` account total, which is unchanged |
| `LedgerEntry.remittance_code` and `PostingIntent.remittance_code` added | Optional, default `None` |
| `PeriodResult.remittance_summary()`, `YearResult.remittance_summary()`, `RemittanceLine`, `RemittanceColumn` added | Use them to fill the F24 of each month of payment |
| Invariants `credit_non_negative` and `remittance_code_consistent` added | Handle them where invariant codes are matched |

Net pay and employer cost are unchanged.

## Household employers withhold no tax

A household employer is not a withholding agent (art. 23 c. 1 DPR 600/1973;
art. 33 c. 1 D.Lgs. 33/2025 from 2027). The domestic CCNLs now withhold no
IRPEF or surtax and pay no tax credit: see
[Domestic work](engine/domestic-work.md#no-withholding-on-the-payslip).

| Change | What to do |
|---|---|
| `CCNLMeta.withholding_exempt` removed | Read `CCNLMeta.withholding_agent`, derived from `tax_sector`; drop `"withholding_exempt"` from custom CCNL JSON, which now rejects it |
| Domestic payslips: no `ordinary_tax`, `surtax`, `substitute_tax` or `credits` entries, empty `tax_computation` | Net is gross less employee contributions; do not expect IRPEF lines |
| Reason code `not_withholding_agent` on the skipped capabilities | Handle it where reason codes are matched; the traces are `not_applicable` |
| Invariant `non_agent_untaxed` | Handle it where invariant codes are matched |
| Opening state with recoveries, shortfall or tax withheld rejected for a domestic CCNL | Start household employments from a zero tax state |

Amounts change only for the two domestic CCNLs.

## Provenance status required on every rule record

Every `provenance` record now declares a `status`: `verified`, `derived`,
`assumed` or `missing` (see [Provenance](trust/provenance.md)). Bundled data
is migrated; caller-supplied data must add it.

| Change | What to do |
|---|---|
| `RuleProvenance.status` is required | Add `"status"` to each `provenance` object; `uv run python scripts/data/assign_rule_provenance.py` shows the mapping |
| `RuleProvenance.location` and `extraction` are optional | Guard `record.location` and `record.extraction` against `None` |
| `verified` needs `extraction.verified_by` and `verified_at` | Records claiming a check without both are rejected |
| Non-gap `additional_months` periods need a record at load | Add a `provenance` to each period |
| `PreferentialTaxRegime.source_status` is required | Add `"source_status": "derived"` (or `"assumed"`) next to `source` |
| `CapabilityReport.rule_sources` added | Read the weakest status per executed capability |
| `SourceKind.DLGS`, `SourceKind.AMMINISTRAZIONE` added | Match them where kinds are enumerated |
| New issues `rule_source_missing` (incomplete) and `employer_rate_category_assumed` (provisional) | Handle them where issue codes are matched |

Amounts are unchanged.

## Oversized domain and service modules split

Seven modules were split by responsibility. Only internal module paths
change: names exported from `ccnl_engine` are unchanged, and so are amounts.
Names not listed stay where they were.

| Name | Before | After |
|---|---|---|
| `WeeklyHours`, `SeniorityMonths` (since replaced by `SeniorityFact`), `ContributableHours`, `EmploymentPeriod`, `check_within_full_time` | `payroll.domain.employment` | `payroll.domain.employment_facts` |
| `PeriodState` | `payroll.domain.period` | `payroll.domain.period_state` |
| `PeriodCalculationRequest` | `payroll.domain.period` | `payroll.domain.period_request` |
| `YearInput` | `payroll.domain.inputs` | `payroll.domain.year_input` |
| `ExtraMonthEntitlement` | `payroll.domain.calendar` | `payroll.domain.extra_month_entitlement` |
| `AccrualWindow`, `ExtraMonthKind`, `ExtraMonthSchedule` | `payroll.domain.calendar` | `payroll.domain.extra_month_schedule` |
| `CreditAccount`, `TrattamentoAccount`, `SommaEsenteAccount`, `UlterioreDetrazioneAccount` | `payroll.domain.ytd_accounts` | `payroll.domain.credit_accounts` |
| `InpsEmployeeTier`, `InpsEmployerTier`, `InpsRawRates`, `ApprenticeRawRates` | `tax.domain.contribution_rules` | `tax.domain.contribution_tiers` |
| `DomesticInpsRates`, `DomesticInpsHoursBracket`, `DomesticInpsWageBracket` | `tax.domain.contribution_rules` | `tax.domain.domestic_contribution_rules` |
| `work_income_deduction`, `for_days`, `apply_sterilizzazione_detrazioni` | `payroll.service.irpef` | `payroll.service.irpef_deductions` |
| `somma_esente` | `payroll.service.irpef` | `payroll.service.irpef_credits` |

Every path is relative to `ccnl_engine`.

## Rounding and bundled repository moved to their layers

Two internal modules moved so that the layers import in one direction only.
Names exported from `ccnl_engine` and amounts are unchanged.

| Before | After |
|---|---|
| `ccnl_engine.payroll.service.rounding` | `ccnl_engine.payroll.domain.rounding` |
| `ccnl_engine.knowledge.service.bundled_knowledge_repository` | `ccnl_engine.payroll.service.bundled_knowledge_repository` |

## Engine package flattened into capabilities

The `ccnl_engine.engine` wrapper is removed. Its subpackages are now
capabilities directly under `ccnl_engine`. Only internal module paths change:
names exported from `ccnl_engine` are unchanged, and so are amounts.

| Before | After |
|---|---|
| `ccnl_engine.engine.contract.*` | `ccnl_engine.contract.*` |
| `ccnl_engine.engine.tax.*` | `ccnl_engine.tax.*` |
| `ccnl_engine.engine.surtax.domain.rules` | `ccnl_engine.tax.domain.surtax_rules` |
| `ccnl_engine.engine.surtax.service.loaders` | `ccnl_engine.tax.service.surtax_loaders` |
| `ccnl_engine.engine.provenance.*` | `ccnl_engine.provenance.*` |
| `ccnl_engine.engine.metadata.domain.rules` | `ccnl_engine.provenance.domain.ruleset_identity` |
| `ccnl_engine.engine.diff.*` | `ccnl_engine.diff.*` |
| `ccnl_engine.engine.errors` | `ccnl_engine.shared.domain.errors` |
| `ccnl_engine.engine.primitives.domain.primitives` | `ccnl_engine.shared.domain.primitives` |
| `ccnl_engine.engine.io.service.*` | `ccnl_engine.knowledge.service.*` |
| `ccnl_engine.engine.capability_catalog` | `ccnl_engine.payroll.domain.capability_catalog` |
| `ccnl_engine.engine.knowledge_repository` | `ccnl_engine.payroll.application.knowledge_repository` |
| `PolicyResolver.load()` | `ccnl_engine.payroll.service.policy_loader.load_policy_resolver()` |

The paths in the "After" column of the next section predate this change: read
them through the table above.

## Legacy modules and aliases removed

Every public name is now imported from `ccnl_engine`; internal modules are
imported from the module that defines them. The re-export modules, the empty
`serialization` stubs and the alias names are removed without a compatibility
layer. Amounts are unchanged.

| Before | After |
|---|---|
| `from ccnl_engine.events import OvertimeEvent` (any work event) | `from ccnl_engine import OvertimeEvent` |
| `PayrollState` | `PeriodState` |
| `PayrollCalendar` | `WorkCalendar` |
| `ccnl_engine.api.PeriodInput` (any name of `ccnl_engine.api`) | `ccnl_engine.PeriodInput` |
| `ccnl_engine.engine.contract.domain.ccnl.CCNL` | `ccnl_engine.engine.contract.domain.identity.CCNL` (identity, coverage, metadata and enums); other names from their own module: `compensation`, `absence`, `category`, `seniority`, `sickness`, `working_time` |
| `ccnl_engine.engine.tax.domain.rules.YearRules` | `ccnl_engine.engine.tax.domain.ruleset.YearRules`; other names from `contribution_rules`, `credit_rules`, `irpef_rules`, `tfr_rules` |
| `ccnl_engine.engine.tax.service.loaders.load_year_rules` | `ccnl_engine.engine.tax.service.tax_annual_assembler.load_year_rules`; the other loaders from `tax_optional_loaders`, `tax_resource_reader`, `tax_tier_resolver` |
| `from ccnl_engine.engine.tax import load_year_rules` (and the same for `contract`, `surtax`, `diff`, `io`, `metadata`, `primitives`, `provenance`) | import from the defining module, e.g. `ccnl_engine.engine.surtax.service.loaders.load_surtax_rules` |
| `ccnl_engine.knowledge.version.__version__` | `ccnl_engine.knowledge.__version__` |
| `ccnl_engine.engine.serialization` | removed: it held no code |

Unused internals are removed as well: the `Ledger` and `Posting` classes and
the `AccountPolicy` alias of `payroll.domain.ledger`, `AnnualisedPay`,
`MonthlyPayChain.scaled_selective()`, `resolve_tax_computation` (use `compute_tax(...).computation`),
`RulesetIdentity.as_dict()`, and the contribution helpers
`inps_contribution`, `inps_employee_additional`, `tfr` and `fund_applies_to`
(the payroll uses `resolve_contributions`).
