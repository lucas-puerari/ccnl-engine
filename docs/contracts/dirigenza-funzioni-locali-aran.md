# CCNL Area Dirigenza Funzioni Locali 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S125` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-23 |
| **Workers (est.)** | ~13k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - FEDIRETS
    - CISL FP
    - UIL FPL
    - UNSCP

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | — |

0 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 9 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-02-23 |
| **Last review** | — |
| **Latest salary tranche** | 2024-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DIRIGENTE` | Dirigente enti locali (RAL, PTA, Segretari comunali fascia A e B) | € 3,846.60 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Riepilogo CCNL Area Dirigenza Funzioni Locali 2022-2024. Conferma tabellare 50.005,77€/anno per dirigenti e segretari fascia A/B, incremento +230€/mese da 1/1/2024, signatari. | altro | 2026-02-23 | [↗](https://www.truenumbers.it/ccnl-dirigenti-enti-locali-aumenti-arretrati/) |
| Dettaglio incrementi: dirigenti RAL +491€/mese totale, segretari +400€, dirigenti PTA +377€ (comprensivi di tabellare + posizione). | altro | 2026-02-23 | [↗](https://www.logospa.it/contratto-dirigenza-funzioni-locali-2022-2024-tutte-le-novita-su-stipendi-e-normativa/) |
| SIMPLIFICATION: codice CNEL S125 da fonte secondaria (ilccnl.it). Non riportato nel testo ufficiale ARAN. | altro | — | [↗](https://ilccnl.it/ccnl/dirigenti---funzioni-locali/dirigenti---enti-locali-dal-010195) |

??? note "Coverage notes"
    Retribuzione di posizione: variabile per tipo incarico e ente, non modellata (SIMPLIFICATION). Totale mensile medio include posizione: +491€ RAL, +400€ segretari, +377€ PTA (include tabellare + posizione + altro).
    
    Segretari comunali e provinciali fascia C (neo-assunti): incremento tabellare +184€/mese (vs +230€ delle altre fasce), valore stimato 49.407,77€/anno = 3.800,60€/mese. Non modellati come livello separato per mancanza di fonte primaria verificata.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Nessuno scatto automatico di anzianità per i dirigenti. maximum_count=0.
    
    CNEL S125 inferito dalla struttura coerente dei codici ARAN: S005/S025 (FC), S105/S125 (FL), S205/S225 (Sanità) — pattern *05=comparto, *25=area dirigenza. I codici S005, S105, S205 e S225 sono verificati; S125 è inferito dal pattern.
    
    Hourly divisor 165 = 38h/settimana × 52/12 = 164.67 ≈ 165 (CCNL Area FL 2022-2024 / CCNL 17/12/2020 Art. sull'orario). Standard contrattuale PA per la dirigenza. L'orario non è soggetto a controllo puntuale.
    
    Tabellare pre-2024 3.616,60€/mese = back-calculation: 50.005,77 - 230×13 = 47.015,77€/anno / 13 = 3.616,60€/mese. Incrociato con il valore identico confermato per Area FC e Area Sanità (ARAN allinea i tabellari tra le aree dirigenziali). Aritmeticamente esatto rispetto alle fonti secondarie verificate.
    
    Un unico livello DIRIGENTE modella dirigenti RAL, PTA e segretari fascia A/B (stesso tabellare 50.005,77€/anno). I segretari fascia C (incremento +184€/mese, valore stimato 3.800,60€/mese) sono esclusi — fonte primaria non disponibile in formato leggibile. Scelta strutturale deliberata.
    
    Nessun straordinario: principio di onnicomprensività della retribuzione dirigenziale PA (Art. 3 D.Lgs. 165/2001). overtime_bands vuoto è corretto per questa categoria.
    
    Assenza non retribuita: prassi PA divisore 30 (mensile/30 per giorno di assenza). Modellato con by_30, coerente con le altre aree ARAN.
    
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13-18, comporto max 18 mesi (540 gg) — CCNL Area FL 2022-2024 (stessa disciplina delle altre aree ARAN). Modellato con SicknessTier; periodi a cavallo di soglia ricevono un unico tasso (engine limitation accettabile).
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    Stipendio tabellare da fonte secondaria (truenumbers.it, logospa.it): valore a regime dall'1.1.2024 = 50.005,77€/anno per 13 mensilità = 3.846,60€/mese. Incremento +230€/mese per dirigenti e segretari comunali fascia A e B.
    
    Tabellare pre-2024 (47.015,77€/anno = 3.616,60€/mese) back-calcolato: 50.005,77 - 230×13 = 47.015,77. Stesso valore base del CCNL Area Sanità e Area Funzioni Centrali (ARAN allinea tabellari tra aree dirigenziali).
    
    Signatari: ARAN, FEDIRETS, CISL FP, UIL FPL, UNSCP. CGIL non ha firmato (truenumbers.it).
    
    Contratto applicato a ~13.000 dirigenti: 5.500 dirigenti RAL, 5.200 dirigenti PTA (enti locali sanitari), 2.300 segretari comunali e provinciali (truenumbers.it). Platea GOAL.md (~40k) era sovrastimata.
    

## Raw data

The contract file this page is generated from: [`agreement/dirigenza-funzioni-locali-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/dirigenza-funzioni-locali-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/dirigenza-funzioni-locali-aran/example.py"
```
