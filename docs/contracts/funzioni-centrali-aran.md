# CCNL Comparto Funzioni Centrali — Triennio 2022-2024

| | |
|---|---|
| **CNEL code** | `S005` |
| **Sector** | Pubblica Amministrazione — Comparto Funzioni Centrali |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-01-27 |
| **Workers (est.)** | ~250k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - CISL
    - CONFSAL UNSA
    - CONFSAL
    - FLP
    - CGS
    - CONFINTESA FP
    - CONFINTESA
    - UIL PA
    - UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ELEVATE_PROFESSIONALITA` | Area Elevate Professionalità | € 3,107.21 | — |
| `FUNZIONARI` | Area Funzionari ed Elevata Qualificazione — Funzionari | € 2,275.39 | — |
| `ASSISTENTI` | Area Assistenti | € 1,873.56 | — |
| `OPERATORI` | Area Operatori | € 1,780.57 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    aliquote INPS CTPS (ex-INPDAP) — dipendente 8,80%, datore 24,20% — da proxy kitech.it 2026; verificare circolare INPS annuale per valori esatti.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-01-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/01/CCNL_L_C_FC_2022_2024.pdf) |
| — | — | 2026-08-06 | [↗](https://cislfp.it/2026/08/06/ccnl-funzioni-centrali-2025-2027-aumenti-busta-paga/) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    apprendistato assente dal CCNL vigente (fonte primaria: indice ARAN CCNL 2022-2024, Art. 1-38 senza capitolo apprendistato) e dal CCNL Ministeri 12/6/2003 richiamato dall'Art. 38 Conferme, che esclude espressamente gli apprendisti dall'ambito di applicazione (fonte secondaria: olympus.uniurb.it); quadro normativo PA D.Lgs. 165/2001 non prevede apprendistato ex D.Lgs. 81/2015.
    
    CCNL Funzioni Centrali 2025-2027 (S005) firmato definitivamente il 2026-08-06; in vigore dal 2026-08-07. Incrementi retroattivi al 1/1/2025 e 1/1/2026 liquidati con gli stipendi di agosto/settembre 2026. Tre periodi aggiornati: 2025-01-01, 2026-01-01, 2027-01-01. Fonte: CISL FP (cislfp.it), testo ARAN definitivo non ancora pubblicato su aranagenzia.it al 2026-09-09.
    
    codice CNEL S005 confermato da tre fonti secondarie convergenti: lavoro-economia.it (intestazione pagina "CCNL Comparto Funzioni Centrali [Cnel: S005]"), blia.it (ID S005-209278), contratticcnl.it (/ccnl/s005/). Verificato 2026-09-09.
    
    retribuzione tabellare conglobata dal 1/1/2024 per 13 mensilità (Tabella 2, Art. 30 CCNL 2022-2024); tranche precedente dal 9/5/2022 derivata per sottrazione degli incrementi Tabella 1.
    
    divisore orario 156 (settimana di 36h) — Art. 29 c.3 CCNL 2022-2024 fonte primaria. Verifica: OPERATORI 1653,97/156=10,60; ASSISTENTI 1740,36/156=11,16; FUNZIONARI 2113,59/156=13,55.
    
    progressione economica non automatica — differenziali stipendiali assegnati per graduatoria (Art. 16 CCNL 2022-2024); seniority_increments.maximum_count=0.
    
    sub-settori ENAC, ANSFISA, ANSV e AGID hanno tabelle retributive proprie (Tabelle 3-6 CCNL) non modellate — out_of_scope per implementazione standard.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/funzioni-centrali-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/funzioni-centrali-aran.py"
```
