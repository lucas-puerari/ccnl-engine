# CCNL Components

Every CCNL is built from a standard set of components. Understanding them is
essential for interpreting the library's input types and output fields.

## 1. Job levels (*livelli di inquadramento*)

Workers are classified into a hierarchy of levels (*livelli*), each corresponding to
a skill and responsibility band. Levels are typically grouped into categories:

| Category | Description |
|---|---|
| Operaio | Blue-collar worker |
| Impiegato | White-collar employee |
| Quadro | Middle management (not quite *dirigente*) |
| Dirigente | Senior executive |

Classification is determined at hire and may change through vertical progression.
Minimum salaries are non-decreasing across levels: a higher level always carries
a higher minimum than the one below it.

## 2. Base salary (*minimo tabellare*)

The base salary is the **statutory floor** for each level. It is set by the CCNL
and cannot be reduced by individual contract.

Because CCNLs are renewed in tranches, the minimum changes at scheduled dates.
The library models these as a time series: every call passes an `as_of` date and
the engine resolves the correct value.

*Example — Metalmeccanico C3 level (monthly, gross):*

| Effective date | Base salary (EUR/month) |
|---|---:|
| 2024-06-01 | 2,133 |
| 2025-01-01 | 2,172 |
| 2026-01-01 | 2,211 |

## 3. Historical allowances (*indennità storiche*)

Three frozen elements appear in many CCNLs:

| Allowance | Description | Value |
|---|---|---|
| Contingenza | Cost-of-living supplement, frozen Nov 1993 (L. 438/1992) | Level-specific |
| EDR | *Elemento Distinto della Retribuzione*, added in 1993 | €10.33/month |
| Terzo elemento | Sector-specific third element | Varies |

**Conglobamento vs. separated:** Many modern CCNLs *conglobate* (merge) contingenza
and EDR into the base salary figure, so the published minimum already includes them
and no separate rows appear. Others keep them as distinct allowance rows. The library
handles both: when allowances are listed separately, the engine sums them; when
conglobated, the base salary column already reflects the merged value.

## 4. Seniority increments (*scatti di anzianità*)

Workers accumulate a pay increment — *scatto di anzianità* — at regular intervals
of service. Key parameters:

- **Cadence**: how many months between increments (e.g. 24 months for Metalmeccanico,
  36 months for Commercio).
- **Amount**: a fixed EUR amount per level, defined in the CCNL.
- **Maximum**: the number of increments that can be accumulated (e.g. 5 for most).

Seniority is based on **company tenure**, not age. It is distinct from career
progression, which involves a change of level.

Some CCNLs use a tiered model: the cadence changes after a certain number of
increments (e.g. the first 4 increments every 24 months, then every 36 months).

## 5. Additional months and hourly divisor

### Additional months

All Italian workers receive a **thirteenth month** (*tredicesima*) paid in December.
Many CCNLs add a **fourteenth month** (*quattordicesima*), usually in June. The
engine accounts for both via the `parameters.additional_months` time series.

### Hourly divisor (*divisore orario*)

