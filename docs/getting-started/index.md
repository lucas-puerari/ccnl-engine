# Get started

## Installation

```bash
pip install ccnl-engine
```

Requires Python 3.12+.

## Quickstart

The minimum working example: load a CCNL, describe the employee, compute the
payroll.

```python
--8<-- "docs/examples/period/example.py"
```

Every result says whether its amounts can be paid as computed
(`result.is_payable`, `result.blockers`) and which rulesets it read, with
their readiness (`result.rulesets`). `engine.list_contracts()` and
`engine.inspect_ruleset(ccnl_id)` report readiness before any run.
`PayrollEngine.bundled()` simulates; `PayrollEngine.bundled(mode="operational")`
computes the same amounts but blocks payment unless the CCNL ruleset is
`production`, which only Metalmeccanico Federmeccanica is. See
[Readiness](../trust/readiness.md#simulation-and-operational-modes).

## Supported CCNLs

Every bundled CCNL is listed in the contracts index with its CNEL code,
sector, estimated workforce, readiness and coverage; the list and its counts
are generated from the data.

Full list with sources and per-contract examples: [Contracts →](../contracts/index.md)

To understand the terminology used in each contract page, read
[Domain: What is a CCNL](../domain/index.md) first.

## Disclaimer

Not legal or tax advice. Always verify results against official sources or a
qualified payroll professional.
