# Production map

Part of the [Architecture contract](architecture-contract.md). The target
of every module under `src/ccnl_engine` today, grouped by concept. Two or
more modules with one target merge; a module with several targets splits
by concept. Each concept migration applies its rows and maps them in the
inventory.

## Package root

| Today | Target |
|---|---|
| `api.py` | `api.py` |
| `errors.py` | `errors.py` |
| `events.py` | `events.py` |
| `inputs.py` | `inputs.py` |
| `results.py` | `results.py` |
| `primitives.py` | `types.py` |
| `validation.py` | `validators.py` |
| `version.py` | `version.py` |

## absence

| Today | Target |
|---|---|
| `payroll/event/inputs_absence_sickness.py` | `absence/inputs.py` |
| `contract/absence/models.py` | `absence/models.py` |

## agreement

| Today | Target |
|---|---|
| `contract/identity/models_coverage.py` | `agreement/coverage/models.py` |
| `contract/identity/models_series_coverage.py` | `agreement/coverage/models.py` |
| `contract/identity/facade.py` | `agreement/facade.py` |
| `contract/identity/models_meta.py` | `agreement/metadata/models.py` |
| `contract/identity/models.py` | `agreement/models.py` |
| `contract/identity/types.py` | `agreement/types.py` |
| `contract/identity/validators.py` | `agreement/validators.py` |
| `contract/identity/models_validity_window.py` | `agreement/validity/models.py` |
| `contract/identity/rules_validity.py` | `agreement/validity/rules.py` |

## apprenticeship

| Today | Target |
|---|---|
| `contract/employment/models_apprenticeship.py` | `apprenticeship/models.py` |
| `payroll/employment/rules_apprenticeship.py` | `apprenticeship/rules.py` |

## assurance

| Today | Target |
|---|---|
| `payroll/assurance/models.py` | `assurance/models.py` |
| `payroll/assurance/policies_engine_mode.py` | `assurance/policies.py` |
| `payroll/assurance/services_rule_source.py` | `assurance/rule_source/services.py` |
| `payroll/assurance/rules_assessment.py` | `assurance/rules.py` |
| `payroll/assurance/services_ruleset.py` | `assurance/ruleset/services.py` |

## balance

| Today | Target |
|---|---|
| `payroll/state/models_ytd_account.py` | `balance/cash/account/models.py` |
| `payroll/state/models_tax_cash.py` | `balance/cash/models.py` |
| `payroll/state/services_closing.py` | `balance/closing/services.py` |
| `payroll/state/models_accrual.py` | `balance/competence/models.py` |
| `payroll/state/models.py` | `balance/models.py` |
| `payroll/state/models_obligation.py` | `balance/obligation/models.py` |
| `payroll/state/services_opening_balance.py` | `balance/opening/provider/services.py` |
| `payroll/state/validators_opening_balance.py` | `balance/opening/provider/validators.py` |
| `payroll/state/rules_opening_history.py` | `balance/opening/rules.py` |
| `payroll/state/services_opening.py` | `balance/opening/services.py` |
| `payroll/state/serializers.py` | `balance/serializers.py` |
| `payroll/state/serializers_persistence.py` | `balance/serializers.py` |

## capability

| Today | Target |
|---|---|
| `payroll/capability/services_applicability.py` | `capability/applicability/services.py` |
| `knowledge/capability/loaders.py` | `capability/loaders.py` |
| `payroll/capability/models_catalog.py` | `capability/registry/models.py` |
| `payroll/capability/services_registry.py` | `capability/registry/services.py` |
| `payroll/capability/rules_requirement.py` | `capability/requirement/rules.py` |
| `payroll/capability/results.py` | `capability/results.py` |
| `payroll/capability/services_rule_lookup.py` | `capability/rule/services.py` |
| `payroll/capability/services_coverage.py` | `capability/support/services.py` |
| `payroll/capability/models_trace.py` | `capability/trace/models.py` |
| `payroll/capability/services_trace.py` | `capability/trace/services.py` |

## catalog

