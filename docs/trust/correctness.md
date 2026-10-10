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
  decisions (source labels, input names).
- Reference table cases: <!-- trust:reference-cases -->11<!-- /trust:reference-cases -->
  cases in `tests/knowledge/ccnl_engine/payroll/period/reference_case/`, each running one regular period through
  `PayrollEngine` and asserting, to the cent, the three values its cited
  salary table states: base salary, fixed allowances and period gross. They
  do not check net pay, contributions, taxes or employer cost.
  <!-- trust:reference-cases-source-linked -->10<!-- /trust:reference-cases-source-linked -->
  are `source_linked` (they cite the table they model) and
  <!-- trust:reference-cases-verified -->1<!-- /trust:reference-cases-verified -->
  are `verified` against an independent payslip or official worked example.
- Legal scenario tests: selected rules (IRPEF, regional and municipal
  surtaxes, substitute-tax regimes, apprenticeship scaling, the withholding
  schedule and others) checked against hand-derived values, in the
  knowledge tests under `tests/knowledge/ccnl_engine/`.

Full-payslip oracles are kept apart from the reference table cases and from
the rule oracles, as `oracles_payslip_*.py` in
`tests/knowledge/ccnl_engine/payroll/period/`, and run in
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

Metamorphic tests in `tests/knowledge/ccnl_engine/payroll/period/test_metamorphic_concia.py`
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
<!-- trust:readiness-production -->0<!-- /trust:readiness-production -->.
Payable rules with provenance status `verified`:
<!-- trust:rules-verified -->0<!-- /trust:rules-verified -->
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
