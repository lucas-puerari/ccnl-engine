# Three layers of correctness

A payroll simulation can fail at three independent levels. ccnl-engine makes each
layer explicit so you know which questions you can answer and which you cannot.

---

## Layer 1 — Software correctness

**The engine applies its modelled rules consistently.**

This is the layer the test suite proves. It means: given rule R and input I,
the engine always returns the output the rule specifies. It says nothing about
whether R is the right rule.

Evidence:

- 100% branch coverage: every branch of `src/ccnl_engine` runs in the test suite
- `mypy --strict`: the type system rules out entire classes of logic error
- Mutation testing (`mutmut`, weekly CI job): the money-moving modules
  (contributions, IRPEF and its deductions, the trattamento integrativo,
  the additional 1% IVS, the INPS minimum base, the per-run withholding,
  the ledger, rounding and the payability assessment) are mutated and the
  tests of those modules must kill at least 93% of the mutants; 805 of 855
  (94.2%) on 8 October 2026.  The survivors are mostly the trace text of
  decisions (source labels, input names).  A pull request that changes one
  of those modules runs the same campaign on the modules it changes, with
  the same minimum, so a regression cannot merge before the next weekly
  run: 218 of 227 (96.0%) on the deduction and assessment rules changed on
  15 October 2026.  Every campaign records its commit, date and modules in
  `mutants/mutation-score.json`, kept as a workflow artifact: a score
  without its perimeter and its date is not quoted.  The perimeter also
  holds the five event handlers that move money (overtime and work-time
  supplements, sick pay, travel allowances, arrears, termination funds and
  TFR).  They entered below 93%, so each keeps its own floor in
  `scripts/quality/mutation/baseline.json`, its score on 15 October 2026
  (travel 67.8%, termination 86.2%, overtime 86.8%, arrears 87.8%, sick
  pay 90.6%): a score can rise, never fall, and the floor follows it.
  Termination reached 100% on 16 October 2026 (138 of 138 mutants killed),
  once tests traced each bilateral fund and TFR settlement entry to its
  pay item and its policy; it left the baseline and now counts in the
  93% minimum of the core. Travel followed on the same day (219 of 219,
  from 67.8%): tests now cover the night allowance from 18 hours included
  and in the TFR base, the exempt and taxable parts of the item, the
  decision trace, and the errors of an amount not in force or not stated;
  two equivalent mutants were removed by dropping a default argument and a
  redundant guard. Overtime and supplements reached 98.5% (134 of 136, from
  86.8%): tests now cover the PdR income ceiling at 80,000 EUR included,
  the INPS and TFR bases a PdR above it keeps, the premium a bonus is
  withheld apart as (art. 23 c. 2 lett. b) DPR 600/1973) against a renewal
  increment and a night supplement taxed with the period, and the policy
  and band decision traced. The two survivors are equivalent: they send a
  contract renewal through the PdR ceiling, where its own regime (33,000
  EUR) already taxes it as ordinary income. Arrears reached 100% (164 of
  164, from 87.8%): tests now trace arrears of the year (ordinary IRPEF,
  INPS), of an earlier year (separate tax) and of an unknown one (separate
  tax as a simulation, with its missing fact) to their decision, item and
  policy, and the error of a year not yet begun. Sick pay reached 100%
  (159 of 159, from 90.6%): tests now cover the seniority in the daily
  quota, the units of each class of days, the INPS share INPS pays directly
  (not advanced), the carenza paid by the employer alone, a worker paid by
  the hour (no sick hours deducted) and a carenza left on a Sunday at the
  start of a month. The baseline is empty: the five handlers count in the
  93% minimum of the core.  The core twelve scored 859 of
  917 (93.7%) that day.
- Validation matrix: [Validation matrix](validation-matrix.md), generated
  in CI from the reference cases, the observed payslip replay, the sector
  oracles and the review log, crosses for each CCNL the source,
  independence, cycle, relationship, variables, thresholds, outputs,
  outcome and freshness of its evidence. Outputs are split into complete
  totals, components of a total and rates: only a compared total counts
  for readiness, so fixed allowances never stand for the gross and an
  INPS rate never for the amount of the contributions.
- Reference table cases: <!-- trust:reference-cases -->32<!-- /trust:reference-cases -->
  cases in `tests/knowledge/ccnl_engine/period/reference_case/`, each running one regular period through
  `PayrollEngine` and asserting, to the cent, the three values its cited
  salary table states: base salary, fixed allowances and period gross. They
  do not check net pay, contributions, taxes or employer cost.
  <!-- trust:reference-cases-source-linked -->30<!-- /trust:reference-cases-source-linked -->
  are `source_linked` (they cite the table they model) and
  <!-- trust:reference-cases-verified -->2<!-- /trust:reference-cases-verified -->
  are `verified` against an independent payslip or official worked example.
