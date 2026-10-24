# Validation packets

A validation packet records one case on which the engine is compared with an
output it did not compute. It is the unit of the certification protocol:
every external comparison that counts toward readiness is a packet, and the
schema gate (`scripts/provenance/check.py --schema`) rejects an incomplete
one. Packets live in
`tests/knowledge/ccnl_engine/period/validation_packet/`, one JSON file each.

## What a packet declares

| Section | Fields | Purpose |
|---|---|---|
| `artifact` | `id`, `kind`, `sha256` | What the engine is compared with, pinned by its hash. `kind` is `provider_output`, `official_worked_example`, `hand_oracle` or `engine_provisional` |
| `provenance` | `source`, `obtained_on`, `independence`, `anonymisation`, `retention` | Where the artifact comes from, why it is independent of the engine and of the sources of the bundle, how personal data were removed and the right to keep it |
| `inputs` | `scenario` and the facts of a request (`ccnl_id`, `level_code`, `year`, `month`, `headcount`, `contract_type`, residence, hire and termination dates, hours, events...) with the keys of an observed payslip replay | Every fact that rebuilds the case, so a provider can compute it and the engine can replay it |
| `outputs` | per output: `output`, `value`, `perimeter`, `tolerance`, `rounding`, `result`, `explanation` | One entry per compared total |
| `review` | `reviewer`, `date`, `owner`, `review_by` | Who checked the comparison, who answers for it, when it is looked at again |
| `versions` | `engine`, `bundle`, `provider` | What the comparison ran on |

`scenario` is one of `ordinary_month`, `partial_month`, `variable`,
`extra_month`, `annual_conguaglio`, `termination` and `employer_cost`.

## Each output on its own

`output` is one of the eight totals of the definition of done: `base_salary`,
`gross`, `employee_contributions`, `employer_contributions`, `tax`, `net`,
`tfr`, `employer_cost`. A rate is no total: an INPS rate never covers the
contributions, a base salary never the gross, a net never the employer cost.
Each entry states the `perimeter` of its total (what it includes), a
`tolerance` in euro with cents and the `rounding` the artifact applies
(`half_up_cents`, `half_even_cents`, `truncate_cents`, `whole_euro`).

`result` is the outcome of the comparison:

| Result | Covers the output | Required |
|---|---|---|
| `match` | yes | |
| `explained_difference` | yes | `explanation` |
| `engine_bug` | no | `explanation` (the fix) |
| `artifact_error` | no | `explanation` (why the artifact is wrong) |
| `pending` | no | |

## From packets to readiness

A valid packet adds, for each output it matched or explained, the triple
`(ccnl, output, independence)` to the [validation matrix](validation-matrix.md).
The independence follows from `artifact.kind`: a `provider_output` and an
`official_worked_example` stand for a provider output, a `hand_oracle` for a
hand oracle, and an `engine_provisional` packet (an input packet the engine
has computed while it waits for a provider) covers nothing. The readiness
gate reads those triples, so a packet is the way an output of a `production`
CCNL leaves the `provider output` list of
`scripts/provenance/readiness/baseline.json`.

## The packets of the production CCNLs

Every `production` CCNL has a packet for each scenario: the three pilots
(`commercio-confcommercio` level 4, `metalmeccanico-federmeccanica` C3,
`edilizia-ance-impiegati` level 4) and
`pubblici-esercizi-fipe-angem-ristorazione-collettiva` level 4, 28 input
packets of an impiegato hired on 1
January 2025, resident in IT-25 / A005, ready to hand to a payroll
provider. The `employer_cost` packets enrol the worker in the pension fund
of the CCNL with 60 employees and compare the employer side only. The
`variable` packets of `edilizia-ance-impiegati` and of the ristorazione
collettiva state the hourly rate of their overtime, since the bundle has no
verified hourly base for those CCNLs. A test keeps the packets on the
`production` tier: a CCNL promoted to it gets its packets in the same
change.

Until a provider computes them they are `engine_provisional`: valid, with
`result` `pending`, covering nothing, and pinned to what the engine computes
today by `tests/knowledge/ccnl_engine/period/validation_packet/test_packets.py`.
After a change of the engine that is meant, rewrite their values with:

```bash
uv run python -m tests.knowledge.ccnl_engine.period.validation_packet.runner
```

When a provider output arrives, the packet takes its `artifact` (kind,
`sha256`), `provenance`, `versions.provider`, the values of the provider and
a `result` per output; only then does it cover anything.