The hourly divisor converts a monthly salary into an hourly rate. It is derived from
the standard weekly hours defined in the CCNL (see `parameters.hourly_divisor` in the
contract's JSON file). Each CCNL defines its own value; never copy one contract's
divisor into another.

## 6. Apprenticeship (*apprendistato professionalizzante*)

The *apprendistato professionalizzante* (D.lgs. 81/2015, Art. 41–47) is a fixed-term
training contract that allows reduced labour costs. Key features:

- Duration: up to 36 months (can extend to 60 in some sectors).
- Employer can terminate without notice at the end of the period.
- Reduced INPS employer contributions (often ~10% for employers with < 9 employees).

Two distinct salary models exist:

### Percentage track (*percentuale*)

The apprentice's pay is expressed as a percentage of the destination level's
minimum, increasing at preset thresholds.

*Example — Metalmeccanico:*

| Phase | Months elapsed | % of destination level |
|---|---:|---:|
| 1 | 0–11 | 70% |
| 2 | 12–23 | 80% |
| 3 | 24+ | 90% |

Used in: Metalmeccanico, Chimica, Edilizia, and most industrial CCNLs.

### Under-classification track (*sottoinquadramento*)

The apprentice is formally assigned to a level two steps below the destination,
then moves up at scheduled months.

*Example — Commercio:*

| Phase | Months elapsed | Effective level |
|---|---:|---|
| 1 | 0–11 | Destination − 2 |
| 2 | 12–23 | Destination − 1 |
| 3 | 24+ | Destination |

Used in: Commercio, Turismo, and most tertiary-sector CCNLs.

## 7. Part-time

Part-time contracts scale base pay, seniority, and most allowances proportionally
to the agreed ratio of full-time hours. Individual frozen elements (*ad personam*
amounts agreed outside the CCNL table) are not scaled.

## 8. Fixed-term (*tempo determinato*)

Remuneration is identical to a permanent contract. The only difference is an
additional **NASpI *addizionale*** of 1.40% of gross, charged to the employer
(Art. 2, c. 28, L. 92/2012).

## 9. Social contributions (INPS)

### Percentage-based (all sectors except domestic work)

Both employee and employer contribute a percentage of gross salary, up to an annual
ceiling (*massimale IVS*). Rates vary by sector, employer size, and contract type.
The `tax/data/` files bundled with the library carry the precise rates for each year
and sector.

### Flat hourly rate (domestic work)

Domestic workers (*lavoro domestico*) use a different system: INPS publishes tables
of fixed per-hour contributions by wage bracket. No percentage of gross applies.

### Contribution base

The INPS base is gross pay minus any elements flagged
`contribution_relevant = false` in the contract data (e.g. certain expense
reimbursements).

## 10. IRPEF and surcharges

### IRPEF

Italian personal income tax is progressive, computed on *reddito imponibile* (taxable
income = gross − INPS employee contributions). Rates and brackets are set by law
annually; values for each year are in the bundled `tax/data/` files.

Workers earning from employment receive a **work income deduction** (*detrazione da
lavoro dipendente*, Art. 13 TUIR): a credit that decreases as income rises and
reaches zero around €50,000.

Workers with taxable income between €8,500 and €28,000 receive the **trattamento
integrativo** (Art. 1 D.L. 3/2020): €1,200/year, withheld by the employer and
offset against the tax due.

### Addizionale regionale

A regional surcharge on taxable income, with rates set by each region. Rates are
in the bundled `surtax/data/regionale/` files.

### Addizionale comunale

A municipal surcharge on taxable income, identified by the municipality's *codice
Belfiore*. Rates are in the bundled `surtax/data/comunale/` files.

### Domestic work exception

For domestic workers, the employer is not a *sostituto d'imposta*: IRPEF is not
withheld at source. Workers declare and pay it directly.

## 11. TFR (*Trattamento di Fine Rapporto*)

The severance fund accrues annually at 1/13.5 of the TFR-relevant remuneration
(Art. 2120 c.c.). The TFR base is gross pay minus elements flagged
`tfr_relevant = false` in the contract data.

For employers with more than 50 employees, the TFR accrual is channelled to INPS
(or a pension fund if the worker elects one) rather than held by the company.

## 12. Second-level bargaining (*contrattazione di secondo livello*)

Company or territorial agreements may supplement the national CCNL with additional
allowances: productivity bonuses, shift premiums, welfare. Each supplementary element
can be independently configured for INPS, TFR, and apprenticeship scaling.

The 5% preferential tax rate on *premi di risultato* (Art. 1 c. 182 L. 208/2015) is
**not** computed by the engine.

---

→ [Guide: How to use the library](../guide/employment-types.md)  
→ [Contracts: all 85 supported CCNLs](../contracts/index.md)