- Release parity: `.github/workflows/quality-gates.yml` holds every gate
  of `main` (lint, types, complexity, the generated-document drift checks,
  the full suite with 100% coverage, the API and knowledge tests on Python
  3.13 and 3.14, docs build, security scan, provenance gates, public
  snippets, and the build of the wheel and sdist smoke-tested on Python
  3.12, 3.13 and 3.14). Pull requests and the release call the same
  workflow; the release publishes the distribution it built and tested,
  and is blocked while `scripts/provenance/check.py --deadlines` finds a
  CCNL past its `review_due`, an accepted variance past its `review_by`
  or a divergence without an owner.
- Sector oracles: a year and a termination on 30 June of each contribution
  sector of the `production` CCNLs (industria: Metalmeccanico C3 with a
  weekday overtime; terziario: Terziario Confesercenti IV, fourteen
  payments; edilizia: ANCE operaio of the 1st level with the 4.95%, the
  Cassa Edile accrual and Prevedi), in
  `tests/knowledge/ccnl_engine/period/sector/`. Every payment (gross,
  worker INPS, employer contributions with the solidarity contribution on
  the pension fund, TFR accrued net of the 0.50%, employer cost) and the year
  (taxable, IRPEF, credits, surtax withheld at the termination, net cash,
  TFR, employer cost) are compared to the cent with hand oracles written
  from the cited tables and statutes, and so is the assurance: the amounts
  each CCNL owes and the engine does not compute leave the employer cost
  short, and the net pay too where they reach the worker. These oracles
  read the same primary sources as the bundle: they check the pipeline,
  not the sources, and are no independent output.
