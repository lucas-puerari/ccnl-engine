# Ruleset readiness

`readiness` is a three-tier classification on each CCNL ruleset that answers
one question: *for what use context is this ruleset cleared?*

It is separate from `verification.confidence` (which measures how verified
individual data values are) and from the coverage percentage (which measures
how many engine features are implemented). A ruleset can score 100% coverage
while remaining `exploratory` because all values were extracted by an automated
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
2. At least one reference case must exist in `tests/integration/cases/`
   sourced from a real payslip (anonymised) or an official regulatory example,
   not a synthetic scenario.
3. A named owner must be recorded in `verification.human_reviewed_by`.
4. An update-policy entry must exist: who monitors CCNL renewals, and within
   what target window the ruleset is updated after a renewal.
5. Set `verification.readiness = "production"` in the CCNL JSON.

## Current status

The current readiness distribution across the 125 bundled rulesets is visible
in the [CCNL coverage matrix](../contracts/index.md) under the Readiness column.

As of the initial introduction of this field (September 2026), all rulesets
default to `exploratory`. The target is to bring the 15 most-used CCNLs
(by covered worker population) to `reviewed` status, with at least 5 reaching
`production`.

## Relationship to the result status

`result.status` is a result-level signal derived at compute time from the
issues of the run. `readiness` is a ruleset-level classification set by a
human reviewer. They answer different questions:

| Question | Field |
|---|---|
| Did this computation rest on known rules and facts? | `result.status` and `result.issues` |
| Is this ruleset cleared for production use? | `ccnl.verification.readiness` |
| Were the individual values checked against the source? | `ccnl.verification.confidence` |

A result can be `final` while the ruleset is still `readiness =
"exploratory"`: the status says every rule the run needed was known and
applied, not that a person checked the values against the source.
