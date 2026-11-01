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

The ruleset has been extracted and traced to a source, but no recorded
review has cleared the key salary-table values against the primary document.

**Safe for:** demos, research, prototyping, internal tooling where figures are
clearly labelled as unverified estimates.

**Not safe for:** any interface that shows a net salary to an end user as if
it were authoritative; any decision that relies on the figure being correct.

### `reviewed` 👁

At least the L1 values (base salary per level, seniority table, additional
months, hourly divisor) have been cross-checked against the primary CCNL
document by a recorded review (an AI review today, see
[What a review records](#what-a-review-records)), and the source URL is
recorded in the JSON.

The tier also requires `verification.confidence = "verified"` and no
`assumed` or `missing` payable rule in the CCNL file (salary tables,
allowances, seniority, extra months and their accrual, overtime, absence and
sickness rules, employer funds): a review cannot clear a value no source
backs.

**Safe for:** product simulations with an explicit disclaimer that names the
verification scope and date; workforce-planning and offer-modelling tools.

**Not safe for:** operational flows that present figures without a disclaimer;
any context where the user cannot see the readiness tier.

### `production` 🏭

Full review: all L1 and L2 values verified, at least one `verified`
reference case from an independent source (official payslip or regulatory
document, anonymised), an owner role assigned, and a review date.

**Safe for:** operational flows that gate payment on `is_payable` and show
the readiness and review date next to the figures; a second opinion next to
a payroll provider's own calculation.

**Not certified:** production does not mean a person signed the values (the
reviews are AI reviews), nor that every total was matched against an
independent provider output (see criterion 3 below: today none is). Keep
your own disclaimer and verify the amounts before paying them.

## Promotion criteria

### `exploratory` → `reviewed`

A reviewer, a person or an AI model, must:

1. Open the primary CCNL source document (URL recorded in `meta.sources`).
2. Confirm every base salary amount for each level against the table in the
   document.
3. Confirm the seniority table amounts and cadence.
4. Confirm `additional_months`, `hourly_divisor`, and any fixed allowances.
5. Append an entry to the [review log](#review-log), mark each checked value
   `verified` with the `review_id` of that entry, and set
   `verification.confidence = "verified"`.
6. Source every `assumed` or `missing` payable rule of the CCNL file: each
   must be `derived` or `verified` (see
   [Provenance](provenance.md#a-label-never-outruns-its-evidence)).
7. Record the owner in `verification.owner` and the date the next review is
   due in `verification.review_due`, after the date of the last entry of the
   review log: a `reviewed` CCNL is a candidate for `production`, so it is
   monitored from the start (see the [Review plan](review-plan.md)).
8. Set `verification.readiness = "reviewed"` in the CCNL JSON.

### `reviewed` → `production`

In addition to the `reviewed` criteria:

1. All L2 values (INPS sector, apprenticeship rules, TFR) must be verified
   against primary sources.
2. At least one reference case must exist in `tests/knowledge/ccnl_engine/period/reference_case/`
   sourced from a real payslip (anonymised) or an official regulatory example,
   not a synthetic scenario: a `verified` case (see
   [Reference case verification status](index.md#reference-case-verification-status)).
   The schema gate of `scripts/provenance/check.py` enforces it: a
   `production` CCNL without a valid reference case fails, and so does one
   without a `verified` case. No CCNL is exempt: the nine CCNLs promoted
   before the rule, whose cases were only `source_linked`, went back to
   `reviewed` on 24 October 2026, so `operational` mode no longer pays
   them, until an independent output backs each one. Turismo Federalberghi
   and Pubblici Esercizi FIPE returned to `production` the same day, each
   with a `verified` case from a real 2026 payslip (p72, p73) whose
   full-time paga base the engine matches to the cent.
   `python scripts/provenance/check.py --index` prints the cases of each CCNL
   with its readiness, status and axes.
3. Its evidence must cover every complete output of the definition of done
   for operational use (base salary, gross, employee contributions,
   employer contributions, tax, net pay, TFR, employer cost) in the
   `Totals` column of the [Validation matrix](validation-matrix.md).
   Contributions are two outputs, not one: their bases and roundings can
   diverge on the two sides. A component (fixed allowances, a taxable
   base, a tax credit) or a rate (an INPS rate, the hourly percentages)
   is listed in its own column and never covers the total it belongs to.
   The schema gate reads explicit `(CCNL, output, independence)` pairs at
   two levels: any evidence, and a `provider output`, the only evidence
   independent of the sources the bundle was read from (a hand oracle
   recomputes the same sources). It fails a `production` CCNL that misses
   an output, at either level, that
   `scripts/provenance/readiness/baseline.json` does not list for it. The
   list holds what each `production` CCNL still misses and only shrinks:
   `scripts/quality/baseline/check.py` fails a pull request that adds an
   entry unless its body justifies it with an `allow-growth:` line;
   today no `production` CCNL covers every total with a provider output.
4. An owner must be recorded in `verification.owner`, and the review in the
   [review log](#review-log).
5. An update-policy entry must exist: who monitors CCNL renewals, and within
   what target window the ruleset is updated after a renewal. Record the
   date the next review is due in `verification.review_due`, after the date
   of the last entry of the review log.
6. Set `verification.readiness = "production"` in the CCNL JSON.

### Review log

`verification.reviews` lists the reviews of a CCNL file, oldest first. An
entry is appended for each review and never rewritten, so the file keeps its
whole history. A person and an AI model record a review with the same
fields:

| Field | Content |
|---|---|
| `id` | Identifier of the entry, unique in the file |
| `date` | Day of the review |
| `reviewer` | Role of the person (`maintainer`), or identifier of the model |
| `reviewer_kind` | `human` or `ai` |
| `scope` | What the review checked: the whole file, or which rules |
| `independence` | `same_process` (the run that extracted the values), `separate_session`, `separate_model` or `human` |
| `checked` | The fields or values compared with the sources, e.g. `levels[C3].base_salary 2026-06-01` |
| `outcome` | `confirmed`, `corrected`, `flagged` (values left to re-check) or `demoted` |
| `sources` | URL and sha256 of each document the review read |
| `findings` | The differences the review found, or notes on its scope |
| `divergences` | Each difference from an independent output (a payslip, an official cost table), closed by a decision |

A divergence never stays open. Its `decision` is one of:

| Decision | Meaning | Required |
|---|---|---|
| `engine_bug` | The engine was wrong and is fixed | `evidence` names the regression test |
| `source_context_missing` | The output omits a fact the comparison needs | `limitation` names a limitation of the file that blocks the runs concerned |
| `accepted_external_variance` | The difference is explained and kept | `review_by`, the date it is looked at again |
| `external_artifact_error` | The output is incoherent for the case compared (another year, another scope) and is no evidence | `evidence` names the document read |

Each divergence also states its `subject` (both values) and `cause`. The
owner of the ruleset answers for it. A file whose divergence names a
limitation it does not declare does not load. An unexplained difference is
never evidence of correctness: until it is closed it is a finding of a
`flagged` review, not a match.

Each value the review checked is `verified` and points to the entry with
`extraction.review_id`. An AI review is cleared by the owner when the pull
request that records it is merged; the log does not repeat it. Each
[contract page](../contracts/index.md) renders its log as a review history.

The INPS rates of a sector are verified against a table of the year when one
exists. Where none exists, the owner accepted on 2026-10-10 a reconstruction
by component from a table of the year of a sibling sector and the statutes of
the components that differ: the INPS rates of the industria in genere for
2026 are built from the 2026 table of the industria edile (Assimpredil ANCE)
and the CIGO and CIGS of D.Lgs. 148/2015 arts. 13 and 23.
The INPS rates of the artigianato for 2026 are built the same way from the
same table and the exemptions of L. 388/2000 art. 120 and L. 266/2005 art.
1 c. 361, but stay `derived`: the CUAF of the artigianato and the maternità
and malattia of a non-construction craft firm have no primary source of the
year.
The INPS rates of the industria edile for 2026 are verified on the same
Assimpredil ANCE table. The terziario has no table of the year: the owner
accepted on 2026-10-13 the allegato of INPS circ. 117/2022, still in force,
as the source of its components, with the FIS and CIGS of D.Lgs. 148/2015
arts. 29 and 23 in force in 2026.

The schema gate (`scripts/provenance/check.py --schema`) rejects a
`reviewed` or `production` ruleset with an `assumed` or `missing` payable
rule in its file or without `confidence` `verified`, and a `production`
ruleset without the fields above. These errors have no baseline.

### What a review records

`verified` means checked by the review process of the project, not
checked by an independent person. Today every review of the bundle is an
AI review (`reviewer_kind` `ai`, `claude-opus-5-5`), and the owner of every
ruleset is the role `maintainer`. When the run that extracted a value also
reviews it, an interpretation error shared by both survives the review;
only an output the engine did not produce (a `verified` reference case,
see the [validation matrix](validation-matrix.md)) breaks that dependency.

So that the log says how far each review stands from the extraction, every
entry of a `reviewed` or `production` CCNL dated from 24 October 2026 must
record its `sources`, the fields or values it `checked` and its
`independence`; for a `production` CCNL the independence cannot be
`same_process`. Older entries predate the fields and do not state them:
read their `scope` and `findings` instead.

## Current status

Distribution across the
<!-- trust:ccnl-total -->134<!-- /trust:ccnl-total --> bundled CCNL rulesets,
generated from the data by `scripts/documentation/trust_count/generate.py` (CI fails when
it drifts):

<!-- trust:readiness-table -->

| Readiness | CCNL rulesets |
|---|---:|
| `exploratory` | 111 |
| `reviewed` | 17 |
| `production` | 6 |

<!-- /trust:readiness-table -->

The <!-- trust:readiness-reviewed -->17<!-- /trust:readiness-reviewed -->
`reviewed` rulesets: <!-- trust:readiness-reviewed-list -->`alimentari-federalimentare`, `chimica-farmaceutica-federchimica`, `concia-unic`, `cooperative-sociali`, `dmo-federdistribuzione`, `edilizia-ance`, `funzioni-centrali-aran`, `funzioni-locali-aran`, `lavoro-domestico-convivente`, `lavoro-domestico-convivente-orario-ridotto`, `lavoro-domestico-non-convivente`, `logistica-trasporto-confetra`, `logistica-trasporto-confetra-viaggiante`, `metalmeccanico-confapi`, `sanita-aran`, `studi-professionali-confprofessioni`, `terziario-confesercenti`<!-- /trust:readiness-reviewed-list -->.
Each [contract page](../contracts/index.md) shows its own tier.

In October 2026 fifteen rulesets `reviewed` on a file-level review were
lowered to `exploratory`: each still read `assumed` or `missing` payable rules
and none recorded a `verified` confidence. Their review log keeps the
file-level review that promoted them; a ruleset returns to `reviewed` once its weak rules are sourced and its
confidence is `verified`, as the ones listed above did.

`reviewed` records a file-level review, not a per-value one. Of the `reviewed`
rulesets, <!-- trust:reviewed-with-reviewer -->17<!-- /trust:reviewed-with-reviewer -->
hold an entry in the review log, and
<!-- trust:reviewed-confidence-verified -->17<!-- /trust:reviewed-confidence-verified -->
set `verification.confidence = "verified"` (step 5 of the criteria above).
A per-value review is recorded only by the provenance status `verified` of a
payable rule, and <!-- trust:rules-verified -->2713<!-- /trust:rules-verified -->
payable rules of the bundle have it (see
[Provenance](provenance.md#provenance-status)).

## Readiness in the public API

Readiness is part of the public contract, before and after a run:

| Question | Field |
|---|---|
| Which contracts exist, and how far is each cleared? | `engine.list_contracts()`: `ContractSummary.readiness` |
| From which date does the bundle hold every rule of a CCNL? | `ContractSummary.validity` (`first_day`, `last_day`) |
| What exactly is the ruleset of one CCNL? | `engine.inspect_ruleset(ccnl_id)`: `RulesetAssurance` (identity, `source_hash`, `readiness`, `confidence`) |
| Which kinds of evidence back it, apart? | `RulesetAssurance.axes`: `AssuranceAxes` (`source_checked`, `externally_compared`, `human_signed_off`) |
| Which rulesets did this result read? | `result.rulesets`, one `RulesetAssurance` each |
| Can the amounts of this computation be paid as computed? | `result.is_payable` and `result.blockers` |

`ContractSummary.validity` and `RulesetIdentity.effective_from` answer two
questions: the first is the span the bundled tables cover, the second the
date the agreement of the ruleset takes effect. They can differ (the
agreement of a renewal is signed before its first tranche is paid), so a
caller deciding whether a date can be computed reads `validity`
(`catalog.get_ccnl(ccnl_id).validity` for one CCNL). A competence year
leaves out the runs before the base salary of the level, and before its
seniority amount when the employment states a seniority, with a
`run_not_computed` blocker each.

Only CCNL rulesets carry a tier. Tax, INPS and surtax rulesets report
`readiness = None` (not tracked) and the `verification_status` of their
identity as `confidence`; their evidence is the provenance of each rule (see
[Provenance](provenance.md#provenance-status)).

`RulesetAssurance.confidence_contradicts_readiness` is `True` when a
`reviewed` or `production` tier is not backed by
`verification.confidence = "verified"` (step 5 of the criteria above). The
schema gate rejects such a tier in the bundle, so the flag is `False` for
every bundled ruleset. `RulesetAssurance.is_production` requires both the
`production` tier and a confidence that agrees.

### Assurance axes

The tier summarises several kinds of evidence; `RulesetAssurance.axes`
keeps them apart, so a caller can tell what a tier does not say:

| Axis | True when |
|---|---|
| `source_checked` | `confidence` is `verified` and a review recorded the sources it read |
| `externally_compared` | at least one `verified` reference case compares the engine with an output it did not produce (`verification.verified_cases`, kept equal to the cases by the schema gate) |
| `human_signed_off` | a review records a person, independent of the extraction (`independence` `human`) |

That the implementation is tested is a property of the release, not of a
ruleset: the full suite, with 100% branch coverage, runs on the commit that
builds the bundle. Today no CCNL has `human_signed_off`: every review of the
bundle is an AI review. `axes` is `None` for the tax, INPS and surtax
rulesets, which track no tier.

## Simulation and operational modes

`PayrollEngine.bundled(mode=...)` chooses how readiness acts on payability.
Both modes compute the same amounts.

| Mode | Readiness |
|---|---|
| `simulation` (default) | Reported in `result.rulesets`, not enforced. A result can be payable while its CCNL is `exploratory`: payability says every rule the run needed was known, sourced and applied, not that a person checked the values. |
| `operational` | Enforced: each ruleset that tracks a tier and is not `is_production` adds a `ruleset_not_production` blocker naming its id. So does a `production` ruleset whose `verification.review_due` falls before the payment date of the run (see [Review date](#review-date-at-run-time)). A run whose CCNL has no ruleset identity fails closed. |

An operational engine returns the result with its blockers instead of
refusing before the calculation, so the amounts and every other blocker stay
inspectable. With <!-- trust:readiness-production -->6<!-- /trust:readiness-production -->
`production` rulesets, only those CCNLs are payable in operational mode: the
gate opens one CCNL at a time, as each is promoted.

### Review date at run time

A `production` tier holds until the next review is due. Each CCNL records
that day in `verification.review_due`, and `RulesetAssurance.review_due`
carries it into every run. In `operational` mode a run whose payment date is
later than `review_due` does not count the CCNL as production: it gets the
same `ruleset_not_production` blocker (detail: the ruleset id), with a
remediation that names the review date and the payment date. The due day
itself is still in time. An installed wheel therefore stops paying a CCNL
whose review lapsed, even though the deadline gate of CI and of the
release (`scripts/provenance/check.py --deadlines`) no longer runs against
it.

`RulesetAssurance.is_production` stays a property of the file, so
`inspect_ruleset` reports the tier before any run; use
`RulesetAssurance.review_overdue(day)` to check a date yourself. `simulation`
mode ignores the review date, as it ignores the tier.
