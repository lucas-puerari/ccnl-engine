<!-- auto-generated -- run: uv run python docs/scripts/gen_coverage_matrix.py -->
<!-- generated: 2026-09-08 -->

# Feature Coverage Matrix

Generated: 2026-09-08 - 103 CCNL

Coverage % = percentage of bundled CCNLs that implement the feature (partial = 0.5).

## Layer 1 -- Gross

| Feature | Coverage | Note |
|---------|----------|------|
| Base salary | 99% | Minimo contrattuale da tabella CCNL |
| Seniority allowance | 84% | Scatti di anzianita |
| Fixed allowances | 55% | Indennita fisse contrattuali |
| Additional months | 100% | 13/14 mensilita -- obbligatorio per schema |
| Hourly rate | 100% | Da divisore orario -- obbligatorio per schema |

## Layer 2 -- Net

| Feature | Coverage | Note |
|---------|----------|------|
| INPS contributions | 94% | Contributi INPS dipendente e datore |
| TFR | 94% | Trattamento fine rapporto Art. 2120 c.c. |
| IRPEF | 92% | Ritenuta IRPEF (esclusi withholding-exempt per design) |
| Regional/municipal surtax | 92% | Addizionali -- richiede regione/comune in input |
| Family deductions (Art. 12) | 100% | Detrazioni familiari a carico -- obbligatorie per schema |
| Mortgage interest deduction (Art. 15) | 100% | Interessi passivi mutuo prima casa -- obbligatorio per schema |

## Layer 3 -- Work rules

| Feature | Coverage | Note |
|---------|----------|------|
| Overtime/night/holiday | 94% | Maggiorazioni orarie da time_supplements CCNL |
| Sick/injury leave | 94% | Integrazione malattia/infortunio da sickness_rules CCNL |
| Leave entitlement | 94% | Ferie e permessi da leave_rules CCNL |
| Absence deduction | 94% | Decurtazione per assenza da absence_rules CCNL |
