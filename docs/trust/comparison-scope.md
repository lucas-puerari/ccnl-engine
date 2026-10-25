# Comparison scope by variant

Which payroll variants an adopter can compare with its own output today,
and on what evidence. A variant in scope has an oracle the engine already
matches; a variant out of scope is compared only after the evidence below
exists, and a run that needs a missing fact or an open limitation is not
payable anyway (`is_payable`, `blockers`).

The evidence is the one the [validation matrix](validation-matrix.md)
records. Independent evidence comes from public provider outputs (official
worked examples and published payslips with a traceable source): no total
but the base salary has one on a production CCNL yet.

## Variants

| Variant | Evidence today | Scope |
|---|---|---|
| Ordinary month, full time | Hand oracles on every production CCNL; real payslips pin the base salary | In scope |
| Extra month (tredicesima, quattordicesima) | Hand oracles on every production CCNL | In scope |
| Annual conguaglio | Hand oracles; one real conguaglio checks two rule functions | In scope, compared on the totals of December |
| Termination | Hand oracles; TFR of an employment started before 2001 blocks | In scope from 2001 hires |
| Part time | Hand oracles on metalmeccanico-federmeccanica only; two real part-time payslips are not replayable | Out of scope until a public output covers a production CCNL other than metalmeccanico |
| Apprenticeship | Hand oracles on metalmeccanico-federmeccanica only; the TFR guarantee fund compensation is an open limitation with a monetary impact | Out of scope |
| Fixed term | Hand oracles on metalmeccanico-federmeccanica only | Out of scope |
| Hire or termination mid-month | Hand oracles on metalmeccanico-federmeccanica only | Out of scope |
| Sickness | Hand oracles on metalmeccanico-federmeccanica only; open limitations on every production CCNL | Out of scope (see below) |
| Maternity | Unit-level pilots only, no scenario and no replayed payslip | Out of scope |
| Several regions or comuni | Every validation packet uses one region and one comune | Out of scope |

## Sickness limitations

Two limitations of `knowledge/limitation/engine.json` keep sickness out of
scope on the production CCNLs:

- `sickness_inps_daily_base`: the INPS share is computed on the CCNL daily
  quota, not on the INPS daily base; its monetary impact is unknown. It
  closes when the INPS daily base (retribuzione media globale giornaliera)
  is an input or is derived from the run, with a cited source, and a public
  worked example of a sick month matches.
- `sickness_cumulation_window`: covers five of the six production CCNLs
  and closes with the comporto window of each CCNL sourced in its file.

Until both close, a sick month is compared, if at all, only on the gross
and the employer-paid integration, never on contributions or net.
