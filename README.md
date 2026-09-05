# ccnl-engine

[![PyPI version](https://img.shields.io/pypi/v/ccnl-engine?logo=pypi&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine?logo=python&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![CI](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/lucas-puerari/ccnl-engine/graph/badge.svg)](https://codecov.io/gh/lucas-puerari/ccnl-engine)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python library for modeling Italian collective labor agreements (CCNL) as structured, versioned data and computing gross-to-net salary and employer cost from first principles.

**[Interactive demo](https://lucas-puerari.github.io/ccnl-engine/demo/) · [API docs](https://lucas-puerari.github.io/ccnl-engine/docs/)**

## Why

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values — they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
compute(ccnl, rules, Scenario(...)) → Payslip
```

## Quickstart

```python
from datetime import date
from ccnl_engine import Scenario, Permanent, TaxSector, compute, load_ccnl, load_year_rules

ccnl = load_ccnl("commercio-confcommercio.json")
scenario = Scenario(
    level_code="4",
    as_of=date(2026, 9, 1),
    employment=Permanent(),
    num_employees=50,
)
rules = load_year_rules(2026, TaxSector.TERZIARIO, scenario.num_employees)
payslip = compute(ccnl, rules, scenario)

print(payslip.net_annual)              # → Decimal('...')
print(payslip.trattamento_integrativo) # → Decimal('...') — Art. 1 D.L. 3/2020 bonus
print(payslip.fiscal_simplifications)  # → frozenset of items not computed by the engine
print(payslip.employer_cost_annual)    # → Decimal('...')
```

## CCNL coverage

*Layers legend*

| Layer | Meaning |
| ----- | ------- |
| **Layer 1** | base salary, seniority increments (*scatti di anzianità*), fixed allowances, additional months. |
| **Layer 2** | part-time, fixed-term (NASpI *addizionale*), apprenticeship (percentage or under-classification). |

*Status legend*

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully modelled; all salary tables and rules for this layer are in scope |
| ⚠️ | Partially modelled; known gaps or simplifications apply — see `coverage.notes` in the contract's JSON data file |
| 🤖 | Extraction: extracted automatically via Claude Code — no manual human review |
| 🧑 | Extraction: verified manually against the official source |

*CCNL Matrix*

| # | Codice CNEL | CCNL | Sector | Lavoratori (~)<sup><a id="ref-1" href="#fn-1">1</a></sup> | Layer 1 | Layer 2 | Extraction<sup><a id="ref-2" href="#fn-2">2</a></sup> |
|---|---|---|---|---:|:---:|:---:|:---:|
| 1 | H011 | Commercio — Confcommercio | Terziario | ~800k | ✅ | ✅ | 🤖 |
| 2 | C011 | Metalmeccanico — Federmeccanica/Assistal | Industria | ~1,7M | ✅ | ✅ | 🤖 |
| 3 | C018 | Metalmeccanico PMI — Unionmeccanica-Confapi | Industria | ~350k | ✅ | ✅ | 🤖 |
| 4 | B011 | Chimica-Farmaceutica — Federchimica/Farmindustria/Assistal | Industria | ~210k | ✅ | ✅ | 🤖 |
| 5 | H052 | Turismo — Confcommercio | Terziario | ~300k | ✅ | ✅ | 🤖 |
| 6 | F012 | Edilizia — ANCE | Edilizia | ~550k | ✅ | ✅ | 🤖 |
| 7 | T151 | Cooperative Sociali — Confcooperative/Legacoop/AGCI | Terziario | ~380k | ✅ | ✅ | 🤖 |
| 8 | I100 | Logistica, Trasporto Merci e Spedizione — Confetra | Industria | ~430k | ✅ | ✅ | 🤖 |
| 9 | K511 | Servizi di Pulizia e Multiservizi — ANIP-Confindustria | Terziario | ~580k | ✅ | ✅ | 🤖 |
| 10 | H442 | Studi e Attività Professionali — Confprofessioni | Terziario | ~350k | ✅ | ✅ | 🤖 |
| 11 | J241 | Credito — ABI | Credito | ~270k | ✅ | ✅ | 🤖 |
| 12 | D014 | Tessile Abbigliamento Moda — SMI | Industria | ~160k | ✅ | ✅ | 🤖 |
| 13 | E012 | Alimentari Industria — Federalimentare | Industria | ~145k | ✅ | ✅ | 🤖 |
| 14 | H008 | Distribuzione Moderna Organizzata — Federdistribuzione | Terziario | ~460k | ✅ | ✅ | 🤖 |
| 15 | C030 | Metalmeccanica e Installazione Impianti — Artigianato | Artigianato | ~350k | ✅ | ✅ | 🤖 |
| 16 | B371 | Gomma e Plastica Industria — Federazione Gomma Plastica | Industria | ~90k | ✅ | ✅ | 🤖 |
| 17 | G011 | Grafica e Editoria — AIEG-Acigraf | Industria | ~70k | ✅ | ✅ | 🤖 |
| 18 | G022 | Carta e Cartone — Assocarta | Industria | ~35k | ✅ | ✅ | 🤖 |
| 19 | K411 | Telecomunicazioni — Asstel | Industria | ~110k | ✅ | ✅ | 🤖 |
| 20 | HV40 | Vigilanza Privata — ASSIV/ANIVP/UNIV (GPG) | Terziario | ~85k | ✅ | ✅ | 🤖 |
| 21 | F051 | Legno e Arredamento — Federlegno-Arredo | Industria | ~90k | ✅ | ✅ | 🤖 |
| 22 | F015 | Edilizia e Affini — CNA/Confartigianato/Casartigiani | Artigianato | ~350k | ✅ | ✅ | 🤖 |
| 23 | K321 | Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas | Industria | ~65k | ✅ | ✅ | 🤖 |
| 24 | T141 | Istituzioni Socio-Assistenziali — UNEBA | Terziario | ~130k | ✅ | ✅ | 🤖 |
| 25 | H515 | Acconciatura ed Estetica — Confartigianato/CNA | Artigianato | ~95k | ✅ | ✅ | 🤖 |
| 26 | E015 | Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA) | Artigianato | ~90k | ✅ | ✅ | 🤖 |
| 27 | I022 | Autoferrotranvieri e Internavigatori (Mobilita/TPL) — AGENS/ASSTRA/ANAV | Terziario | ~120k | ✅ | ✅ | 🤖 |
| 28 | J271 | Credito Cooperativo (BCC/CRA) — Federcasse | Credito | ~33k | ✅ | ✅ | 🤖 |
| 29 | K051 | Elettrico (produzione/distribuzione energia) — Elettricita Futura | Industria | ~60k | ✅ | ✅ | 🤖 |
| 30 | D121 | Calzaturiero (industria delle calzature) — Assocalzaturifici | Industria | ~75k | ✅ | ✅ | 🤖 |
| 31 | V751 | Area Tessile-Moda e Chimica-Ceramica — Artigianato (Confartigianato/CNA) | Artigianato | ~120k | ✅ | ✅ | 🤖 |
| 32 | F060 | Area Legno-Lapidei — Artigianato (Confartigianato/CNA) | Artigianato | ~95k | ✅ | ✅ | 🤖 |
| 33 | G016 | Area Comunicazione — Artigianato (Confartigianato/CNA) | Artigianato | ~60k | ✅ | ✅ | 🤖 |
| 34 | B122 | Ceramica Industria — Confindustria Ceramica (Assopiastrelle) | Industria | ~23k | ✅ | ✅ | 🤖 |
| 35 | C021 | Orafi e Argentieri — Federorafi | Industria | ~18k | ✅ | ✅ | 🤖 |
| 36 | D111 | Pelli e Cuoio Industria — Assopellettieri | Industria | ~17k | ✅ | ✅ | 🤖 |
| 37 | H05Y | Pubblici Esercizi, Ristorazione Collettiva e Turismo — FIPE/ANGEM | Terziario | ~350k | ✅ | ✅ | 🤖 |
| 38 | H052 | Agenzie di Viaggio e Turismo — Fiavet/Confcommercio | Terziario | ~25k | ✅ | ✅ | 🤖 |
| 39 | H012 | Terziario Distribuzione e Servizi — Confesercenti | Terziario | ~230k | ✅ | ✅ | 🤖 |
| 40 | H052 | Turismo — Federalberghi/Faita | Terziario | ~220k | ✅ | ✅ | 🤖 |
| 41 | S005 | Funzioni Centrali 2022-2024 — ARAN (Ministeri, Agenzie, INPS, INAIL) | Pubblica Amministrazione | ~250k | ✅ | ✅ | 🤖 |
| 42 | S105 | Funzioni Locali 2022-2024 — ARAN (Comuni, Province, Regioni, Camere di Commercio) | Pubblica Amministrazione | ~400k | ✅ | ✅ | 🤖 |
| 43 | S205 | Comparto Sanità 2022-2024 — ARAN (SSN non-dirigenza) | Pubblica Amministrazione | ~580k | ✅ | ✅ | 🤖 |
| 44 | S225 | Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN) | Pubblica Amministrazione | ~100k | ✅ | ✅ | 🤖 |
| 45 | S225 | Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi) | Pubblica Amministrazione | ~37k | ✅ | ✅ | 🤖 |
| 46 | S125 | Area Dirigenza Funzioni Locali 2022-2024 — ARAN (Dirigenti enti locali, Segretari comunali) | Pubblica Amministrazione | ~13k | ✅ | ✅ | 🤖 |
| 47 | S025 | Area Dirigenza Funzioni Centrali 2022-2024 — ARAN (Dirigenti ministeri, agenzie fiscali, INPS, INAIL) | Pubblica Amministrazione | ~30k | ✅ | ✅ | 🤖 |
| 48 | S325 | Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN (Dirigenti scolastici, universitari, ricerca) | Pubblica Amministrazione | ~8k | ✅ | ✅ | 🤖 |
| 49 | S305 | Comparto Istruzione e Ricerca 2022-2024 — ARAN (Docenti e ATA scuola, università, ricerca) | Pubblica Amministrazione | ~1,2M | ✅ | ✅ | 🤖 |
| 50 | T011 | Case di Cura Private - Personale Non Medico (AIOP/ARIS) | Sanità privata | ~150k | ✅ | ✅ | 🤖 |
| 51 | H501 | Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi) | Lavoro Domestico | ~900k | ✅ | ✅ | 🤖 |
| 52 | H501 | Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi) | Lavoro Domestico | ~900k | ✅ | ✅ | 🤖 |
| 53 | A011 | Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA | Agricoltura | ~600k | ✅ | ✅ | 🤖 |
| 54 | B018 | Chimica e Affini PMI — Unionchimica Confapi | Chimica | ~56k | ✅ | ✅ | 🤖 |
| 55 | E023 | Panificazione e Settori Affini Industria — Assipan/Fiesa/Federpanificatori | Alimentare | ~20k | ✅ | ✅ | 🤖 |
| 56 | I320 | Attività Ferroviarie — AGENS | Trasporto | ~75k | ✅ | ✅ | 🤖 |
| 57 | I810 | Trasporto Aereo — Gestori Aeroportuali (Assaeroporti) | Trasporto | ~40k | ✅ | ✅ | 🤖 |
| 58 | K540 | Igiene Ambientale — Servizi Ambientali e di Igiene Urbana (Utilitalia/FISE) | Industria | ~65k | ✅ | ✅ | 🤖 |
| 59 | A021 | Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti | Agricoltura | ~80k | ✅ | ✅ | 🤖 |
| 60 | — | Forze di Polizia ad ordinamento civile 2022-2024 — DPR 53/2025 (Polizia di Stato, Polizia Penitenziaria) | Pubblica Amministrazione | ~130k | ✅ | ✅ | 🤖 |
| 61 | G029 | Comunicazione, Informatica e Servizi Innovativi PMI — Unimatica-Confapi (Settore Informatico) | Industria | ~20k | ✅ | ✅ | 🤖 |
| 62 | T241 | Istituzioni Formative Private (Scuole Private Religiose) — AGIDAE | Terziario | ~50k | ✅ | ⚠️ | 🤖 |
| 63 | J121 | Assicurazioni — ANIA | Credito | ~45k | ✅ | ⚠️ | 🤖 |
| 64 | B254 | Energia e Petrolio — Confindustria Energia | Industria | ~38k | ✅ | ✅ | 🤖 |
| 65 | H016 | Distribuzione Cooperativa — ANCC-Coop | Terziario | ~63k | ⚠️ | ✅ | 🤖 |
| 66 | D0L1 | Lavanderie Industriali — Assosistema (turismo) | Industria | ~17k | ⚠️ | ✅ | 🤖 |
| 67 | H601 | CED, ICT, Professioni Digitali e STP — Assoced | Terziario | ~22k | ✅ | ✅ | 🤖 |
| 68 | A051 | Attivita Agromeccaniche (Contoterzismo) — CAI Agromec | Agricoltura | ~4k | ✅ | ✅ | 🤖 |
| 69 | A131 | Consorzi di Bonifica — SNEBI | Agricoltura | ~4k | ✅ | ✅ | 🤖 |
| 70 | A141 | Consorzi Agrari — ASSOCAP | Agricoltura | ~2k | ✅ | ✅ | 🤖 |
| 71 | A221 | Organizzazioni Allevatori e Enti Zootecnici — AIA | Agricoltura | ~2k | ✅ | ✅ | 🤖 |

<p id="fn-1"><a href="#ref-1">1.</a> Approximate estimates. Sources: CNEL, INPS, Ministero del Lavoro, CCNL renewal communications.</p>

<p id="fn-2"><a href="#ref-2">2.</a> Salary tables were extracted from official CCNL documents using Claude Code (AI-assisted), without manual human review. Values should be verified against the official source before use in production payroll systems.</p>

The 62 contracts above cover approximately **14.5 million workers** (sum of per-CCNL estimates; some overlap is possible where sector boundaries are not mutually exclusive, so the unique-worker count is somewhat lower). Italy has roughly **16 million employees** covered by some collective agreement (ISTAT/CNEL 2024, public and private sectors combined). This library therefore reaches an estimated **~85–90% of CCNL-covered workers** on a gross-headcount basis.

## What is not modelled

- Addizionali regionali and addizionali comunali
- Detrazioni per carichi di famiglia (Art. 12 TUIR)
- IVS contributory ceiling split (Art. 1 L. 335/1995)
- Second-level bargaining (territorial and company agreements)
- Bilateral system contributions (EST, Fon.Te, …)
- Overtime, night/holiday premiums, leave accruals, sick-pay integrations

See [API docs](https://lucas-puerari.github.io/ccnl-engine/docs/) for full detail.

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.