| Today | Target |
|---|---|
| `catalog.py` | `catalog/facade.py` |
| `contract/catalog/loaders.py` | `catalog/loaders.py` |
| `contract/catalog/loaders_discovery.py` | `catalog/loaders.py` |
| `contract/catalog/models_readiness.py` | `catalog/models.py` |
| `contract/catalog/services.py` | `catalog/services.py` |

## collection

| Today | Target |
|---|---|
| `validation_collection.py` | `collection/validators.py` |

## comparison

| Today | Target |
|---|---|
| `comparison/ruleset/rules.py` | `comparison/ruleset/rules.py` |
| `comparison/ruleset/serializers.py` | `comparison/ruleset/serializers.py` |
| `comparison/ruleset/services.py` | `comparison/ruleset/services.py` |

## compensation

| Today | Target |
|---|---|
| `payroll/amount/rules_chain.py` | `compensation/element/rules.py` |
| `payroll/amount/services_chain.py` | `compensation/element/services.py` |
| `payroll/amount/types_chain.py` | `compensation/element/types.py` |
| `contract/compensation/models.py` | `compensation/models.py` |
| `payroll/amount/rules_proration.py` | `compensation/proration/rules.py` |
| `payroll/amount/services_proration.py` | `compensation/proration/services.py` |
| `payroll/amount/services_provincial.py` | `compensation/provincial_element/services.py` |
| `payroll/amount/services_erc.py` | `compensation/raccordo/services.py` |
| `payroll/amount/rules_renewal_minimum.py` | `compensation/renewal_minimum/rules.py` |
| `payroll/amount/services_renewal_minimum.py` | `compensation/renewal_minimum/services.py` |

## contribution

| Today | Target |
|---|---|
| `tax/contribution/models_additional_ivs.py` | `contribution/additional_ivs/models.py` |
| `payroll/contribution/rules_additional_ivs.py` | `contribution/additional_ivs/rules.py` |
| `payroll/contribution/services_additional_ivs.py` | `contribution/additional_ivs/services.py` |
| `payroll/contribution/rules_apprentice_rate.py` | `contribution/apprenticeship/rules.py` |
| `payroll/contribution/models_inps_base.py` | `contribution/base/models.py` |
| `payroll/contribution/services_other_employer.py` | `contribution/base/other_employment/services.py` |
| `payroll/contribution/inputs_eligibility.py` | `contribution/ceiling/inputs.py` |
| `payroll/contribution/services_ivs_ceiling.py` | `contribution/ceiling/services.py` |
| `payroll/contribution/services_decision.py` | `contribution/decision/services.py` |
| `tax/contribution/models_domestic.py` | `contribution/domestic/models.py` |
| `payroll/contribution/rules_domestic_rate.py` | `contribution/domestic/rules.py` |
| `payroll/contribution/services_domestic.py` | `contribution/domestic/services.py` |
| `payroll/contribution/services_enam.py` | `contribution/enam/services.py` |
| `tax/contribution/models_fis_reduction.py` | `contribution/fis/models.py` |
| `tax/contribution/models_tier.py` | `contribution/headcount/models.py` |
| `tax/contribution/rules_tier.py` | `contribution/headcount/rules.py` |
| `payroll/contribution/models_minimum_base.py` | `contribution/minimum_base/models.py` |
| `tax/contribution/models_minimum_base.py` | `contribution/minimum_base/models.py` |
| `payroll/contribution/rules_minimum_base.py` | `contribution/minimum_base/rules.py` |
| `payroll/contribution/services_minimum_base.py` | `contribution/minimum_base/services.py` |
| `payroll/contribution/rules_naspi.py` | `contribution/naspi/rules.py` |
| `payroll/contribution/services_naspi.py` | `contribution/naspi/services.py` |
| `tax/contribution/models.py` | `contribution/rate/models.py` |
| `payroll/contribution/rules_rate.py` | `contribution/rate/rules.py` |
| `payroll/contribution/results.py` | `contribution/results.py` |
| `payroll/contribution/rules.py` | `contribution/rules.py` |
| `payroll/contribution/services.py` | `contribution/services.py` |
| `tax/contribution/models_zone_reduction.py` | `contribution/zone/models.py` |

## decision

