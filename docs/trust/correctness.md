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

- 100% branch coverage — no reachable path is untested
- `mypy --strict` — the type system rules out entire classes of logic error
- Reference cases — byte-identical assertions on real scenarios; a salary table
  change that shifts any output by even one cent fails a test

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

Source correctness is ruleset-scoped: each CCNL, tax year, and INPS file has its
own readiness tier. A `reviewed` CCNL used with `exploratory` INPS rates gives a
mixed result; the engine does not fold the readiness tier into the result, so
check it next to `result.status`.

See [Readiness](readiness.md) for promotion criteria and the current tier of each
contract.

---

## Layer 3 — Case completeness

**The user's scenario falls within the engine's modelled scope.**

This is what `result.status`, `result.issues`, `result.decisions` and
`result.capability_report` communicate. A scenario is case-complete when every
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
  composition) skips the capability: nothing is withheld and the result stays
  `final`;
- a fact a rule needs but that is not known (prior-year income, sector,
  employer activity, the signing date of a renewal) makes the rule fall back
  to ordinary taxation and the result `provisional`, with an issue that names
  the missing fact.

Case completeness is the user's responsibility: only the caller knows whether
their scenario requires overtime, family deductions, or second-level agreements.
The engine's job is to report every gap, not to silently ignore it.

---

## Reading all three layers together

| Situation | Likely layer | Signal to check |
|---|---|---|
| Calculation crashes or gives NaN | Software correctness | Open a GitHub issue with a reproduction |
| Output differs from a real payslip | Source correctness | Check `readiness`, compare to sources |
| Output missing expected components | Case completeness | Read `status`, `issues` and `capability_report` |
| Output slightly off but plausible | Source OR case | Check both readiness and `decisions` |

No single metric collapses all three layers into one. A `final` result has no
open issue, but it still requires the caller to check the readiness of the
rulesets and case completeness against their scenario.
