# ccnl-engine

A Python library for modeling Italian collective labor agreements (CCNL) as structured, versioned data and computing gross-to-net salary and employer cost from first principles.

## Why

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values — they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
compute(ccnl, level, date, rules, employment) → ComputationResult
```

## Quickstart

```python
from datetime import date
from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.engine.compute import compute
from ccnl_engine.models.ccnl import TaxSector
from ccnl_engine.models.employment import Permanent

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, TaxSector.TERZIARIO, num_employees=50)
result = compute(ccnl, "4", date(2026, 9, 1), rules, Permanent())

print(result.net_annual)  # → Decimal('...')
print(result.employer_cost_annual)  # → Decimal('...')
```

## CCNL coverage

*Layers legend*

| Layer | Meaning |
| ----- | ------- |
| **Layer 1** | base salary, seniority increments (*scatti di anzianità*), fixed allowances, additional months. |
| **Layer 2** | part-time, fixed-term (NASpI *addizionale*), apprenticeship (percentage or under-classification). |
| **Layer 3** | overtime, night/holiday premiums, leave accruals, sick-pay integrations. Out of scope for now. |

*Status legend*

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented |
| ⚠️ | Partial (documented simplifications or missing sub-tracks) |
| — | Out of scope |

*CCNL Matrix*

| # | CCNL | Sector | Lavoratori (~)<sup><a id="ref-1" href="#fn-1">1</a></sup> | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---:|:---:|:---:|:---:|
| 1 | Commercio — Confcommercio | Terziario | ~800k | ✅ | ✅ | — |
| 2 | Metalmeccanico — Federmeccanica/Assistal | Industria | ~1,7M | ✅ | ✅ | — |
| 3 | Metalmeccanico PMI — Unionmeccanica-Confapi | Industria | ~350k | ✅ | ✅ | — |
| 4 | Chimica-Farmaceutica — Federchimica/Farmindustria/Assistal | Industria | ~210k | ✅ | ✅ | — |
| 5 | Turismo — Confcommercio | Terziario | ~300k | ✅ | ✅ | — |
| 6 | Edilizia — ANCE | Edilizia | ~550k | ✅ | ✅ | — |
| 7 | Cooperative Sociali — Confcooperative/Legacoop/AGCI | Terziario | ~380k | ✅ | ✅ | — |
| 8 | Logistica, Trasporto Merci e Spedizione — Confetra | Industria | ~430k | ✅ | ✅ | — |
| 9 | Servizi di Pulizia e Multiservizi — ANIP-Confindustria | Terziario | ~580k | ✅ | ✅ | — |
| 10 | Studi e Attività Professionali — Confprofessioni | Terziario | ~350k | ✅ | ✅ | — |
| 11 | Credito — ABI | Credito | ~270k | ✅ | ✅ | — |
| 12 | Tessile Abbigliamento Moda — SMI | Industria | ~160k | ✅ | ✅ | — |
| 13 | Alimentari Industria — Federalimentare | Industria | ~145k | ✅ | ✅ | — |
| 14 | Distribuzione Moderna Organizzata — Federdistribuzione | Terziario | ~460k | ✅ | ✅ | — |
| 15 | Metalmeccanica e Installazione Impianti — Artigianato | Artigianato | ~350k | ✅ | ✅ | — |
| 16 | Gomma e Plastica Industria — Federazione Gomma Plastica | Industria | ~90k | ✅ | ✅ | — |
| 17 | Grafica e Editoria — AIEG-Acigraf | Industria | ~70k | ✅ | ✅ | — |
| 18 | Carta e Cartone — Assocarta | Industria | ~35k | ✅ | ✅ | — |
| 19 | Telecomunicazioni — Asstel | Industria | ~110k | ✅ | ✅ | — |
| 20 | Vigilanza Privata — ASSIV/ANIVP/UNIV (GPG) | Terziario | ~85k | ✅ | ✅ | — |
| 21 | Legno e Arredamento — Federlegno-Arredo | Industria | ~90k | ✅ | ✅ | — |
| 22 | Edilizia e Affini — CNA/Confartigianato/Casartigiani | Artigianato | ~350k | ✅ | ✅ | — |
| 23 | Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas | Industria | ~65k | ✅ | ✅ | — |
| 24 | Istituzioni Socio-Assistenziali — UNEBA | Terziario | ~130k | ✅ | ✅ | — |
| 25 | Acconciatura ed Estetica — Confartigianato/CNA | Artigianato | ~95k | ✅ | ✅ | — |
| 26 | Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA) | Artigianato | ~90k | ✅ | ✅ | — |
| 27 | Autoferrotranvieri e Internavigatori (Mobilita/TPL) — AGENS/ASSTRA/ANAV | Terziario | ~120k | ✅ | ✅ | — |
| 28 | Credito Cooperativo (BCC/CRA) — Federcasse | Credito | ~33k | ✅ | ✅ | — |
| 29 | Elettrico (produzione/distribuzione energia) — Elettricita Futura | Industria | ~60k | ✅ | ✅ | — |
| 30 | Calzaturiero (industria delle calzature) — Assocalzaturifici | Industria | ~75k | ✅ | ✅ | — |
| 31 | Area Tessile-Moda e Chimica-Ceramica — Artigianato (Confartigianato/CNA) | Artigianato | ~120k | ✅ | ✅ | — |
| 32 | Area Legno-Lapidei — Artigianato (Confartigianato/CNA) | Artigianato | ~95k | ✅ | ✅ | — |
| 33 | Area Comunicazione — Artigianato (Confartigianato/CNA) | Artigianato | ~60k | ✅ | ✅ | — |
| 34 | Ceramica Industria — Confindustria Ceramica (Assopiastrelle) | Industria | ~23k | ✅ | ✅ | — |
| 35 | Orafi e Argentieri — Federorafi | Industria | ~18k | ✅ | ✅ | — |
| 36 | Pelli e Cuoio Industria — Assopellettieri | Industria | ~17k | ✅ | ✅ | — |
| 37 | Pubblici Esercizi, Ristorazione Collettiva e Turismo — FIPE/ANGEM | Terziario | ~350k | ✅ | ✅ | — |
| 38 | Agenzie di Viaggio e Turismo — Fiavet/Confcommercio | Terziario | ~25k | ✅ | ✅ | — |
| 39 | Terziario Distribuzione e Servizi — Confesercenti | Terziario | ~230k | ✅ | ✅ | — |
| 40 | Turismo — Federalberghi/Faita | Terziario | ~220k | ✅ | ✅ | — |
| 41 | Funzioni Centrali 2022-2024 — ARAN (Ministeri, Agenzie, INPS, INAIL) | Pubblica Amministrazione | ~250k | ✅ | — | — |
| 42 | Funzioni Locali 2022-2024 — ARAN (Comuni, Province, Regioni, Camere di Commercio) | Pubblica Amministrazione | ~400k | ✅ | — | — |
| 43 | Comparto Sanità 2022-2024 — ARAN (SSN non-dirigenza) | Pubblica Amministrazione | ~580k | ✅ | — | — |
| 44 | Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN) | Pubblica Amministrazione | ~100k | ✅ | — | — |
| 45 | Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi) | Pubblica Amministrazione | ~37k | ✅ | — | — |

<p id="fn-1"><a href="#ref-1">1.</a> Approximate estimates. Sources: CNEL, INPS, Ministero del Lavoro, CCNL renewal communications.</p>

## What is not modelled

- Addizionali regionali and addizionali comunali
- Detrazioni per carichi di famiglia (Art. 12 TUIR)
- IVS contributory ceiling split (Art. 1 L. 335/1995)
- Second-level bargaining (territorial and company agreements)
- Bilateral system contributions (EST, Fon.Te, …)
- Overtime, premiums, and leave (Layer 3)

Each limitation is documented in the relevant data file's `coverage.notes` field and marked with `# SIMPLIFICATION:` comments in the engine source.

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.