| Today | Target |
|---|---|
| `payroll/assurance/models_decision.py` | `decision/models.py` |

## default

| Today | Target |
|---|---|
| `payroll/period/policies_default_event.py` | `default/event/policies.py` |
| `payroll/period/policies_default_fact.py` | `default/fact/policies.py` |
| `payroll/period/models_default.py` | `default/models.py` |
| `payroll/period/policies_default_registry.py` | `default/policies.py` |
| `payroll/period/policies_default_request.py` | `default/request/policies.py` |

## employer

| Today | Target |
|---|---|
| `payroll/employment/inputs_employer.py` | `employer/inputs.py` |

## employment

| Today | Target |
|---|---|
| `contract/employment/models_category.py` | `employment/category/models.py` |
| `payroll/employment/rules_category.py` | `employment/category/rules.py` |
| `payroll/employment/models_context.py` | `employment/context/models.py` |
| `payroll/employment/inputs_fact.py` | `employment/fact/inputs.py` |
| `payroll/employment/services_fact.py` | `employment/fact/services.py` |
| `payroll/employment/inputs_fixed_term.py` | `employment/fixed_term/inputs.py` |
| `payroll/employment/inputs.py` | `employment/inputs.py` |
| `payroll/employment/models_spell.py` | `employment/spell/models.py` |

## end_of_service

| Today | Target |
|---|---|
| `payroll/contribution/services_public_end_of_service.py` | `end_of_service/services.py` |

## event

| Today | Target |
|---|---|
| `payroll/event/services_allocation.py` | `event/allocation/services.py` |
| `payroll/event/facade.py` | `event/facade.py` |
| `payroll/event/handlers_context.py` | `event/handlers.py` |
| `payroll/event/handlers_registry.py` | `event/handlers.py` |
| `payroll/event/handlers_standard.py` | `event/standard/handlers.py` |
| `payroll/event/handlers_totals.py` | `event/total/handlers.py` |
| `payroll/event/types.py` | `event/types.py` |

## extra_month

| Today | Target |
|---|---|
| `payroll/accrual/services_decision.py` | `extra_month/decision/services.py` |
| `payroll/accrual/models_extra_month_entitlement.py` | `extra_month/entitlement/models.py` |
| `payroll/termination/services_ratei.py` | `extra_month/liquidation/services.py` |
| `payroll/accrual/models.py` | `extra_month/models.py` |
| `payroll/accrual/services_extra_month_qualification.py` | `extra_month/qualification/services.py` |
| `payroll/accrual/services_rule.py` | `extra_month/qualification/services.py` |
| `payroll/accrual/models_extra_month_schedule.py` | `extra_month/schedule/models.py` |
| `payroll/accrual/services_extra_month.py` | `extra_month/services.py` |
| `payroll/accrual/services_extra_month_settlement.py` | `extra_month/settlement/services.py` |

## family

| Today | Target |
|---|---|
| `payroll/family/rules_ascendant.py` | `family/ascendant/rules.py` |
| `payroll/family/rules_child.py` | `family/child/rules.py` |
| `payroll/family/inputs.py` | `family/inputs.py` |
| `tax/family/models.py` | `family/models.py` |
| `payroll/family/rules.py` | `family/rules.py` |
| `payroll/family/rules_deduction.py` | `family/rules.py` |
| `payroll/family/services.py` | `family/services.py` |
| `payroll/family/rules_spouse.py` | `family/spouse/rules.py` |

## fund

| Today | Target |
|---|---|
| `contract/fund/models_assistance.py` | `fund/assistance/models.py` |
| `payroll/contribution/policies_assistance.py` | `fund/assistance/policies.py` |
| `payroll/contribution/rules_assistance.py` | `fund/assistance/rules.py` |
| `payroll/contribution/policies_contractual_eligibility.py` | `fund/contractual/policies.py` |
| `payroll/contribution/rules_contractual_fund.py` | `fund/contractual/rules.py` |
| `contract/fund/models.py` | `fund/models.py` |
| `contract/fund/models_solidarity.py` | `fund/solidarity/models.py` |
| `payroll/contribution/services_solidarity_fund.py` | `fund/solidarity/services.py` |

## irpef

