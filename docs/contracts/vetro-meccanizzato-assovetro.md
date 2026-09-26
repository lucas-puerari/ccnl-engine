# CCNL Vetro (Industrie) — Settori Meccanizzati (Prime Lavorazioni)

| | |
|---|---|
| **CNEL code** | `B132` |
| **Sector** | vetro industria — settori meccanizzati |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-04-09 |
| **Workers (est.)** | ~28k |
| **Ruleset version** | `—` |
| **Extraction** | 🧑 Manual |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assovetro
    - Filctem-CGIL
    - Femca-CISL
    - Uiltec-UIL

## Coverage

### Funzionalità

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🔲 not_implemented |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🟢 Verified |
| **Last human review** | 2026-09-17 |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2026-04-09 |
| **Last verified** | 2026-09-17 |
| **Next salary event** | — |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Livello A — base | € 2,874.69 | 2026-01-01 |
| `B` | Livello B — base | € 2,616.86 | 2026-01-01 |
| `C` | Livello C — base | € 2,354.05 | 2026-01-01 |
| `D` | Livello D — base | € 2,080.92 | 2026-01-01 |
| `E` | Livello E — base | € 1,822.13 | 2026-01-01 |
| `F` | Livello F — base | € 1,683.88 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 17.56 |
| `B` | € 16.53 |
| `C` | € 14.98 |
| `D` | € 12.91 |
| `E` | € 10.33 |
| `F` | € 8.26 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    TRANCHE 2026-2028: Only the Jan 2026 tranche is modelled (retroactive from renewal 2026-04-09). Remaining tranches at D1: +15 EUR Oct 2026, +30 EUR Jan 2027, +25 EUR Jun 2027, +75 EUR Jul 2028. Per-level amounts confirmed proportional (A:D=1.5, F:D=0.7462) but official per-level tables not publicly available at extraction date 2026-09-17.

!!! warning ""
    APPRENTICESHIP: not modelled. Under-classification type confirmed (first half: 2 levels below; second half: 1 level below). Total duration not verified from post-2026 source.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabelle retributive CCNL Settori meccanizzati Vetro Industrie — KITech | tabella_retributiva | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=215) |
| Industrie del Vetro, Lampade e Display — Tabelle retributive 2023-2025 | tabella_retributiva | — | [↗](https://esterinocafasso.it/rubrica-mensile/industrie-del-vetro-lampade-e-display-nuovo-ccnl-diffuse-le-tabelle-dei-minimi-retributivi/) |
| CCNL Vetro Meccanizzato Industria — ilCCNL.it tabelle retributive | tabella_retributiva | — | [↗](https://ilccnl.it/ccnl/vetro---industria/vetro-meccanizzato---industria/tabelleretributive) |
| Accordo di rinnovo CCNL Vetro Industrie 2026-2028 — Assovetro | altro | — | [↗](https://confindustriatoscanacentroecosta.it/ccnl-vetro-industria-ipotesi-di-accordo-e-nuovi-minimi-tabellari/) |

??? note "Coverage notes"
    SCOPE: Settori meccanizzati (prime lavorazioni) only — 6 base sub-levels (A, B, C, D, E, F). Other sub-sectors (trasformazione, soffio, lampade e display) and sub-levels (A2, B2, C2, D2, D3, E2, E3) not modelled.
    
    SALARY MODEL: split — base_salary = minimo tabellare (paga base); fixed_allowance TER = Terzo Elemento della Retribuzione (EDR, 10.33 EUR, frozen). Sources: esterinocafasso.it for 2023-03-01 / 2024-01-01 / 2025-04-01 periods; kitech.it + ilccnl.it for 2026-01-01.
    
    HOURLY_DIVISOR: 173 — confirmed by ilccnl.it tabelle retributive (divisore orario column, 2026-01-01). Back-check D1: (2080.92+10.33)/173 = 12.09 EUR/h.
    
    SENIORITY: 5 biennial scatti (cadence 24 months, max 5). Per-level amounts sourced from kitech.it Jan 2026: A=17.56, B=16.53, C=14.98, D=12.91, E=10.33, F=8.26 EUR. Historical amounts assumed stable (not verified for 2023-2025 periods).
    
    FONCHIM: employer contribution 1.5% (2023-2025 contract) increased to 2.0% from Jan 2026 per the April 2026 renewal (source: Assovetro/Filctem-CGIL press releases).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/vetro-meccanizzato-assovetro.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/vetro-meccanizzato-assovetro.py"
```
