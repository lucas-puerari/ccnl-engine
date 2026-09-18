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
mixed-confidence result, which `calculation.result.confidence` reflects.

See [Readiness](readiness.md) for promotion criteria and the current tier of each
contract.

---

## Layer 3 — Case completeness

**The user's scenario falls within the engine's modelled scope.**

This is what `calculation_scope` and `warnings` communicate. A scenario is
case-complete when every relevant feature is either computed or explicitly excluded
by a deliberate caller choice. It is case-incomplete when a feature the scenario
needs is either not modelled in the CCNL data or not supplied as an input.

```python
for item in result.calculation_scope:
    print(item.feature, item.status)
# irpef                    verified      ← computed, included in net_annual
# family_deductions        excluded      ← caller chose not to supply FamilyComposition
# overtime                 not_computed  ← CCNL does not model this feature yet
```

The distinction between `excluded` and `not_computed` is important:

- `excluded` — the caller deliberately omitted an optional input (e.g. no
  `Jurisdiction` passed, so regional surtax is zero and excluded from the net)
- `not_computed` — the engine could not compute this even if asked because the
  CCNL data does not include the relevant rules

Case completeness is the user's responsibility: only the caller knows whether
their scenario requires overtime, family deductions, or second-level agreements.
The engine's job is to report every gap, not to silently ignore it.

---

## Reading all three layers together

| Situation | Likely layer | Signal to check |
|---|---|---|
| Calculation crashes or gives NaN | Software correctness | Open a GitHub issue with a reproduction |
| Output differs from a real payslip | Source correctness | Check `readiness`, compare to sources |
| Output missing expected components | Case completeness | Read `calculation_scope` and `warnings` |
| Output slightly off but plausible | Source OR case | Check both readiness and scope |

No single metric collapses all three layers into one. A `high` confidence result
has high source confidence and no active warnings, but it still requires the caller
to check case completeness against their scenario.