| Today | Target |
|---|---|
| `payroll/taxation/services_tax_computation.py` | `irpef/computation/services.py` |
| `payroll/taxation/inputs_prior_year.py` | `irpef/declaration/inputs.py` |
| `payroll/taxation/rules_irpef_deduction.py` | `irpef/deduction/rules.py` |
| `payroll/taxation/rules_irpef_minimum.py` | `irpef/minimum/rules.py` |
| `tax/income/models.py` | `irpef/models.py` |
| `payroll/taxation/rules_irpef_net.py` | `irpef/net/rules.py` |
| `payroll/taxation/inputs_current_year.py` | `irpef/other_income/inputs.py` |
| `payroll/taxation/results.py` | `irpef/results.py` |
| `payroll/taxation/rules_irpef.py` | `irpef/rules.py` |
| `payroll/taxation/rules_separate_tax.py` | `irpef/separate/rules.py` |
| `payroll/taxation/services_irpef.py` | `irpef/services.py` |
| `payroll/taxation/services_taxable.py` | `irpef/taxable/services.py` |
| `payroll/taxation/results_irpef_trace.py` | `irpef/trace/results.py` |

## knowledge

| Today | Target |
|---|---|
| `knowledge/facade.py` | `knowledge/facade.py` |
| `knowledge/loaders.py` | `knowledge/loaders.py` |
| `knowledge/loaders_manifest.py` | `knowledge/loaders.py` |
| `knowledge/loaders_resource.py` | `knowledge/loaders.py` |
| `tax/annual/loaders.py` | `knowledge/sector/loaders.py` |
| `tax/annual/loaders_resource.py` | `knowledge/sector/loaders.py` |
| `tax/annual/models.py` | `knowledge/sector/models.py` |
| `knowledge/validators.py` | `knowledge/validators.py` |

## ledger

| Today | Target |
|---|---|
| `payroll/ledger/services_base_line.py` | `ledger/line/services.py` |
| `payroll/ledger/services_line.py` | `ledger/line/services.py` |
| `payroll/ledger/services_tax_line.py` | `ledger/line/tax/services.py` |
| `payroll/ledger/models.py` | `ledger/models.py` |
| `payroll/ledger/services_posting.py` | `ledger/posting/services.py` |
| `payroll/ledger/models_remittance.py` | `ledger/remittance/models.py` |
| `payroll/ledger/services.py` | `ledger/services.py` |

## limitation

| Today | Target |
|---|---|
| `knowledge/limitation/loaders.py` | `limitation/loaders.py` |
| `knowledge/limitation/models.py` | `limitation/models.py` |
| `payroll/assurance/services_limitation.py` | `limitation/services.py` |

## pay_item

| Today | Target |
|---|---|
| `payroll/amount/facade.py` | `pay_item/facade.py` |
| `payroll/amount/loaders_policy.py` | `pay_item/loaders.py` |
| `payroll/amount/models_pay_item.py` | `pay_item/models.py` |
| `payroll/amount/policies.py` | `pay_item/policies.py` |
| `payroll/amount/policies_rounding.py` | `pay_item/rounding/policies.py` |
| `payroll/amount/policies_pay_item.py` | `pay_item/selection/policies.py` |
| `payroll/amount/models_treatment.py` | `pay_item/treatment/models.py` |
| `payroll/amount/types_treatment.py` | `pay_item/treatment/types.py` |

## pension_fund

| Today | Target |
|---|---|
| `payroll/employment/services_seniority_conversion.py` | `pension_fund/conversion/services.py` |
| `payroll/contribution/services_pension_decision.py` | `pension_fund/decision/services.py` |
| `payroll/contribution/rules_pension_fund_lookup.py` | `pension_fund/enrolment/rules.py` |
| `payroll/contribution/inputs_pension_fund.py` | `pension_fund/inputs.py` |
| `tax/pension/models.py` | `pension_fund/models.py` |
| `payroll/contribution/rules_pension_fund.py` | `pension_fund/rules.py` |
| `payroll/contribution/services_pension.py` | `pension_fund/services.py` |

## period

