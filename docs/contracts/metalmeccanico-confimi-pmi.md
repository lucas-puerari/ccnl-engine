# CCNL Metalmeccanici Piccola Industria (CONFIMI IMPRESA MECCANICA)

| | |
|---|---|
| **CNEL code** | `C01A` |
| **Sector** | metalmeccanico |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~100k |
| **Ruleset version** | `2025.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFIMI IMPRESA MECCANICA
    - FIM-CISL
    - UILM-UIL

## Coverage

### Funzionalità

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | — |
| **Next salary event** | 2027-06-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9Q` | Category 9Q — senior quadro (senior management), with funzione quadro allowance | € 3,272.42 | 2028-06-01 |
| `9` | Category 9 — expert specialist, senior impiegato direttivo; includes elemento retributivo | € 3,272.42 | 2028-06-01 |
| `8Q` | Category 8Q — quadro (middle management), with funzione quadro allowance | € 2,943.48 | 2028-06-01 |
| `8` | Category 8 — senior specialist or impiegato direttivo; includes elemento retributivo | € 2,943.48 | 2028-06-01 |
| `7` | Category 7 — expert specialist, university-level role or equivalent experience | € 2,706.26 | 2028-06-01 |
| `6` | Category 6 — senior specialist, team coordinator or technical reference | € 2,521.94 | 2028-06-01 |
| `5` | Category 5 — highly skilled worker, autonomous complex tasks | € 2,351.35 | 2028-06-01 |
| `4` | Category 4 — specialist worker, complex independent operations | € 2,195.29 | 2028-06-01 |
| `3` | Category 3 — skilled worker, qualified operations | € 2,103.44 | 2028-06-01 |
| `2` | Category 2 — semi-skilled worker, standard repetitive operations | € 1,896.80 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `6` | € 32.43 |
| `7` | € 36.41 |
| `8` | € 40.95 |
| `8Q` | € 40.95 |
| `9` | € 45.96 |
| `9Q` | € 45.96 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP OMITTED: Art. 10 CCNL (2022-01-01 update) provides an under_classification model where the destination cat.3 requires initial classification at 90% of cat.2 salary (a hybrid percentage+under_classification mechanism not directly supported). Apprenticeship omitted from this model; affected employers should refer to the CCNL text.

!!! warning ""
    WORK RULES: overtime bands and absence rules modelled on the standard industry framework consistent with the CONFAPI PMI metalmeccanica CCNL (C018), which shares the same legislative base. Verify specific CONFIMI provisions before applying.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-10-28 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=445) |
| — | — | 2025-10-28 | [↗](https://www.consulentidellavoro.ts.it/index.php/circolari-e-news/172-tabelle-stipendi-ccnl-metalmeccanica-confimi-pmi-aggiornamento-2026-2027-2028) |
| — | — | 2025-10-28 | [↗](https://www.fim-cisl.it/2025/10/29/metalmeccanica-piccola-industria-firmato-il-rinnovo-del-ccnl-confimi/) |
| — | — | — | [↗](https://www.direzionelavoro.it/sites/default/files/files_pubblici/Accordo%20C01A%20CONFIMI.pdf) |

??? note "Coverage notes"
    CONGLOBATED MODEL (levels 2-7): base_salary = total minimo tabellare per the CONFIMI table (paga base + contingenza + EDR all consolidated). fixed_allowances is empty for levels 2-7.
    
    ELEMENTO RETRIBUTIVO (levels 8, 9, 8Q, 9Q): per the official CNEL/CONFIMI text, categories 8 and 9 carry an 'elemento retributivo' of EUR 59.39/month fixed alongside the minimo. Modelled as a fixed_allowance with code ELEMENTO_RETRIBUTIVO.
    
    FUNZIONE QUADRO (levels 8Q, 9Q): quadri in cat.8 receive EUR 49.06/month and in cat.9 EUR 69.72/month as 'funzione quadro'. Modelled as fixed_allowance FUNZIONE_QUADRO. Amounts treated as perpetual; future tranche indexation not sourced.
    
    CATEGORY ELIMINATION: Art. of the CCNL eliminated Category 1 from 2022-01-01; workers formerly in cat.1 automatically moved to cat.2. This JSON models levels 2-9 (plus 8Q/9Q) as in force from 2026-06-01.
    
    SALARY TRANCHES: the October 2025 renewal schedules the first increase at 2026-06-01 (no tranche at signature). Three tranches modelled: 2026-06-01, 2027-06-01, 2028-06-01.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week x 52/12). Confirmed by kitech.it and the official CCNL text for calculation of hourly pay.
    
    MONTHLY PAYMENTS: 13 (tredicesima only). Source: ilccnl.it and official CNEL PDF.
    
    SENIORITY: 5 biennali. Amounts from the official CNEL C01A text: cat.2=21.59, cat.3=25.05, cat.4=26.75, cat.5=29.64, cat.6=32.43, cat.7=36.41, cat.8=40.95, cat.9=45.96. Levels 8Q and 9Q use the same scatto as cat.8 and cat.9 respectively.
    
    INPS: uses 2026-industria.json. Standard industry rates.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/metalmeccanico-confimi-pmi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanico-confimi-pmi.py"
```
