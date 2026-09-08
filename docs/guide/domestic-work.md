# Domestic work (*lavoro domestico*)

Domestic employment (*lavoro domestico*) follows a contribution system entirely
different from the general regime. Understanding the differences is essential before
computing payrolls for this sector.

See [Domain: Social contributions](../domain/components.md#9-social-contributions-inps)
for the background on the general and flat-rate systems.

## Key differences

| Feature | General regime | Domestic work |
|---|---|---|
| INPS contributions | % of gross salary | Flat rate per hour worked (INPS quarterly tables) |
| INPS base | Proportional | Depends on wage bracket |
| Employer as *sostituto d'imposta* | Yes — withholds IRPEF at source | **No** — worker files directly |
| `weekly_hours` required | No | **Yes** — needed to compute flat INPS |
| IRPEF withheld | Yes | No (`irpef_net = 0`) |

## Convivente vs. non-convivente

The library includes two separate JSON files:

- `lavoro-domestico-convivente.json` — live-in domestic worker
- `lavoro-domestico-non-convivente.json` — non-live-in domestic worker

Each file carries the correct INPS rate table and level structure for that variant.

## Usage

Pass `weekly_hours` in `WorkArrangement`. The engine uses it together with the
flat-rate INPS table to compute contributions.

```python
--8<--"docs/examples/10_domestic.py"
```

!!! warning
    Because the employer does not withhold IRPEF, `payroll.irpef_net` is always
    `Decimal(0)` for domestic workers. `payroll.irpef_gross` is computed for
    informational purposes but is not deducted.

**API reference:** [`WorkArrangement`](../api/engine.md),
[`PayrollResult.employer_withholds_irpef`](../api/engine.md)
