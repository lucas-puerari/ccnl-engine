# Get started

## Installation

```bash
pip install ccnl-engine
```

Requires Python 3.11+.

## Quickstart

The minimum working example: load a CCNL, describe the employee, compute the
payroll.

```python
--8 < --"docs/examples/01_quickstart.py"
```

## Supported CCNLs

The library bundles 85 contract configurations covering approximately 15 million
employees across private and public sectors.

| Sector | Contracts | Workers (~) |
|---|---:|---:|
| Industria | 20 | ~3.6M |
| Terziario | 17 | ~3.5M |
| Pubblica Amministrazione | 10 | ~2.75M |
| Artigianato | 7 | ~1.2M |
| Agricoltura | 5 | ~0.7M |
| Lavoro Domestico | 2 | ~0.9M |
| Credito | 3 | ~0.35M |
| Trasporto | 3 | ~0.15M |
| Other | 18 | ~1.8M |

Full list with sources and per-contract examples: [Contracts →](../contracts/index.md)

To understand the terminology used in each contract page, read
[Domain: What is a CCNL](../domain/index.md) first.

## Disclaimer

Not legal or tax advice. Always verify results against official sources or a
qualified payroll professional.