| Today | Target |
|---|---|
| `payroll/amount/services.py` | `period/amount/services.py` |
| `payroll/amount/types.py` | `period/amount/types.py` |
| `payroll/period/services_contract.py` | `period/context/agreement/services.py` |
| `payroll/period/services_context.py` | `period/context/fact/services.py` |
| `payroll/period/services_context_fact.py` | `period/context/fact/services.py` |
| `payroll/period/services_run_context.py` | `period/context/services.py` |
| `payroll/period/services_caller_rule.py` | `period/decision/override/services.py` |
| `payroll/period/rules_run_decision.py` | `period/decision/rules.py` |
| `payroll/period/services_base_decision.py` | `period/decision/services.py` |
| `payroll/period/inputs.py` | `period/inputs.py` |
| `payroll/period/models_payroll.py` | `period/models.py` |
| `payroll/period/ports.py` | `period/ports.py` |
| `payroll/period/services_posting.py` | `period/posting/services.py` |
| `payroll/period/repositories.py` | `period/repositories.py` |
| `payroll/period/services_facade_input.py` | `period/request/validators.py` |
| `payroll/period/requests.py` | `period/requests.py` |
| `payroll/period/services_assembly.py` | `period/result/services.py` |
| `payroll/period/results.py` | `period/results.py` |
| `payroll/period/services.py` | `period/services.py` |
| `payroll/period/services_shared.py` | `period/services.py` |
| `payroll/period/services_sources.py` | `period/services.py` |
| `payroll/period/services_pipeline_input.py` | `period/step/input/services.py` |
| `payroll/period/services_pipeline.py` | `period/step/services.py` |
| `payroll/period/services_check.py` | `period/validators.py` |
| `payroll/period/validators_request.py` | `period/validators.py` |

## provenance

| Today | Target |
|---|---|
| `provenance/ruleset/models_assurance.py` | `provenance/ruleset/assurance/models.py` |
| `provenance/ruleset/models.py` | `provenance/ruleset/models.py` |
| `provenance/source/models_extraction.py` | `provenance/source/extraction/models.py` |
| `provenance/source/models.py` | `provenance/source/models.py` |
| `provenance/source/models_chain.py` | `provenance/source/rule/models.py` |

## reconciliation

| Today | Target |
|---|---|
| `payroll/assurance/validators_untaxed.py` | `reconciliation/agent/validators.py` |
| `payroll/assurance/validators_attribution.py` | `reconciliation/attribution/validators.py` |
| `payroll/assurance/validators_withholding.py` | `reconciliation/ceiling/validators.py` |
| `payroll/assurance/validators_decision.py` | `reconciliation/decision/validators.py` |
| `payroll/assurance/validators_ledger.py` | `reconciliation/ledger/validators.py` |
| `payroll/assurance/validators_lifecycle.py` | `reconciliation/lifecycle/validators.py` |
| `payroll/assurance/validators_remittance.py` | `reconciliation/remittance/validators.py` |
| `payroll/assurance/validators_sign.py` | `reconciliation/sign/validators.py` |
| `payroll/assurance/validators_state.py` | `reconciliation/transition/validators.py` |
| `payroll/assurance/types.py` | `reconciliation/types.py` |
| `payroll/assurance/validators.py` | `reconciliation/validators.py` |

## regime

| Today | Target |
|---|---|
| `payroll/taxation/rules_regime_eligibility.py` | `regime/eligibility/rules.py` |
| `payroll/event/handlers_preferential_regime.py` | `regime/handlers.py` |
| `tax/regime/models.py` | `regime/models.py` |
| `payroll/taxation/rules_regime_requirement.py` | `regime/requirement/rules.py` |

## run

| Today | Target |
|---|---|
| `payroll/period/models_run.py` | `run/models.py` |
| `payroll/period/types_run_kind.py` | `run/types.py` |

## seniority

| Today | Target |
|---|---|
| `payroll/employment/inputs_seniority.py` | `seniority/inputs.py` |
| `payroll/employment/rules_seniority_tier.py` | `seniority/ladder/rules.py` |
| `contract/seniority/models.py` | `seniority/models.py` |
| `payroll/employment/rules_seniority.py` | `seniority/rules.py` |
| `payroll/employment/services_seniority.py` | `seniority/services.py` |

