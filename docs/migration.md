# Migration guide

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
[Fiscal: regional rates of 2026](engine/fiscal.md#regional-rates-of-2026).
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
[Fiscal: when the surtax is withheld](engine/fiscal.md#when-the-surtax-is-withheld).

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

## PeriodInput and YearInput

The facade no longer takes a flat request. `calculate_period()` takes a
`PeriodInput` and `calculate_year()` a `YearInput`; both group the facts by
owner and are validated when built. There is no compatibility layer: every
name in the left column is removed.

| Before | After |
|---|---|
| `engine.calculate(PayrollRequest(...))` | `engine.calculate_period(PeriodInput(...))` |
| `engine.calculate_year(PayrollYearRequest(...))` | `engine.calculate_year(YearInput(...))` |
| `PayrollEngine.from_builtin_data()` | `PayrollEngine.bundled()` |
| `PayrollRequest.ccnl_slug`, `level_code` | `Employment.ccnl_slug`, `Employment.level_code` |
| `EmploymentFacts(...)` | `Employment(...)`, with the CCNL slug and the level |
| `EmploymentFacts(weekly_hours=25, full_time_weekly_hours=40)` | `Employment(weekly_hours=WeeklyHours(25), full_time_weekly_hours=WeeklyHours(40))` |
| `EmploymentFacts(seniority_months=60)` | `Employment(seniority=SeniorityFact(60, as_of, source))` |
| `EmploymentFacts(started_on=..., ended_on=...)` | `Employment(employment_period=EmploymentPeriod(started_on, ended_on))` |
| `EmploymentFacts(contributable_hours=Decimal(108))` | `PeriodFacts(contributable_hours=ContributableHours(Decimal(108)))` |
| sector derived from the CCNL tax sector | `Employment.sector` (`EmploymentSector.PRIVATE` or `PUBLIC`), `None` means unknown |
| `Employer()` (50 employees when omitted) | `EmployerProfile(headcount=Headcount(n))`, required on every input |
| no employer activity | `EmployerProfile.activity` (`EmployerActivity`), `None` means unknown |
| `prior_income=` on `BonusEvent`, `NightShiftEvent`, `HolidayWorkEvent`, `ShiftWorkEvent` | `PriorYearTaxFacts(employment_income=...)` on the input, once |
| `substitute_tax_waived=True` on an event | `PriorYearTaxFacts(waived_regimes=frozenset({SubstituteTaxRegime.RINNOVO}))` |
| renewal signing date not received | `BonusEvent(kind="contract_renewal", agreement_signed_on=...)` |
| `regione`, `comune_belfiore`, `family_composition`, `has_dependent_children` on the request | `PeriodFacts` of the run |
| `events=` on `PayrollRequest` | `PeriodFacts(events=...)` |
| `period_events={3: (...)}` | `YearInput.periods={3: PeriodFacts(events=...)}` |
| `per_run_events={"2026-12-thirteenth": (...)}` | `YearInput.periods={"2026-12-thirteenth": PeriodFacts(events=...)}` |
| year-level `regione`, family, `contributable_hours` | `YearInput.default_facts` (an entry in `periods` replaces it for its run) |
| `PayrollYearRequest.calendar` | `YearInput.calendar_override` |
| `PayrollResult` (alias of `PeriodCalculationResult`) | `PeriodResult` |
| `PayrollYearResult` (`YearCalculationResult`) | `YearResult`, with `closing_state` of the last run |
| `year.period_results[-1].closing_state` | `year.closing_state` |
| `SupplementaryAllowance`, `AgreementKind` | removed: second-level amounts are not an engine input |
| `RinnovoRules` | `PreferentialTaxRegime` with `agreements_signed_from` and `agreements_signed_until` |

```python
from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerActivity,
    EmployerProfile,
    Employment,
    EmploymentSector,
    Headcount,
    NightShiftEvent,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    YearInput,
)

engine = PayrollEngine.bundled()
employment = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    seniority=SeniorityFact(36, date(2026, 1, 1), SenioritySource.PAYSLIP),
    sector=EmploymentSector.PRIVATE,
)
employer = EmployerProfile(headcount=Headcount(100), activity=EmployerActivity.OTHER)
prior_year = PriorYearTaxFacts(employment_income=Decimal(30_000))
base = PeriodFacts(regione="IT-45", comune_belfiore="F257")

january = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(2026, 1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
        facts=base,
        prior_year=prior_year,
    )
)

night = NightShiftEvent(event_date=date(2026, 3, 10), supplement_amount=Decimal(200))
year = engine.calculate_year(
    YearInput(
        year=2026,
        employment=employment,
        employer=employer,
        prior_year=prior_year,
        default_facts=base,
        periods={3: replace(base, events=(night,))},
    )
)
opening_2027 = engine.close_tax_year(year.closing_state)
```

Behaviour that changes with the inputs:

- The sector of the employment is declared, not derived from the CCNL: a
  public employer applying a private CCNL is public. When `sector` is `None`
  the renewal and the night, holiday and shift regimes are `unknown` and the
  result is `provisional`. Declare `EmploymentSector.PRIVATE` to keep a
  private-sector worker eligible.
- L. 199/2025 art. 1 c. 11 excludes the activities of c. 18 (food and
  beverage service, tourism, thermal establishments) from the night, holiday
  and shift regime: such an employer is `ineligible`, and an employer whose
  activity is `None` is `unknown`.
- A renewal increment is eligible only when `agreement_signed_on` lies
  between 1 January 2024 and 31 December 2026; without it the renewal is
  `unknown`.
- A year run takes one prior-year income for every regime and every run:
  the same worker cannot carry different incomes on different events.
- Naming the same run twice in `periods` (by month and by run id) raises
  `InvalidInputError`, a `ValueError`, at construction.
- `default_facts` must carry no event.

Amounts are unchanged for the same facts: the documentation examples print
the same figures as before the change.

## Earlier changes

The sections below document earlier releases. Their code uses the names of
the release that introduced them; the table above gives the current name.

### From `estimate_annual()` to `PayrollEngine`

The entry point changed from `estimate_annual()` to `PayrollEngine`.

`estimate_annual()` computed an annual gross-to-net projection in a single call.
`PayrollEngine.calculate()` (now `calculate_period()`) computed one payroll run at a time, threading
YTD state (`PeriodState`) between runs. `PayrollEngine.calculate_year()` does
the full sequence in one call.

#### Before (removed)

```python
from datetime import date
# estimate_annual was removed in v0.5; use PayrollEngine instead.
result = ...  # AnnualEstimateInput / estimate_annual no longer available
```

The current API is described in the first section of this page.

#### `estimate_annual` is removed

`estimate_annual` and the `ccnl_engine.engine.payroll` namespace were removed
in v0.5. Migrate to `PayrollEngine` for all new code.

### Surtax codes and decisions

- `regione` takes the ISO 3166-2:IT region code (`IT-45` Emilia-Romagna,
  `IT-25` Lombardia, ...), with `IT-BZ` and `IT-TN` for the autonomous
  provinces, listed in `ccnl_engine.payroll.domain.jurisdiction.REGION_CODES`.
  A region name such as `"Lombardia"`, a short code such as `"ER"` and
  `"IT-32"` (Trentino-Alto Adige) now raise `InvalidInputError`, like a
  malformed Belfiore code.  Before, a code such as `"ER"` matched no regional row and the
  regional surtax was silently zero.
- A well-formed code without a table row makes the result `incomplete`, with
  the issue `regional_surtax_unknown` or `municipal_surtax_unknown`.
- `ccnl_engine.payroll.domain.fiscal.FiscalSimplification` is removed: read the
  surtax outcome from `result.decisions` (capabilities
  `addizionale_regionale`, `addizionale_comunale`).

### Payroll state: tax year and obligations

`PayrollState` (`PeriodState`) is now a composite of the tax year state and
the obligations that survive the year change.

| Before | After |
|---|---|
| `state.earnings`, `state.tax`, `state.fringe`, `state.trattamento`, `state.somma_esente`, `state.work_time_regime` | `state.ytd.<same name>` |
| `state.regular_periods_closed`, `state.tax_withholding_periods_closed`, `state.closed_run_ids` | `state.ytd.<same name>` |
| `state.tax_year` | unchanged (shortcut for `state.ytd.tax_year`) |
| `PayrollState(tax=TaxYtd(...), ...)` | `PayrollState(ytd=TaxYearState(tax=TaxYtd(...), ...))`, or `OpeningBalances(...).to_state()` |
| `TrattamentoAccount(plan=...)` | `PayrollState(obligations=EmploymentObligations(recoveries=(RecoveryObligation(tax_year, plan),)))` |
| `closing_state.zero()` to start a new year (dropped a running recovery) | `PayrollEngine.close_tax_year(closing_state)` |
| `calculate_year` always started from zero | `PayrollYearRequest.opening_state` / `calculate_year(opening_state=...)` |

- `PeriodState.SCHEMA_VERSION` is now 2.
- `TaxYearState.withholding_slots` records the slots of the schedule of the
  last run; `close_tax_year` requires them all closed.
- Installments of a recovery carried from an earlier year are posted as a
  negative tax credit line `trattamento_integrativo_recovery_{year}_{run_id}`
  and no longer suppress the trattamento integrativo of the new year.  Each one records a decision with capability
  `trattamento_integrativo_recovery`.
- `KnowledgeRepository` gains `load_variable_pay_rules(year)` and
  `load_family_deduction_rules(year)`; a custom repository must implement
  them.
- New public names: `OpeningBalances`, `RecoveryObligation`, `RecoveryPlan`.

### Credit accounts and run ids

| Before | After |
|---|---|
| `state.ytd.closed_run_ids: frozenset[str]` | `tuple[PayrollRunId, ...]` in closing order; `PayrollRunId.parse("2026-01-regular")` |
| `OpeningBalances(closed_run_ids=frozenset({"2026-06-regular"}))` | `OpeningBalances(closed_run_ids=(PayrollRunId.parse("2026-06-regular"),))` |
| `obligations.recovery_of(tax_year)` | `obligations.recovery_of(tax_year, kind)`, kind `"trattamento_integrativo"` or `"somma_esente"` |
| `SommaEsenteAccount(recognized=...)` only | `CreditAccount` schema: `recognized`, `recovered`, `due`, `reason`, `net`, `residual` |
| bare period run id `"2026_01"` in item ids | `"2026-01-regular"`, the regular run of the month |

- A run already closed, of a year after the tax year, or before a closed run
  of the tax year raises `InvalidInputError` (feature `payroll_run`), a
  subclass of `ValueError` as before.
- Every YTD total rejects a negative amount. A run producing one fails with
  `DataIntegrityError`; an `OpeningBalances` with one raises
  `InvalidInputError` naming the account field (`EarningsYtd.gross`).
- The somma esente is settled at the conguaglio: the credits of a full year
  now add up to the annual amount (before, the last slot paid a plain share
  and the total could drift by several EUR from the annual due). An excess
  is recovered in full up to 60 EUR, in ten installments above it
  (L. 207/2024 art. 1 c. 7). Every run records a decision with capability
  `somma_esente`; carried installments record `somma_esente_recovery`.
- `OpeningBalances` gains `somma_esente_recovered`.
- `PeriodState.SCHEMA_VERSION` is now 3: a persisted state of version 2
  needs its closed run ids parsed into `PayrollRunId` and its credit accounts
  read with `due` and `reason` unset.
- New public name: `PayrollRunId`.

### Decisions and capability report

- `result.decisions` now also holds the decisions of the tax credits
  (`ulteriore_detrazione_lavoro`, `trattamento_integrativo`), of the worker
  category, of seniority, of family deductions and of the PdR substitute tax.
  Filter by `capability` instead of assuming only surtax or regime records.
  `YearCalculationResult.decisions` concatenates the decisions of every run.
- The capability report traces each feature from what the run executed: an
  event present in the request with no effect is skipped, and the two credits
  are no longer always computed.  A surtax without a table is now reported as
  an `unresolved` gap (`CapabilityGapKind.UNRESOLVED`).
- `trattamento_integrativo` and `ulteriore_detrazione_lavoro` moved from
  `ccnl_engine.payroll.service.irpef` to
  `ccnl_engine.payroll.service.irpef_credits`.

### Invariants and input checks

- The reconciliation invariants have descriptive codes instead of `I1` to
  `I19` and `L1` to `L4` (for example `net_identity` for `I9`,
  `employee_contribution_non_negative` for `L3`); see the
  [glossary](domain/glossary.md#reconciliation-invariants). The code is the
  `invariant_id` of a `ReconciliationViolation` and appears as `[code]` in
  the `DataIntegrityError` message.
- `legal_invariants` is renamed `sign_invariants`; `reconcile()` takes an
  optional `RunFacts` for the checks that need facts the result does not
  carry.
- `PeriodCalculationRequest` rejects a field of the wrong type (a raw `int`
  for `weekly_hours`, a string for `payment_date`) with `InvalidInputError`
  instead of an `AttributeError` later, and a regular run for a month
  without a day of employment with `InvalidInputError`.
- The IRPEF projection enters the current run with its actual employee
  INPS (IVS ceiling and 1% addizionale included) instead of the total rate
  times the gross; only the slots still to come are projected at the rate.
  Above the 1% addizionale threshold the conguaglio now settles on the final
  taxable income: for bancari-abi QD4 in 2026 the IRPEF withheld over the
  year falls by 22.19 EUR (18,333.08 to 18,310.89 EUR). Below the threshold
  the annual IRPEF is unchanged and single runs can move by a cent.
- Unpaid absences above the monthly pay of the run raise `InvalidInputError`
  instead of `DataIntegrityError`. Absences that leave less pay than the
  IRPEF and surtax due no longer raise `OutOfScopeError`: the taxes are
  withheld up to the pay left and the rest is carried in
  `state.ytd.shortfall` to the next runs (see
  [Fiscal: shortfall](engine/fiscal.md#pay-that-does-not-cover-the-tax)).
  Metalmeccanico C3 with 160 absence hours in January 2026 now nets
  0.00 EUR, withholding 143.25 of the 162.33 EUR of IRPEF due, and February
  withholds the 19.08 EUR carried. `OutOfScopeError` (reason
  `withholding_shortfall`) remains only when the other deductions exceed
  the pay left.

### Fiscal rule corrections

- The ulteriore detrazione (L. 207/2024 art. 1 c. 6) recognized by the
  withholding is tracked in `state.ytd.ulteriore_detrazione`. An excess
  found at the conguaglio above 60 EUR is recovered in ten installments
  (c. 7): the first on the conguaglio, nine from the first run of the next
  year. Before, the conguaglio took it back in full. No bundled scenario
  changes: none reaches the conguaglio with the deduction no longer due.
- `OpeningBalances` accepts `*_due` and `*_reason` for each credit, the
  ulteriore detrazione totals and the IRPEF and surtax shortfall.
- The capability catalog declares `somma_esente`, `withholding_shortfall`
  and the two substitute tax regimes (`partially_computed`: their
  eligibility rests on the declared prior income).
- One-off income of a run (bonus, overtime, ordinary arrears, excess PdR,
  ratei settled at termination) has its IRPEF withheld on that run: the net
  annual IRPEF with the income less the net annual IRPEF without it. Before,
  that tax was spread over the remaining slots, so a 20,000 EUR bonus in
  November left the tredicesima run with a negative net and the year failed
  with `DataIntegrityError`. The annual IRPEF is unchanged; the runs that
  pay one-off income withhold more and the later runs less.
- The regional and municipal surtaxes are due only when the net IRPEF
  (gross less the deductions) is due, not the gross IRPEF. A 12-hour
  part-time Metalmeccanico C3 in Lombardia no longer withholds 93.71 EUR of
  regional surtax a year; the decisions record `no_irpef_due`.
- The work deduction, the ulteriore detrazione and the trattamento
  integrativo follow `days / 365` without truncating the day ratio to four
  decimals: 92 days of the 1,955 EUR deduction give 492.77 EUR instead of
  492.66. The ulteriore detrazione is rounded to cents.
- The somma esente percentage is chosen on the employment income
  annualised to the whole year and applied to the income of the year: a
  Metalmeccanico C3 ended on 31 May receives 507.90 EUR (4.8%) instead of
  560.80 (5.3%).
- A run with a somma esente due carries the `provisional` issue
  `somma_esente_income_assumed`: the reddito complessivo is taken as the
  employment income. Low-income results that were `final` are now
  `provisional`. `YearCalculationResult.issues` lists an issue repeated on
  every run once, at its first run (same `code` and `message`); the issues
  of each run stay on `period_results`.
- The projection of a future tredicesima or quattordicesima uses the rateo
  accrued on the employment period instead of a full month: a worker hired
  on 1 July withholds evenly over the seven slots of the year instead of
  overwithholding until the conguaglio.
