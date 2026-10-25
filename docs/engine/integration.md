# Integrating the engine

How to run ccnl-engine inside a service: one engine per process, what it
reads and caches, how it rounds, what to persist, how to upgrade, and which
personal data a persisted state can hold.

## One engine per process

Create the engine once and reuse it for every calculation:

```python
from ccnl_engine import PayrollEngine

ENGINE = PayrollEngine.bundled()  # or PayrollEngine(repository=..., mode=...)
```

The engine holds no state between calls: the state of a worker travels in
the request (`opening_state`) and in the result (`closing_state`). Every
calculation runs in its own decimal context (28 digits, the context is
local to the call and to the thread), so calls from several threads do not
interfere. The knowledge bundle is read lazily, parsed and checked against
its manifest hash once per process, and kept in process-wide caches of
frozen models that no call mutates.

## Cost of a run

The first calculation of a process loads the CCNL and the tax year it
needs; later ones read the caches. On a laptop (Apple silicon, CPython
3.12) a regular month of Commercio level 4 took about 80 ms cold and
1.4 ms warm. Measure on your own hardware: the figures are an order of
magnitude, not a promise. To keep the first run of a batch off the
critical path, compute one run per CCNL and tax year you serve at start-up;
that also surfaces a damaged bundle (`DataIntegrityError`) at deploy time,
not during payroll.

## Rounding

Amounts are `Decimal`, never `float`. A monetary result (a rate times a
base, a bracket, a proportion) is rounded to the cent half up when it is
computed; sums of rounded amounts are not rounded again. The net is not
rounded to the euro: an arrotondamento netto in busta is outside the
engine (see [Perimeter and tolerance](../trust/perimeter.md)).

## What to persist

For each payslip keep:

- the request JSON (`request_to_json`) and the result JSON
  (`result_to_json`), which carries the payslip lines, the progressivi and
  the remittance lines;
- the closing state JSON (`period_state_to_json`), which opens the next
  run;
- `engine_version`, `bundle_version` and, from `result.rulesets`, the id,
  version and source hash of each ruleset the run read.

A stored state of an earlier schema is migrated when read. A stored
request is read only by a release of the same request schema: to replay an
archived request, install the release that wrote it. A result is never
read back; recompute it from its request.

## Upgrades

The package is in alpha (see
[Versioning and support](../trust/data-operations.md#versioning-and-support)):
pin an exact version, read the changelog, and before you switch replay a
sample of your archived requests with the new version and compare the
totals with your own payslips (`ccnl_engine.results.compare_totals`). A
difference is a change of the engine or of the bundle; the
`bundle_version` tells the two apart.

## Personal data

The engine logs nothing and writes nothing: it computes from what it is
given. What you persist can hold personal data, and a state can hold
special categories of data (GDPR art. 9): a sickness episode or a
maternity leave in the state of a run is health data. Store states and
requests with the protections those data need, and keep exception texts
(which can quote input values) out of shared logs.
