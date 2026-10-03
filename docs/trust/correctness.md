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
- Reference table cases: <!-- trust:reference-cases -->5<!-- /trust:reference-cases -->
  cases in `tests/fixtures/expected/`, each running one regular period through
  `PayrollEngine` and asserting, to the cent, the three values its cited
  salary table states: base salary, fixed allowances and period gross. They
  do not check net pay, contributions, taxes or employer cost.
  <!-- trust:reference-cases-source-linked -->5<!-- /trust:reference-cases-source-linked -->
  are `source_linked` (they cite the table they model) and
  <!-- trust:reference-cases-verified -->0<!-- /trust:reference-cases-verified -->
  are `verified` against an independent payslip or official worked example.
- Legal scenario tests: selected rules (IRPEF, regional and municipal
  surtaxes, substitute-tax regimes, apprenticeship scaling, the withholding
  schedule and others) checked against hand-derived values, mainly in
  `tests/acceptance/legal_scenarios/`.

No test compares a complete payslip (gross, contributions, taxes, net and
employer cost) with an independent source. A wrong rule shared by the engine
and a hand calculation that follows the same reading goes undetected.

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
no tier. The engine does not fold the readiness tier into the result
assurance yet, so check it next to `result.is_payable`.

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
| Output differs from a real payslip | Source correctness | Check `readiness`, compare to sources |
| Output missing expected components | Case completeness | Read `blockers`, `issues` and `capability_report` |
| Output slightly off but plausible | Source OR case | Check both readiness and `decisions` |

No single metric collapses all three layers into one. A payable result has no
blocker, but it still requires the caller to check the readiness of the
rulesets and case completeness against their scenario.
