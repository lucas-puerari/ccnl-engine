# `ccnl_engine.catalog`

What the engine covers before any run: the bundled contracts and their
discovery, ruleset identity and readiness, the capability catalog. See
[Find a CCNL and its level](../getting-started/index.md#find-a-ccnl-and-its-level).

## Contracts and rulesets

Before any run, `engine.list_contracts()` returns one `ContractSummary`
(`ccnl_id`, `name`, `cnel_code`, `family`, `readiness`, `validity`) per CCNL of
the repository and
`engine.inspect_ruleset(ccnl_id)` returns the `RulesetAssurance` of one CCNL,
by slug or CNEL code: the same value the run reports in `result.rulesets`.

```python
engine = PayrollEngine.bundled(mode="operational")
ruleset = engine.inspect_ruleset("commercio-confcommercio")
if not ruleset.is_production:
    print(ruleset.readiness, ruleset.confidence)  # the run of this CCNL is blocked
```

| `RulesetAssurance` field | Meaning |
|---|---|
| `identity` | `RulesetIdentity`: id, version, validity, source and `source_hash` |
| `kind` | `RulesetKind`: `ccnl`, `tax`, `inps` or `surtax`, set by the loader |
| `readiness` | `RulesetReadiness` for a CCNL; `None` when the kind tracks no tier |
| `confidence` | `VerificationStatus`: the CCNL `verification.confidence`, or the identity `verification_status` |
| `confidence_contradicts_readiness` | `True` when a `reviewed` or `production` tier lacks a `verified` confidence |
| `is_production` | `production` and a confidence that agrees |
| `review_due` | Day the next review of a CCNL is due (`verification.review_due`); `None` for the other kinds |
| `review_overdue(day)` | `True` when `review_due` is before `day`; an `operational` run paid after it is blocked |
| `axes` | `AssuranceAxes` of a CCNL (`source_checked`, `externally_compared`, `human_signed_off`); `None` for the other kinds |

`ContractSummary.validity` is the `ValidityWindow` (`first_day`,
`last_day`, both included, `last_day` `None` when open-ended) on which every
rule of the CCNL has a value in the bundle: pay tables, parameters and work
rules. A run whose month it covers never raises `MissingRuleError`; a run
outside it raises that error when it reads a rule not in force on its date.
Four CCNLs have 2026 pay tables that start after January (`anas` on 1 March,
`igiene-ambientale-utilitalia` on 1 February,
`lavanderie-industriali-assosistema` on 1 May, `metalmeccanico-confimi-pmi`
on 1 June): a competence or tax year of theirs from January is partial (see
[Results](ccnl_engine.md#results)).

```python
(anas,) = (c for c in engine.list_contracts() if c.ccnl_id == "anas")
anas.validity.first_day  # → datetime.date(2026, 3, 1)
```

## Contract families

Every CCNL names its contract family in `meta.family`, an id of the central
catalog that `list_families()` returns (`ContractFamily`: `id`, `name`,
`description`, `criteria` and the work groups G01-G17 of the roadmap). The
family groups the CCNLs of one productive sector across employer size,
legal form and signatories (`metalmeccanica` holds the industrial, small
industry, cooperative and craft metalworking CCNLs); it selects no rule and
is independent of `tax_sector` and of the CNEL code.
`engine.list_contracts(family=...)` and `search_ccnls(query, family=...)`
keep the CCNLs of one family, in the bundle and in a custom repository
alike; an id the catalog does not hold raises `InvalidInputError`.

```python
for family in list_families():
    print(family.id, family.name)
engine.list_contracts(family="edilizia")  # the five construction CCNLs
```

::: ccnl_engine.catalog.ContractFamily

::: ccnl_engine.catalog.FamilyAssignment

::: ccnl_engine.catalog.list_families

::: ccnl_engine.catalog.CapabilityCatalog

::: ccnl_engine.catalog.CapabilityEntry

::: ccnl_engine.catalog.CapabilityImplementation

::: ccnl_engine.catalog.CcnlId

::: ccnl_engine.catalog.ContractSummary

::: ccnl_engine.catalog.LevelSummary

::: ccnl_engine.catalog.RulesetAssurance

::: ccnl_engine.catalog.AssuranceAxes

::: ccnl_engine.catalog.RulesetIdentity

::: ccnl_engine.catalog.RulesetKind

::: ccnl_engine.catalog.RulesetReadiness

::: ccnl_engine.catalog.ValidityWindow

::: ccnl_engine.catalog.VerificationStatus

::: ccnl_engine.catalog.get_ccnl

::: ccnl_engine.catalog.search_ccnls

::: ccnl_engine.catalog.supported_tax_years

## Places and sources

`regions(year)` and `municipalities(year)` list the codes a run states in
`PeriodFacts.regione` and `PeriodFacts.comune_belfiore`, with their names;
`ContractSummary.sources` lists the documents a CCNL file cites and
`ContractSummary.withholding_agent` whether its employer withholds IRPEF;
`LevelSummary.apprenticeship_tracks` names the tracks that lead to a level.

::: ccnl_engine.catalog.regions

::: ccnl_engine.catalog.municipalities

::: ccnl_engine.catalog.Jurisdiction

::: ccnl_engine.catalog.SourceDocument

