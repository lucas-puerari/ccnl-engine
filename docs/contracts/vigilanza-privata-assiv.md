# CCNL Istituti e Imprese di Vigilanza Privata e Servizi Fiduciari — ASSIV/ANIVP/UNIV (GPG)

| | |
|---|---|
| **CNEL code** | `HV40` |
| **Sector** | vigilanza-privata |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-05-30 |
| **Workers (est.)** | ~85k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSIV
    - ANIVP
    - UNIV
    - Legacoop Produzione e Servizi
    - AGCI Servizi
    - Confcooperative Lavoro e Servizi
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| `Q` | GPG Senior Manager (Quadro) — maximum operational and managerial responsibility | € 2,434.74 | — |
| `1` | GPG Grade 1 — security guard with operational responsibilities | € 2,086.89 | — |
| `2` | GPG Grade 2 — highly specialist security guard | € 1,946.09 | — |
| `3` | GPG Grade 3 — specialist security guard | € 1,723.31 | — |
| `4` | GPG Grade 4 — qualified security guard (contractual reference level) | € 1,528.88 | — |
| `5` | GPG Grade 5 — security guard with specific qualification | € 1,450.44 | — |
| `6` | GPG Grade 6 — security guard, basic duties | € 1,350.44 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 31.30 |
| `1` | € 26.12 |
| `2` | € 23.83 |
| `3` | € 22.46 |
| `4` | € 21.13 |
| `5` | € 20.52 |
| `6` | € 19.66 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `6`, `5`, `4`, `3`, `2`, `1`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS: reuses 2026-terziario.json. SIMPLIFICATION: tax_sector='terziario' is a modelling choice. Supporting facts: ASSIV/ANIVP/UNIV are not Confindustria members; private security companies do not access CIGO; the sector uses Ebivip (Ente Bilaterale Vigilanza Privata) for bilateral welfare, not INPS integration schemes. TERZIARIO is the standard classification for non-Confindustria services sector employers in INPS circular IVS rates. Counterargument: some aspects of the sector (24/7 operations, shift work) could suggest INDUSTRIA classification. At ≤50 employees, delta = 28.98% (TERZIARIO) vs 30.20% (INDUSTRIA), difference ~1.22pp employer contribution rate.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-05-30 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=30121:vigilanza452023&catid=257&Itemid=139) |
| — | — | 2024-11-21 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=33337:servizi-vigilanza-privata-e-servizi-fiduciari-ccnl,-21-novembre-2024&catid=262&Itemid=139) |
| — | — | 2024-11-21 | [↗](https://www.univigilanza.it/263/CODICE-ALFANUMERICO-UNICO-DEI-CCNL-.html) |
| — | — | 2023-07-19 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=30385:vigilanza-privata19723&catid=257&Itemid=139) |

??? note "Coverage notes"
    SCOPE: GPG section only (Guardie Particolari Giurate, livelli Q e 1-6). The Servizi Fiduciari/Sicurezza section (livelli A-E, 9 tranches from 01/08/2022) is a distinct salary table and would be a separate data file.
    
    CNEL CODE: HV40 confirmed from primary source: univigilanza.it (UNIV is a signatory employer association), article titled 'Codice Alfanumerico Unico dei CCNL' — 'L'attuale codice di riferimento per il settore vigilanza privata è il HV40.'
    
    SALARY MODEL: conglobated (paga base tabellare conglobata). Sources: (1) 2024 integrative accord salary table header reads 'Paga Conglobata' explicitly; (2) Art. 112 base CCNL 2013: 'stipendio o salario unico nazionale (paga base tabellare conglobata).' Back-calculation: 4° livello 01/06/2023 = 1328.88 / 173 = 7.68 EUR/h; 1° livello = 1772.60 / 173 = 10.25 EUR/h; Q = 2049.03 / 173 = 11.84 EUR/h. Non-integer results confirm conglobated total (not an integer-multiple hourly rate), consistent with historical accumulation of contingenza increments. fixed_allowances=[] for all levels.
    
    SALARY TRANCHES: 6 tranches modelled (01/06/2023 → 01/12/2026) from the 2024 integrative accord 'Tabelle Retributive' (PDF, 2 pages). A prior 01/03/2016 historical column is also present but predates current renewal scope and is not modelled. Source: 2024 integrative accord signed by all 9 signatories.
    
    LEVEL ORDERING: CCNL numbering is counter-intuitive — level '6' is the entry level (lowest salary) and 'Q' (Quadro) is the highest. order=1 corresponds to level 6 (lowest), order=7 to level Q (highest). Salary strictly monotone across all 6 tranches: verified.
    
    HOURLY DIVISOR: 173. Source: Art. 115 base CCNL 2013 — 'dividendo convenzionalmente la retribuzione stessa per 173.' Consistent with 40h/week standard (Art. 71, base CCNL 2013).
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Source: Art. 117 base CCNL 2013. Confirmed applicable to part-time workers too (Art. 64, base CCNL 2013).
    
    APPRENTICESHIP professionalizzante, 100% of the destination level for the whole period (CCNL 21/11/2024 Art. 86, olympus.uniurb.it: 'L'Apprendista ha diritto per tutta la durata del periodo di apprendistato all'inquadramento e alla corrispondente retribuzione del livello finale di collocazione'), max 36 months (Art. 82). The track covers GPG levels 6 to 1; Quadri are not a destination.
    
    SENIORITY triennale (36 months), max 6 scatti; per-level amounts from Art. 111 base CCNL 2013 (Q=31.30, 1°=26.12, 2°=23.83, 3°=22.46, 4°=21.13, 5°=20.52, 6°=19.66), effective 01/02/2013 and assumed current: the 2023 accord (30/05/2023) covers salary tranches and una tantum only, the 2024 integrative accord salary tables only. The 2023 clause on 'permanenza nei Livelli VI e V ... da 24 a 18 mesi' concerns classificatory progression, not seniority.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/vigilanza-privata-assiv.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/vigilanza-privata-assiv.py"
```