## severance

| Today | Target |
|---|---|
| `tax/severance/models.py` | `severance/models.py` |
| `payroll/termination/models_tfr_fund.py` | `severance/provision/models.py` |
| `payroll/termination/services_tfr_destination.py` | `severance/provision/services.py` |
| `payroll/termination/services_public_tfr_reduction.py` | `severance/public/services.py` |
| `payroll/contribution/services_tfr_compensation.py` | `severance/relief/services.py` |
| `tax/severance/models_revaluation.py` | `severance/revaluation/models.py` |
| `payroll/termination/services_tfr_revaluation.py` | `severance/revaluation/services.py` |
| `payroll/termination/services_tfr_rule.py` | `severance/services.py` |

## sickness

| Today | Target |
|---|---|
| `payroll/sickness/handlers_cumulation.py` | `sickness/cumulation/handlers.py` |
| `payroll/sickness/results_cumulation.py` | `sickness/cumulation/results.py` |
| `payroll/sickness/rules_cumulation.py` | `sickness/cumulation/rules.py` |
| `payroll/sickness/rules_year.py` | `sickness/cumulation/year/rules.py` |
| `payroll/sickness/models_pay_rule.py` | `sickness/day/models.py` |
| `payroll/sickness/rules_day.py` | `sickness/day/rules.py` |
| `payroll/sickness/handlers.py` | `sickness/handlers.py` |
| `tax/annual/loaders_optional.py` | `sickness/indemnity/loaders.py` + `variable_pay/loaders.py` + `family/loaders.py` + `severance/loaders.py` + `tax_credit/somma_esente/loaders.py` |
| `tax/sickness/models.py` | `sickness/indemnity/models.py` |
| `contract/sickness/models.py` | `sickness/integration/models.py` |
| `payroll/sickness/handlers_issues.py` | `sickness/issue/handlers.py` |
| `payroll/sickness/models.py` | `sickness/models.py` |
| `payroll/sickness/validators_month.py` | `sickness/month/validators.py` |
| `payroll/sickness/handlers_pay.py` | `sickness/pay/handlers.py` |
| `payroll/sickness/services.py` | `sickness/services.py` |
| `payroll/sickness/rules_terms.py` | `sickness/term/rules.py` |

## surtax

| Today | Target |
|---|---|
| `payroll/taxation/rules_surtax_conguaglio.py` | `surtax/conguaglio/rules.py` |
| `payroll/taxation/types_jurisdiction.py` | `surtax/jurisdiction/types.py` |
| `tax/surtax/loaders.py` | `surtax/loaders.py` |
| `tax/surtax/models.py` | `surtax/models.py` |
| `payroll/state/models_surtax_obligation.py` | `surtax/obligation/models.py` |
| `payroll/taxation/rules_surtax_residence.py` | `surtax/residence/rules.py` |
| `payroll/taxation/rules_surtax.py` | `surtax/rules.py` |
| `payroll/taxation/rules_surtax_stage.py` | `surtax/stage/rules.py` |
| `tax/surtax/models_table.py` | `surtax/table/models.py` |
| `payroll/taxation/rules_surtax_table.py` | `surtax/table/rules.py` |

## tax_credit

| Today | Target |
|---|---|
| `payroll/state/models_credit_account.py` | `tax_credit/account/models.py` |
| `payroll/taxation/rules_credit_decision.py` | `tax_credit/decision/rules.py` |
| `payroll/taxation/inputs_foreign_tax.py` | `tax_credit/foreign/inputs.py` |
| `payroll/taxation/rules_foreign_tax_credit.py` | `tax_credit/foreign/rules.py` |
| `tax/income/models_credit.py` | `tax_credit/models.py` |
| `payroll/withholding/models_recovery_plan.py` | `tax_credit/recovery/models.py` |
| `payroll/withholding/services_carried_recovery.py` | `tax_credit/recovery/services.py` |
| `payroll/taxation/rules_irpef_credit.py` | `tax_credit/rules.py` |
| `payroll/withholding/services_somma_esente_posting.py` | `tax_credit/somma_esente/posting/services.py` |
| `payroll/withholding/services_somma_esente.py` | `tax_credit/somma_esente/services.py` |
| `payroll/withholding/services_somma_esente_settlement.py` | `tax_credit/somma_esente/settlement/services.py` |
| `payroll/taxation/rules_trattamento_credit.py` | `tax_credit/trattamento_integrativo/rules.py` |
| `payroll/taxation/rules_ulteriore_plan.py` | `tax_credit/ulteriore_detrazione/plan/rules.py` |
| `payroll/taxation/rules_ulteriore_recovery.py` | `tax_credit/ulteriore_detrazione/recovery/rules.py` |
| `payroll/taxation/rules_ulteriore_settlement.py` | `tax_credit/ulteriore_detrazione/rules.py` |

