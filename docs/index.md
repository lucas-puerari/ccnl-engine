# ccnl-engine

Python library for computing gross-to-net salary and employer cost from Italian
collective labor agreements (CCNL) and statutory contribution rates.

[**Demo**](../demo/) · [**GitHub**](https://github.com/lucas-puerari/ccnl-engine) · [**CCNL coverage**](contracts/index.md)

---

## What's in this documentation

| Section | Description |
|---|---|
| [Get started](getting-started/index.md) | Install, quickstart, and first payroll in 10 lines |
| [Domain](domain/index.md) | What CCNLs are, how Italian labor law structures them |
| [Guide](guide/employment-types.md) | How to use every library feature with worked examples |
| [Contracts](contracts/index.md) | All 100+ supported contracts — salary tables, sources, examples |
| [API reference](api/index.md) | Full reference for every public type and function |

## Scope

The engine models:

- IRPEF gross and net (Art. 11–13 TUIR), work income deductions,
  *trattamento integrativo* (Art. 1 D.L. 3/2020)
- Regional and municipal income tax surcharges
  (*addizionale regionale e comunale IRPEF*)
- INPS contributions (employee and employer), resolved by headcount tier
- TFR accrual
- Contractual employer funds
- Part-time scaling, seniority increments, fixed allowances
- Apprenticeship contracts (under-classification and percentage tracks)
- Fixed-term contracts (NASpI *addizionale*)
- Second-level bargaining — territorial and company supplementary allowances
- Domestic work (flat per-hour contributions, non-withholding employer)

**Not modelled:**

- Family-dependent deductions (Art. 12 TUIR)
- Bilateral system contributions (EST, Fon.Te, …)
- Overtime, night/holiday premiums, leave accruals, sick-pay integrations
- Preferential 5% tax on *premio di risultato*

Each limitation is documented in the relevant contract's `coverage.notes` field.

## Disclaimer

Not legal or tax advice. Always verify results against official sources or a
qualified payroll professional.