- Observed payslip replay: each of the 74 records (70 transcribed payslips, two worked examples of a
  Cassa Edile and two example payslips of a payroll package) in
  `tests/knowledge/ccnl_engine/period/observed_payslip/` states in `replay`
  whether it is `full`, `partial` or `not_replayable`, and why. A
  replayable record builds its request from the observed facts alone,
  only through the fields of the public API that
  `scripts/provenance/replay/check.py` lists (no generic override can force
  an output), and pins each value it compares with the field it was read
  from, a tolerance and, for the employer cost and the TFR, the perimeter
  of the total. A `partial` record names each fact the request cannot state
  in `unknown_inputs`, with the totals, components and rates that fact
  `affects`, and compares none of them; a `full` record has no unknown fact
  and compares every complete output, or states why one is outside its
  perimeter. The schema gate applies those rules, and the validation
  matrix credits only the records that pass them.
  `test_observed_replay.py` runs each through `PayrollEngine` and fails on
  any difference that `known_differences` does not list with its reason,
  owner and `accepted_until` date. Eleven payslips of 2026 replay in part:
  four of commercio and two of metalmeccanico (the base salary, the
  contingenza and, where the payslip prints its composition and the
  headcount is stated, the worker's INPS rate), one of industria turistica
  (the pay table), the two worked examples of an operaio edile the Cassa
  Edile di Vicenza published for January and March 2026 (the worker's INPS
  rate), and two May 2026 payslips of a Funzioni Locali employer printed
  by a payroll package (the tabellare: the individual elements and the
  TFS or TFR regime are unknown, so the indennità di comparto and the
  INPS rate are not compared). Six payslips of 2026 are `not_replayable`
  because their part-time, partial month or termination moves every
  printed value; for five of them the headcount was also inferred from the
  rate compared.
  None replays in full: superminimi, provincial elements and flat overtime
  have no field in the request. 39 are of years before the bundle's tax
  years.
- Legal scenario tests: selected rules (IRPEF, regional and municipal
  surtaxes, substitute-tax regimes, apprenticeship scaling, the withholding
  schedule and others) checked against hand-derived values, in the
  knowledge tests under `tests/knowledge/ccnl_engine/`.

Full-payslip oracles are kept apart from the reference table cases and from
the rule oracles, as `oracles_payslip_*.py` in
`tests/knowledge/ccnl_engine/period/`, and run in
`test_full_payslip_concia.py` there. The first oracle
covers the first candidate group for `production`: CCNL Concia UNIC, level
D2, a whole 2026 competence year with the industria tax and INPS rulesets,
the family deduction rules (no dependant) and the Sardegna and Alghero
surtaxes. Every expected figure is computed by
hand in plain Python from a cited source (the signed renewal and its salary
table, the TUIR, L. 207/2024, L. 199/2025, the INPS rates, the MEF surtax
tables), never from engine output: salary items, employee INPS and TFR
base of each payment, gross, INPS, taxable, IRPEF and net of the year, the
closing state, and the surtax balance and acconto left for the next year. Employer
contributions are not covered: the bundle holds them as one aggregate rate,
not as primary-sourced components. Some inputs of this oracle (the EDR, the
number of additional months, the employee IVS rate) are not read from a
fetched primary text; the fixture says which. The oracle is hand-computed,
not `verified`: no payslip issued by a payroll provider was compared.

Metamorphic tests in `tests/knowledge/ccnl_engine/period/services/test_metamorphic_concia.py`
check relations that need no expected amount: an unknown fact is not a known
zero, a bonus moves only its axes, the order of independent events and the
split of a year at an exported state change nothing, and the public totals
are the sums of the postings. A relation the engine does not meet yet is a
strict `xfail` that names the rule; none is left today.

A wrong rule shared by the engine and a hand calculation that follows the
same reading still goes undetected.

Software correctness is a necessary condition for the other layers, not a
sufficient one. A perfectly correct engine can still return a wrong number if the
rule it follows is wrong or incomplete.

---

## Layer 2 — Source correctness

**The modelled rules correspond to the current authoritative sources.**

This is the layer the readiness tier measures. It is independent of code quality:
a bug-free implementation of an outdated salary table is source-incorrect.

| Readiness | What it means for source correctness |
|---|---|
| `exploratory` | Rules extracted from sources; key values not yet checked by a person |
| `reviewed` | L1 values (base salary, seniority, additional months) human-verified against primary sources |
| `production` | All L1+L2 values verified, at least one reference case from an independent source |

Source correctness is ruleset-scoped, but today only the CCNL rulesets carry a
readiness tier: the tax, INPS and surtax files record provenance per rule and
no tier, and report `readiness = None` in `result.rulesets`. In the default
`simulation` mode the tier is reported next to `result.is_payable`, not
enforced; in `operational` mode a CCNL that is not `production` adds a
`ruleset_not_production` blocker.

Bundled CCNL rulesets at `production`:
<!-- trust:readiness-production -->12<!-- /trust:readiness-production -->.
Payable rules with provenance status `verified`:
<!-- trust:rules-verified -->1696<!-- /trust:rules-verified -->
(see [Provenance](provenance.md#current-counts)).
See [Readiness](readiness.md) for promotion criteria and the current
distribution.

---

## Layer 3 — Case completeness

**The user's scenario falls within the engine's modelled scope.**

This is what `result.is_payable`, `result.blockers`, `result.issues`,
`result.decisions` and `result.capability_report` communicate. A scenario is case-complete when every
relevant feature is computed from known rules and facts. It is case-incomplete
when a feature the scenario needs is not modelled in the CCNL data, or when a
fact it depends on was not supplied.

```python
for issue in result.issues:
    print(issue.code, issue.status)
# rinnovo_eligibility_unknown  provisional   ← 2025 income not declared
# regional_surtax_unknown      incomplete    ← no table for the region code
for gap in result.capability_report.gaps:
    print(gap.feature, gap.kind.value)
```

The distinction between an omitted input and an unknown fact is important:

- an optional input left out on purpose (no region code, no family
  composition) skips the capability: nothing is withheld and no blocker is
  added for it;
- a fact a rule needs but that is not known (prior-year income, sector,
  employer activity, the signing date of a renewal) makes the rule fall back
  to ordinary taxation and the result `provisional` and not payable, with a
  `missing_fact` blocker that names the fact.

Case completeness is the user's responsibility: only the caller knows whether
their scenario requires overtime, family deductions, or second-level agreements.
The engine's job is to report every gap, not to silently ignore it.

---

## Reading all three layers together

| Situation | Likely layer | Signal to check |
|---|---|---|
| Calculation crashes or gives NaN | Software correctness | Open a GitHub issue with a reproduction |
| Output differs from a real payslip | Source correctness | Check `result.rulesets` readiness, compare to sources |
| Output missing expected components | Case completeness | Read `blockers`, `issues` and `capability_report` |
| Output slightly off but plausible | Source OR case | Check both readiness and `decisions` |

No single metric collapses all three layers into one. A payable result has no
blocker, but in `simulation` mode it still requires the caller to check the
readiness of the rulesets, and in either mode case completeness against their
scenario.
