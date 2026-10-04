# Ruleset readiness

`readiness` is a three-tier classification on each CCNL ruleset that answers
one question: *for what use context is this ruleset cleared?*

It is separate from `verification.confidence` (which measures how verified
individual data values are) and from functional coverage (which capabilities
of the [capability registry](../contracts/capability-matrix.md) the engine
computes). A ruleset can have every capability it needs covered while
remaining `exploratory` because all values were extracted by an automated
tool and no human has checked them.

## The three tiers

### `exploratory` 🧪

The ruleset has been extracted and traced to a source, but no human has
verified the key salary-table values against the primary document.

**Safe for:** demos, research, prototyping, internal tooling where figures are
clearly labelled as unverified estimates.

**Not safe for:** any interface that shows a net salary to an end user as if
it were authoritative; any decision that relies on the figure being correct.

### `reviewed` 👁

At least the L1 values (base salary per level, seniority table, additional
months, hourly divisor) have been cross-checked by a person against the
primary CCNL document, and the source URL is recorded in the JSON.

**Safe for:** product simulations with an explicit disclaimer that names the
verification scope and date; workforce-planning and offer-modelling tools.

**Not safe for:** operational flows that present figures without a disclaimer;
any context where the user cannot see the readiness tier.

### `production` 🏭

Full review: all L1 and L2 values verified, at least one reference case from
an independent source (official payslip or regulatory document, anonymised),
a named owner assigned, and an entry in the update policy.

**Safe for:** operational flows where figures are shown to end users or used
in decisions; integration into HR tools that do not add their own disclaimer.

## Promotion criteria

### `exploratory` → `reviewed`

A human reviewer must:

1. Open the primary CCNL source document (URL recorded in `meta.sources`).
2. Confirm every base salary amount for each level against the table in the
   document.
3. Confirm the seniority table amounts and cadence.
4. Confirm `additional_months`, `hourly_divisor`, and any fixed allowances.
5. Record `verification.last_reviewed`, `verification.human_reviewed_by`, and
   set `verification.confidence = "verified"` on the verified fields.
6. Set `verification.readiness = "reviewed"` in the CCNL JSON.

### `reviewed` → `production`

In addition to the `reviewed` criteria:

1. All L2 values (INPS sector, apprenticeship rules, TFR) must be verified
   against primary sources.
2. At least one reference case must exist in `tests/fixtures/expected/`
   sourced from a real payslip (anonymised) or an official regulatory example,
   not a synthetic scenario.
3. A named owner must be recorded in `verification.owner`, and the reviewer
   in `verification.human_reviewed_by`.
4. An update-policy entry must exist: who monitors CCNL renewals, and within
   what target window the ruleset is updated after a renewal. Record the
   date the next review is due in `verification.review_due`, after
   `verification.last_reviewed`.
5. Set `verification.readiness = "production"` in the CCNL JSON.

The schema gate (`scripts/ci/check_provenance.py --schema`) rejects a
`production` ruleset without these fields or without `confidence` `verified`.

## Current status

Distribution across the
<!-- trust:ccnl-total -->125<!-- /trust:ccnl-total --> bundled CCNL rulesets,
generated from the data by `scripts/docs/gen_trust_counts.py` (CI fails when
it drifts):

<!-- trust:readiness-table -->

| Readiness | CCNL rulesets |
|---|---:|
| `exploratory` | 110 |
| `reviewed` | 15 |
| `production` | 0 |

<!-- /trust:readiness-table -->

The <!-- trust:readiness-reviewed -->15<!-- /trust:readiness-reviewed -->
`reviewed` rulesets: <!-- trust:readiness-reviewed-list -->`commercio-confcommercio`, `cooperative-sociali`, `dmo-federdistribuzione`, `edilizia-ance`, `edilizia-artigianato-cna`, `funzioni-locali-aran`, `istruzione-ricerca-aran`, `lavoro-domestico-convivente`, `lavoro-domestico-non-convivente`, `logistica-trasporto-confetra`, `metalmeccanico-artigianato`, `metalmeccanico-federmeccanica`, `multiservizi-anip`, `operai-agricoli-florovivaisti`, `sanita-aran`<!-- /trust:readiness-reviewed-list -->.
Each [contract page](../contracts/index.md) shows its own tier.

`reviewed` records a file-level review, not a per-value one. Of the `reviewed`
rulesets, <!-- trust:reviewed-with-reviewer -->15<!-- /trust:reviewed-with-reviewer -->
record `verification.human_reviewed_by` and `verification.last_reviewed`, and
<!-- trust:reviewed-confidence-verified -->0<!-- /trust:reviewed-confidence-verified -->
set `verification.confidence = "verified"` (step 5 of the criteria above).
A per-value review is recorded only by the provenance status `verified` of a
payable rule, and <!-- trust:rules-verified -->0<!-- /trust:rules-verified -->
payable rules of the bundle have it (see
[Provenance](provenance.md#provenance-status)).

## Readiness in the public API

Readiness is part of the public contract, before and after a run:

| Question | Field |
|---|---|
| Which contracts exist, and how far is each cleared? | `engine.list_contracts()`: `ContractSummary.readiness` |
| What exactly is the ruleset of one CCNL? | `engine.inspect_ruleset(ccnl_id)`: `RulesetAssurance` (identity, `source_hash`, `readiness`, `confidence`) |
| Which rulesets did this result read? | `result.rulesets`, one `RulesetAssurance` each |
| Can the amounts of this computation be paid as computed? | `result.is_payable` and `result.blockers` |

Only CCNL rulesets carry a tier. Tax, INPS and surtax rulesets report
`readiness = None` (not tracked) and the `verification_status` of their
identity as `confidence`; their evidence is the provenance of each rule (see
[Provenance](provenance.md#provenance-status)).

`RulesetAssurance.confidence_contradicts_readiness` is `True` when a
`reviewed` or `production` tier is not backed by
`verification.confidence = "verified"` (step 5 of the criteria above). Of the
<!-- trust:readiness-reviewed -->15<!-- /trust:readiness-reviewed --> `reviewed`
rulesets, <!-- trust:reviewed-confidence-verified -->0<!-- /trust:reviewed-confidence-verified -->
record a `verified` confidence; the flag is `True` for all the others. `RulesetAssurance.is_production` requires both the
`production` tier and a confidence that agrees.

## Simulation and operational modes

`PayrollEngine.bundled(mode=...)` chooses how readiness acts on payability.
Both modes compute the same amounts.

| Mode | Readiness |
|---|---|
| `simulation` (default) | Reported in `result.rulesets`, not enforced. A result can be payable while its CCNL is `exploratory`: payability says every rule the run needed was known, sourced and applied, not that a person checked the values. |
| `operational` | Enforced: each ruleset that tracks a tier and is not `is_production` adds a `ruleset_not_production` blocker naming its id. A run whose CCNL has no ruleset identity fails closed. |

An operational engine returns the result with its blockers instead of
refusing before the calculation, so the amounts and every other blocker stay
inspectable. With <!-- trust:readiness-production -->0<!-- /trust:readiness-production -->
`production` rulesets, no bundled CCNL is payable in operational mode: the
gate opens one CCNL at a time, as each is promoted.
