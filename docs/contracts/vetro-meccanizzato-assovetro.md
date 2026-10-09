# CCNL Vetro (Industrie) — Settori Meccanizzati (Prime Lavorazioni)

| | |
|---|---|
| **CNEL code** | `B132` |
| **Sector** | vetro industria — settori meccanizzati |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-04-09 |
| **Workers (est.)** | ~28k |
| **Ruleset version** | `2026.2` |
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

Derived from the capability registry, as in the [capability matrix](capability-matrix.md).

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |

| Layer | Status |
|---|---|
| **L1 — Gross** | 🔲 |
| **L2 — Net** | 🔲 |
| **L3 — Work rules** | 🔲 |
| **Limits of this contract** | base_salary |

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
| **Latest salary tranche** | 2026-01-01 |

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

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "vetro-meccanizzato-assovetro/tranches_from_october_2026 · base_salary · impact yes · open"
    TRANCHE 2026-2028: Only the Jan 2026 tranche is modelled (retroactive from renewal 2026-04-09). Remaining tranches at D1: +15 EUR Oct 2026, +30 EUR Jan 2027, +25 EUR Jun 2027, +75 EUR Jul 2028. Per-level amounts confirmed proportional (A:D=1.5, F:D=0.7462) but official per-level tables not publicly available at extraction date 2026-09-17.

    **Applies when:** `base_salary` applies; from 2026-10-01.

    **Remediation:** Add the October 2026 to July 2028 tranches once the per-level tables are published.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
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
    
    FONCHIM: employer contribution 1.5%, raised by 0.5% to 2.0% from 1 January 2027 by the renewal of 9 April 2026 (source: Confindustria Toscana Centro e Costa summary of the ipotesi di accordo). No employee minimum is bundled.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/vetro-meccanizzato-assovetro.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/vetro-meccanizzato-assovetro.py"
```