## termination

| Today | Target |
|---|---|
| `payroll/termination/handlers.py` | `termination/handlers.py` |
| `payroll/event/inputs_termination.py` | `termination/inputs.py` |

## variable_pay

| Today | Target |
|---|---|
| `payroll/event/handlers_variable_pay.py` | `variable_pay/arrears/handlers.py` |
| `payroll/event/handlers_benefit.py` | `variable_pay/benefit/handlers.py` |
| `payroll/event/results_benefit.py` | `variable_pay/benefit/results.py` |
| `payroll/event/inputs_variable_pay.py` | `variable_pay/inputs.py` |
| `tax/regime/models_variable_pay.py` | `variable_pay/models.py` |

## withholding

| Today | Target |
|---|---|
| `payroll/withholding/rules_agent.py` | `withholding/agent/rules.py` |
| `payroll/withholding/services_untaxed.py` | `withholding/agent/services.py` |
| `payroll/withholding/services_cap.py` | `withholding/cap/services.py` |
| `payroll/withholding/inputs_shortfall_deferral.py` | `withholding/deferral/inputs.py` |
| `payroll/withholding/services_deferral_line.py` | `withholding/deferral/posting/services.py` |
| `payroll/withholding/services_deferral.py` | `withholding/deferral/services.py` |
| `payroll/withholding/services_plan.py` | `withholding/plan/services.py` |
| `payroll/withholding/rules_law.py` | `withholding/rules.py` |
| `payroll/withholding/rules_period.py` | `withholding/rules.py` |
| `payroll/withholding/models_schedule.py` | `withholding/schedule/models.py` |

## working_time

| Today | Target |
|---|---|
| `payroll/event/handlers_work_time.py` | `working_time/handlers.py` |
| `payroll/event/inputs_work_time.py` | `working_time/inputs.py` |
| `contract/working_time/models.py` | `working_time/models.py` |
| `payroll/event/policies_overtime_rate.py` | `working_time/overtime/policies.py` |

## year

| Today | Target |
|---|---|
| `payroll/year/inputs_calendar_override.py` | `year/calendar/inputs.py` |
| `payroll/year/models_calendar.py` | `year/calendar/models.py` |
| `payroll/year/services_calendar.py` | `year/calendar/services.py` |
| `payroll/year/inputs_competence_plan.py` | `year/competence/inputs.py` |
| `payroll/year/services_run.py` | `year/competence/run/services.py` |
| `payroll/year/services_competence.py` | `year/competence/services.py` |
| `payroll/year/models_uncovered_run.py` | `year/coverage/models.py` |
| `payroll/year/services_coverage.py` | `year/coverage/services.py` |
| `payroll/year/models_payment.py` | `year/payment/models.py` |
| `payroll/year/services_sequence.py` | `year/payment/sequence/services.py` |
| `payroll/year/services_payment.py` | `year/payment/services.py` |
| `payroll/year/results.py` | `year/results.py` |
| `payroll/year/models_schedule.py` | `year/schedule/models.py` |
| `payroll/year/inputs_tax_plan.py` | `year/tax_year/inputs.py` |
| `payroll/year/rules_close.py` | `year/tax_year/rules.py` |
| `payroll/year/rules_tax_year.py` | `year/tax_year/rules.py` |
| `payroll/year/services_tax_year.py` | `year/tax_year/services.py` |
