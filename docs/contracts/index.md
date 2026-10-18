<!-- auto-generated -- run: uv run python scripts/documentation/coverage_matrix/generate.py -->
<!-- generated: 2026-10-18 -->

# CCNL Coverage

132 bundled contract configurations, private and public sector,
including ARAN public-sector agreements and one Presidential Decree
(DPR 53/2025[^2]). The table is generated from the data: search it, or use
`search_ccnls()` from Python.

→ [Domain: What is a CCNL](../domain/index.md) ·
[Capability matrix](capability-matrix.md)

## Three separate axes

No percentage blends them: a contract can be fully covered and still rest
on unverified sources, or be well sourced and not cleared for production.

- **Coverage:** what the engine computes, from the capability registry of
  2027. **Core** is the path every run takes; **Limits** names the
  capabilities this contract's data leave partial (a `missing` note, or a
  model limitation with a monetary impact). The scenario features and the
  ones outside the input are the same for every contract and are listed
  below.
- **Sources:** payable rules of the contract file by provenance status,
  verified / derived / assumed / missing.
- **Readiness:** the review tier of the contract ruleset.

**Core payroll path: computed on every run of every contract** (20):

- ✅ `base_salary` (native)
- ✅ `seniority` (native)
- ✅ `worker_category` (native)
- ✅ `inps_employee` (native)
- ✅ `inps_employer` (native)
- ✅ `tfr` (native)
- ✅ `tfr_revaluation` (native)
- ✅ `irpef` (native)
- ✅ `trattamento_integrativo` (native)
- ✅ `ulteriore_detrazione_lavoro` (native)
- ✅ `somma_esente` (native)
- ✅ `withholding_shortfall` (native)
- ✅ `shortfall_deferral` (native)
- ✅ `addizionale_regionale` (native)
- ✅ `addizionale_comunale` (native)
- ✅ `family_deductions` (native)
- ✅ `bonus_pdr` (native)
- ✅ `rinnovo_substitute_tax` (native)
- ✅ `notte_festivi_turni_substitute_tax` (native)
- ✅ `assistance_contribution` (native)

**Scenario features: computed when the request declares the event, the fact or the termination** (16):

- 🔲 `termination_residual_leave` (unsupported)
- 📝 `termination_tfr` (caller_supplied)
- 📝 `contract_renewal_arrears` (caller_supplied)
- ⚠️ `foreign_tax_credit` (partial)
- 📝 `overtime` (caller_supplied)
- 📝 `night_work` (caller_supplied)
- 📝 `holiday_work` (caller_supplied)
- 📝 `shift_work` (caller_supplied)
- ✅ `standby` (native)
- 📝 `absence` (caller_supplied)
- ✅ `sickness` (native)
- ✅ `fringe_benefit` (native)
- 📝 `travel_allowance` (caller_supplied)
- ✅ `welfare` (native)
- 📝 `bilateral_funds` (caller_supplied)
- ⚠️ `pension_fund_contribution` (partial)

**Outside the input: the request has no field for the fact, so the engine does not compute them** (14):

- 🔲 `inail` (unsupported)
- 🔲 `contribution_exemption` (unsupported)
- 🔲 `fiscal_adjustment` (unsupported)
- 🔲 `maternity_leave` (unsupported)
- 🔲 `workplace_injury` (unsupported)
- 🔲 `una_tantum` (unsupported)
- 🔲 `personal_withholdings` (unsupported)
- 🔲 `additional_irpef_base` (unsupported)
- 🔲 `health_fund_employee` (unsupported)
- 🔲 `health_fund_employer` (unsupported)
- 🔲 `territorial_supplement` (unsupported)
- 🔲 `company_supplement` (unsupported)
- 🔲 `art15_deductions` (unsupported)
- 🔲 `leave` (unsupported)

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | Readiness and extraction |
|---|---|
| 🧪 | Exploratory — demo, research, prototyping only |
| 👁 | Reviewed — key values human-verified; use with disclaimer |
| 🏭 | Production — full review, reference case, named owner |
| 🤖 | Machine extracted |
| 🧑 | Human reviewed |

## Matrix

| # | CNEL | CCNL | Sector | Workers (~)[^3] | Renewal | Core | Limits | Sources (v / d / a / m) | Readiness | Ext[^4] |
|---|---|---|---|---:|:---:|:---:|---|---|:---:|:---:|
| 1 | H515 | [CCNL Acconciatura ed Estetica — Confartigianato/CNA](acconciatura-estetica-confartigianato.md) | acconciatura ed estetica | ~95k | — | ⚠️ | base_salary, inps_employer | 0 / 29 / 1 / 0 | 🧪 | 🤖 |
| 2 | I481 | [CCNL Agenzie Marittime Raccomandatarie, Agenzie Aeree e Mediatori Marittimi](agenzie-marittime-i481.md) | Agenzie marittime e aeree | ~5k | 2024 | ⚠️ | base_salary, seniority | 0 / 36 / 2 / 0 | 🧪 | 🤖 |
| 3 | H052 | [CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio](agenzie-viaggio-fiavet.md) | Turismo (agenzie di viaggio) | ~25k | 2024 | ⚠️ | seniority, trattamento_integrativo | 0 / 68 / 1 / 1 | 🧪 | 🤖 |
| 4 | E016 | [CCNL Alimentaristi Cooperative (Fedagripesca/Legacoop Agroalimentare/AGCI-Agrital)](alimentaristi-cooperative-e016.md) | industria alimentare — cooperative di produzione e lavoro | ~15k | 2024 | ⚠️ | base_salary, seniority | 0 / 70 / 1 / 1 | 🧪 | 🤖 |
| 5 | E015 | [CCNL Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)](panificazione-artigianato-confartigianato.md) | panificazione e alimentazione artigianato | ~90k | — | ⚠️ | inps_employer, territorial_supplement | 1 / 47 / 0 / 0 | 🧪 | 🤖 |
| 6 | G016 | [CCNL Area Comunicazione — Artigianato](comunicazione-artigianato-confartigianato.md) | comunicazione grafica editoria stampa artigianato | ~60k | 2024 | ⚠️ | base_salary, inps_employer, worker_category | 0 / 40 / 1 / 0 | 🧪 | 🤖 |
| 7 | S025 | [CCNL Area Dirigenza Funzioni Centrali 2022-2024 — ARAN](dirigenza-funzioni-centrali-aran.md) | Pubblica Amministrazione | ~30k | 2025 | ✅ | — | 0 / 13 / 0 / 0 | 🧪 | 🤖 |
| 8 | S125 | [CCNL Area Dirigenza Funzioni Locali 2022-2024 — ARAN](dirigenza-funzioni-locali-aran.md) | Pubblica Amministrazione | ~13k | 2026 | ✅ | — | 0 / 9 / 0 / 0 | 🧪 | 🤖 |
| 9 | S325 | [CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN](dirigenza-istruzione-ricerca-aran.md) | Pubblica Amministrazione | ~8k | 2026 | ✅ | — | 0 / 13 / 0 / 0 | 🧪 | 🤖 |
| 10 | F060 | [CCNL Area Legno-Lapidei — Artigianato](legno-lapidei-artigianato-confartigianato.md) | legno arredamento lapidei artigianato | ~95k | 2024 | ⚠️ | base_salary, inps_employer | 0 / 38 / 2 / 0 | 🧪 | 🤖 |
| 11 | S225 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)](dirigenza-sanitaria-medico-veterinaria-aran.md) | Pubblica Amministrazione | ~100k | 2026 | ⚠️ | base_salary | 0 / 8 / 1 / 1 | 🧪 | 🤖 |
| 12 | S225 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi, fisici, chimici)](dirigenza-sanitaria-area-sanita-aran.md) | Pubblica Amministrazione | ~37k | 2026 | ⚠️ | base_salary | 0 / 10 / 0 / 0 | 🧪 | 🤖 |
| 13 | V751 | [CCNL Area Tessile-Moda e Chimica-Ceramica — Artigianato](tessile-moda-artigianato-confartigianato.md) | tessile moda chimica ceramica artigianato | ~120k | 2024 | ⚠️ | base_salary, inps_employer, seniority | 0 / 36 / 1 / 0 | 🧪 | 🤖 |
| 14 | A051 | [CCNL Attivita Agromeccaniche (Contoterzismo) CAI Agromec-FAI-FLAI-UILA](contoterzismo-caiagromec.md) | Agricoltura | ~4k | 2024 | ⚠️ | inps_employer | 0 / 48 / 1 / 1 | 🧪 | 🤖 |
| 15 | B282 | [CCNL Attivita Minerarie (ASSORISORSE)](attivita-minerarie-assorisorse.md) | Industria estrattiva - Miniere, cave, saline, metallurgia estrattiva | ~3000 | 2022 | ⚠️ | seniority | 36 / 0 / 2 / 1 | 🧪 | 🤖 |
| 16 | I320 | [CCNL Attività Ferroviarie — AGENS](trasporto-ferroviario-agens.md) | trasporto | ~75k | 2025 | ⚠️ | base_salary, seniority | 0 / 55 / 1 / 1 | 🧪 | 🤖 |
| 17 | I022 | [CCNL Autoferrotranvieri e Internavigatori (Mobilita/TPL)](autoferrotranvieri-internavigatori.md) | trasporti | ~120k | 2024 | ⚠️ | inps_employer, seniority | 0 / 138 / 1 / 1 | 🧪 | 🤖 |
| 18 | IC35 | [CCNL Autorimesse, Noleggio Automezzi e Parcheggi (ANIASA)](autorimesse-ic35.md) | Autorimesse e noleggio automezzi | ~41k | 2025 | ⚠️ | base_salary, seniority | 0 / 95 / 1 / 1 | 🧪 | 🤖 |
| 19 | I192 | [CCNL Autostrade e Trafori Concessionari](autostrade-trafori.md) | autostrade e trafori — addetti alle concessionarie autostradali | ~15k | 2023 | ⚠️ | seniority | 0 / 140 / 1 / 1 | 🧪 | 🤖 |
| 20 | H601 | [CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)](ced-assoced.md) | Terziario | ~22k | 2025 | ⚠️ | base_salary, inps_employer | 0 / 44 / 1 / 1 | 🧪 | 🤖 |
| 21 | G022 | [CCNL Carta e Cartone — Aziende Industriali (Assocarta)](carta-cartone-assocarta.md) | carta-cartone | ~35k | 2026 | ⚠️ | seniority | 0 / 74 / 2 / 0 | 🧪 | 🤖 |
| 22 | T011 | [CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)](sanita-privata-aiop-aris.md) | Sanità privata | ~150k | 2020 | ✅ | overtime | 36 / 1 / 0 / 0 | 🧪 | 🤖 |
| 23 | F032 | [CCNL Cemento, Calce e Gesso — Industria (Federbeton)](cemento-calce-gesso-industria.md) | industria del cemento calce e gesso | ~25k | — | ⚠️ | base_salary, seniority | 0 / 80 / 2 / 0 | 🧪 | 🤖 |
| 24 | B122 | [CCNL Ceramica Industria (Confindustria-Assopiastrelle)](ceramica-industria-confindustria.md) | ceramica | ~23k | — | ⚠️ | seniority | 0 / 60 / 1 / 1 | 🧪 | 🤖 |
| 25 | B018 | [CCNL Chimica e Affini PMI — Unionchimica Confapi](chimica-affini-pmi-unionchimica.md) | chimica | ~56k | 2026 | ⚠️ | base_salary, seniority | 0 / 21 / 1 / 1 | 🧪 | 🤖 |
| 26 | S005 | [CCNL Comparto Funzioni Centrali — Triennio 2022-2024](funzioni-centrali-aran.md) | Pubblica Amministrazione — Comparto Funzioni Centrali | ~250k | 2026 | ✅ | — | 26 / 5 / 0 / 0 | 👁 | 🧑 |
| 27 | S105 | [CCNL Comparto Funzioni Locali 2022-2024 — ARAN](funzioni-locali-aran.md) | Pubblica Amministrazione | ~400k | 2026 | ⚠️ | base_salary | 18 / 9 / 0 / 0 | 👁 | 🧑 |
| 28 | S305 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN](istruzione-ricerca-aran.md) | Pubblica Amministrazione | ~1,2M | 2026 | ⚠️ | inps_employee, overtime | 48 / 41 / 1 / 0 | 🧪 | 🤖 |
| 29 | S305 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, AFAM (Alta formazione artistica, musicale e coreutica)](afam-aran.md) | Pubblica Amministrazione | ~1,2M | 2026 | ✅ | pension_fund_contribution, sickness | 24 / 13 / 2 / 0 | 🧪 | 🤖 |
| 30 | S305 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, Enti pubblici di ricerca (ASI compresa)](enti-ricerca-aran.md) | Pubblica Amministrazione | ~1,2M | 2026 | ⚠️ | base_salary, pension_fund_contribution, sickness | 32 / 4 / 1 / 0 | 🧪 | 🤖 |
| 31 | S305 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, Università (personale tecnico-amministrativo e CEL)](universita-aran.md) | Pubblica Amministrazione | ~1,2M | 2026 | ✅ | pension_fund_contribution, sickness | 20 / 4 / 5 / 0 | 🧪 | 🤖 |
| 32 | S305 | [CCNL Comparto Istruzione e Ricerca 2025-2027 (trattamento economico) - ARAN, Università, tecnologi a tempo indeterminato](universita-tecnologi-aran.md) | Pubblica Amministrazione | ~1,2M | 2026 | ✅ | pension_fund_contribution, sickness | 2 / 4 / 1 / 0 | 🧪 | 🤖 |
| 33 | S205 | [CCNL Comparto Sanità 2022-2024 — ARAN](sanita-aran.md) | Pubblica Amministrazione | ~580k | 2025 | ⚠️ | base_salary | 16 / 5 / 0 / 0 | 👁 | 🧑 |
| 34 | G029 | [CCNL Comunicazione, Informatica e Servizi Innovativi PMI — Settore Informatico](informatica-pmi-unimatica.md) | informatica-servizi-innovativi | ~20k | — | ⚠️ | base_salary, seniority | 0 / 40 / 2 / 0 | 🧪 | 🤖 |
| 35 | A141 | [CCNL Consorzi Agrari (ASSOCAP-FLAI-FAI-UILA)](consorzi-agrari-assocap.md) | Agricoltura | ~2k | 2023 | ⚠️ | base_salary, health_fund_employer, inps_employer | 0 / 36 / 1 / 1 | 🧪 | 🤖 |
| 36 | A131 | [CCNL Consorzi di Bonifica (SNEBI-FLAI-FAI-FILBI)](consorzi-di-bonifica-snebi.md) | Agricoltura | ~4k | 2025 | ⚠️ | base_salary, inps_employer, seniority | 0 / 56 / 1 / 1 | 🧪 | 🤖 |
| 37 | T151 | [CCNL Cooperative Sociali (Confcooperative/Legacoop/AGCI)](cooperative-sociali.md) | servizi socio-assistenziali | ~380k | — | ⚠️ | base_salary, bilateral_funds, inps_employer | 62 / 1 / 0 / 0 | 👁 | 🧑 |
| 38 | A016 | [CCNL Cooperative e Consorzi Agricoli](cooperative-consorzi-agricoli.md) | cooperative e consorzi agricoli — impiegati e operai agricoli | ~60k | 2024 | ⚠️ | base_salary, inps_employer, seniority | 32 / 9 / 1 / 0 | 🧪 | 🤖 |
| 39 | T611 | [CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa](federcasa.md) | Case popolari | ~6k | 2024 | ✅ | — | 0 / 23 / 2 / 0 | 🧪 | 🤖 |
| 40 | E018 | [CCNL Dipendenti Piccola e Media Industria Alimentare (Unionalimentari-Confapi)](alimentari-pmi-unionalimentari.md) | Alimentare | ~35k | 2025 | ⚠️ | base_salary | 0 / 44 / 1 / 1 | 🧪 | 🤖 |
| 41 | H401 | [CCNL Dipendenti da Proprietari di Fabbricati (Confedilizia)](portieri-fabbricati-confedilizia.md) | portieri e custodi di condominio | ~40k | 2025 | ⚠️ | seniority | 0 / 37 / 1 / 1 | 🧪 | 🤖 |
| 42 | H124 | [CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)](farmacie-municipalizzate-assofarm.md) | Farmacie municipalizzate e partecipate da enti locali | ~6k | 2022 | ⚠️ | inps_employer, seniority | 0 / 45 / 2 / 0 | 🧪 | 🤖 |
| 43 | H121 | [CCNL Dipendenti delle Farmacie Private](farmacie-private-h121.md) | Farmacie private | ~60k | 2021 | ⚠️ | seniority | 0 / 37 / 1 / 1 | 🧪 | 🤖 |
| 44 | H016 | [CCNL Distribuzione Cooperativa (ANCC-Coop / Confcooperative Consumo)](distribuzione-cooperativa-ancc.md) | distribuzione-cooperativa | ~63k | — | ⚠️ | seniority | 0 / 62 / 2 / 0 | 🧪 | 🤖 |
| 45 | F018 | [CCNL Edilizia PMI CONFAPI ANIEM](edilizia-pmi-confapi-aniem.md) | Edilizia | ~70000 | 2025 | ⚠️ | base_salary, bilateral_funds, pension_fund_contribution, seniority | 14 / 30 / 2 / 0 | 🧪 | 🤖 |
| 46 | F015 | [CCNL Edilizia e Affini Artigianato](edilizia-artigianato-cna.md) | edilizia | ~350k | — | ⚠️ | bilateral_funds, inps_employer, pension_fund_contribution, seniority | 0 / 72 / 1 / 0 | 🧪 | 🤖 |
| 47 | F016 | [CCNL Edilizia — Cooperative (ANCPL/Legacoop/Confcooperative/AGCI)](edilizia-cooperative-ancpl.md) | Edilizia | ~90000 | 2025 | ⚠️ | seniority | 0 / 57 / 1 / 1 | 🧪 | 🤖 |
| 48 | F012 | [CCNL Edilizia — Industria (ANCE), impiegati e quadri](edilizia-ance-impiegati.md) | edilizia | — | — | ⚠️ | base_salary, overtime, seniority, sickness, territorial_supplement | 32 / 23 / 0 / 0 | 🏭 | 🧑 |
| 49 | F012 | [CCNL Edilizia — Industria (ANCE), operai](edilizia-ance.md) | edilizia | ~550k | 2025 | ⚠️ | base_salary, bilateral_funds, overtime, sickness, territorial_supplement | 32 / 8 / 0 / 0 | 🏭 | 🧑 |
| 50 | B254 | [CCNL Energia e Petrolio (Confindustria Energia)](energia-petrolio-confindustria.md) | energia | ~38k | — | ✅ | — | 0 / 170 / 1 / 1 | 🧪 | 🤖 |
| 51 | G211 | [CCNL Esercizi Cinematografici e Cinema-Teatrali (ANEC)](esercizi-cinematografici-anec.md) | cinema | ~6k | — | ⚠️ | inps_employer, seniority | 0 / 54 / 2 / 0 | 🧪 | 🤖 |
| 52 | H201 | [CCNL Fiori Freschi Recisi, Verde e Piante Ornamentali (ANCEF)](fiori-recisi-ancef.md) | Fiori recisi, verde e piante ornamentali (import-export) | ~1.3k | 2023 | ⚠️ | seniority | 0 / 38 / 1 / 1 | 🧪 | 🤖 |
| 53 | T261 | [CCNL Formazione Professionale (CNOS-FAP/CIOFS-FP/FORMA/CNF)](formazione-professionale.md) | formazione professionale | ~19.8k | — | ✅ | — | 0 / 33 / 1 / 1 | 🧪 | 🤖 |
| 54 | K321 | [CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas](gas-acqua-utilitalia.md) | gas e acqua | ~65k | 2025 | ⚠️ | inps_employer, seniority | 0 / 62 / 2 / 0 | 🧪 | 🤖 |
| 55 | B371 | [CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)](gomma-plastica-federazione-gomma-plastica.md) | gomma-plastica | ~90k | — | ⚠️ | base_salary, seniority | 0 / 77 / 1 / 1 | 🧪 | 🤖 |
| 56 | G011 | [CCNL Grafica e Editoria Industria (AIEG-Acigraf)](grafica-editoria-aieg.md) | grafica-editoria | ~70k | — | ⚠️ | seniority | 0 / 71 / 1 / 1 | 🧪 | 🤖 |
| 57 | T511 | [CCNL Gruppo ANAS](anas.md) | anas spa - personale non dirigente | ~7k | 2025 | ⚠️ | seniority | 0 / 42 / 2 / 0 | 🧪 | 🤖 |
| 58 | K540 | [CCNL Igiene Ambientale — Servizi Ambientali e di Igiene Urbana](igiene-ambientale-utilitalia.md) | servizi ambientali | ~65k | 2025 | ⚠️ | inps_employer, pension_fund_contribution, seniority | 0 / 143 / 1 / 1 | 🧪 | 🤖 |
| 59 | H077 | [CCNL Impianti e Attività Sportive Profit e No-profit](impianti-sportivi-sport.md) | impianti sportivi, palestre e attività sportive | 35533 | 2024 | ⚠️ | base_salary, overtime, sickness | 0 / 32 / 1 / 1 | 🧪 | 🤖 |
| 60 | A021 | [CCNL Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti](impiegati-tecnici-agricoli.md) | agricoltura | ~80k | 2024 | ⚠️ | base_salary, bilateral_funds, inps_employer | 0 / 15 / 1 / 1 | 🧪 | 🤖 |
| 61 | B011 | [CCNL Industria Chimica e Farmaceutica (Federchimica-Farmindustria-Assistal)](chimica-farmaceutica-federchimica.md) | chimica | ~210k | — | ⚠️ | base_salary, overtime, sickness | 111 / 5 / 0 / 0 | 🏭 | 🧑 |
| 62 | H05B | [CCNL Industria Turistica (Federturismo Confindustria)](industria-turistica-federturismo.md) | turismo — alberghi, campeggi, villaggi e strutture ricettive | ~40k | 2025 | ⚠️ | seniority, trattamento_integrativo | 0 / 46 / 1 / 0 | 🧪 | 🤖 |
| 63 | G111 | [CCNL Industrie Cineaudiovisive (ANICA)](cinema-audiovisivi-industria.md) | Cinema e audiovisivo | ~2.3k | 2025 | ⚠️ | bilateral_funds, inps_employer | 0 / 62 / 1 / 1 | 🧪 | 🤖 |
| 64 | HV40 | [CCNL Istituti e Imprese di Vigilanza Privata e Servizi Fiduciari — ASSIV/ANIVP/UNIV (GPG)](vigilanza-privata-assiv.md) | vigilanza-privata | ~85k | 2023 | ⚠️ | inps_employer, seniority | 0 / 48 / 2 / 0 | 🧪 | 🤖 |
| 65 | T241 | [CCNL Istituzioni Formative Private (Scuole Private Religiose) — AGIDAE](scuole-private-agidae.md) | istruzione privata | ~50k | — | ✅ | — | 0 / 43 / 1 / 1 | 🧪 | 🤖 |
| 66 | T141 | [CCNL Istituzioni Socio-Assistenziali — UNEBA](uneba-uneba.md) | servizi socio-assistenziali | ~130k | — | ⚠️ | base_salary, seniority | 0 / 41 / 2 / 0 | 🧪 | 🤖 |
| 67 | T131 | [CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)](istituzioni-servizi-socio-assistenziali-anaste.md) | servizi socio-assistenziali | ~120k | — | ⚠️ | seniority | 0 / 31 / 2 / 0 | 🧪 | 🤖 |
| 68 | F041 | [CCNL Lapidei — Industria (Confindustria Marmomacchine/ANEPLA)](lapidei-industria.md) | industria lapidea e delle cave | ~18k | — | ⚠️ | base_salary, inps_employer, seniority | 0 / 79 / 1 / 1 | 🧪 | 🤖 |
| 69 | F021 | [CCNL Laterizi e Manufatti Cementizi - Industria](laterizi-industria-f021.md) | industria | ~17k | — | ⚠️ | base_salary, seniority | 0 / 98 / 2 / 0 | 🧪 | 🤖 |
| 70 | D0L1 | [CCNL Lavanderie Industriali (Assosistema Confindustria)](lavanderie-industriali-assosistema.md) | lavanderie-industriali | ~17k | — | ⚠️ | seniority | 0 / 37 / 1 / 1 | 🧪 | 🤖 |
| 71 | V925 | [CCNL Lavoratori Dipendenti Organizzazioni Sindacali (UNSIC/CONFSAL)](ooss-unsic-confsal.md) | Organizzazioni sindacali nazionali e territoriali | ~7k | 2023 | ⚠️ | base_salary, seniority | 0 / 19 / 2 / 0 | 🧪 | 🤖 |
| 72 | H501 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi a orario ridotto, art. 14 c. 2)](lavoro-domestico-convivente-orario-ridotto.md) | lavoro domestico | — | — | ⚠️ | assistance_contribution, base_salary, inps_employer, overtime, sickness | 13 / 2 / 0 / 0 | 👁 | 🧑✓ |
| 73 | H501 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)](lavoro-domestico-convivente.md) | lavoro domestico | ~900k | — | ⚠️ | assistance_contribution, base_salary, inps_employer, seniority, sickness | 26 / 1 / 0 / 0 | 👁 | 🧑 |
| 74 | H501 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)](lavoro-domestico-non-convivente.md) | lavoro domestico | ~900k | 2025 | ⚠️ | assistance_contribution, base_salary, seniority, sickness | 17 / 0 / 0 / 0 | 👁 | 🧑 |
| 75 | I100 | [CCNL Logistica, Trasporto Merci e Spedizione (Confetra)](logistica-trasporto-confetra.md) | logistica | ~430k | 2024 | ⚠️ | bilateral_funds, overtime, seniority | 63 / 3 / 0 / 0 | 👁 | 🧑 |
| 76 | I100 | [CCNL Logistica, Trasporto Merci e Spedizione (Confetra) - Personale viaggiante](logistica-trasporto-confetra-viaggiante.md) | logistica | ~430k | 2024 | ⚠️ | base_salary, seniority | 53 / 30 / 0 / 0 | 👁 | 🧑 |
| 77 | I391 | [CCNL Marittimi — Industria Armatoriale (CONFITARMA)](marittimi-industria-armatoriale.md) | navigazione marittima — personale di terra | ~15k | — | ⚠️ | seniority | 0 / 40 / 2 / 0 | 🧪 | 🤖 |
| 78 | F020 | [CCNL Materiali da Costruzione PMI — Lapidei (CONFAPI ANIEM)](materiali-costruzione-lapidei-confapi.md) | Industria materiali da costruzione — Lapidei piccola industria | ~5000 | 2025 | ⚠️ | inps_employer, pension_fund_contribution | 40 / 8 / 22 / 0 | 🧪 | 🤖 |
| 79 | C016 | [CCNL Metalmeccanica - Cooperative](metalmeccanica-cooperative.md) | metalmeccanico cooperativo | ~28k | — | ⚠️ | base_salary, seniority | 0 / 45 / 1 / 1 | 🧪 | 🤖 |
| 80 | C030 | [CCNL Metalmeccanica e Installazione di Impianti — Artigianato](metalmeccanico-artigianato.md) | metalmeccanico | ~350k | 2024 | ⚠️ | bilateral_funds, inps_employer, overtime, sickness | 38 / 43 / 0 / 0 | 🧪 | 🤖 |
| 81 | C01A | [CCNL Metalmeccanici Piccola Industria (CONFIMI IMPRESA MECCANICA)](metalmeccanico-confimi-pmi.md) | metalmeccanico | ~100k | — | ✅ | overtime | 0 / 44 / 0 / 1 | 🧪 | 🤖 |
| 82 | C018 | [CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)](metalmeccanico-confapi.md) | metalmeccanico | ~350k | — | ⚠️ | base_salary, bilateral_funds, overtime, pension_fund_contribution, sickness | 58 / 7 / 0 / 0 | 🏭 | 🧑 |
| 83 | C011 | [CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)](metalmeccanico-federmeccanica.md) | metalmeccanico | ~1,7M | 2025 | ⚠️ | base_salary, bilateral_funds, overtime, seniority, welfare | 86 / 0 / 0 / 0 | 🏭 | 🧑 |
| 84 | IC36 | [CCNL Noleggio Autobus con Conducente (ANAV)](noleggio-autobus-conducente-anav.md) | Trasporti - Noleggio autobus con conducente | ~5422 | 2025 | ⚠️ | base_salary, seniority, una_tantum | 0 / 0 / 70 / 1 | 🧪 | 🤖 |
| 85 | D271 | [CCNL Occhiali e Occhialeria — Industria (ANFAO)](occhiali-occhialeria-industria.md) | industria occhialeria e ottica | ~20k | — | ⚠️ | base_salary, seniority | 0 / 88 / 1 / 1 | 🧪 | 🤖 |
| 86 | A011 | [CCNL Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA](operai-agricoli-florovivaisti.md) | agricoltura | ~600k | 2026 | ⚠️ | base_salary, bilateral_funds, inail, inps_employee, inps_employer, overtime, seniority, sickness, territorial_supplement | 10 / 9 / 1 / 1 | 🧪 | 🤖 |
| 87 | A221 | [CCNL Organizzazioni Allevatori, Consorzi ed Enti Zootecnici (AIA-FLAI-FAI-UILA)](organizzazioni-allevatori-aia.md) | Agricoltura | ~2k | 2024 | ⚠️ | base_salary, inps_employer | 0 / 20 / 1 / 1 | 🧪 | 🤖 |
| 88 | H341 | [CCNL Ortofrutticoli ed Agrumari (Import-Export)](ortofrutticoli-agrumari.md) | ortofrutticoli ed agrumari import-export | ~60000 | 2024 | ⚠️ | base_salary, leave, seniority, sickness | 0 / 0 / 53 / 1 | 🧪 | 🤖 |
| 89 | E023 | [CCNL Panificazione e Settori Affini — Industria (Assipan/Fiesa)](panificazione-assipan.md) | alimentare | ~20k | 2025 | ⚠️ | seniority | 0 / 48 / 1 / 1 | 🧪 | 🤖 |
| 90 | K700 | [CCNL Poste Italiane S.p.A. (personale non dirigente)](poste-italiane-k700.md) | Servizi postali | ~117k | 2024 | ⚠️ | base_salary, inps_employer | 0 / 53 / 2 / 0 | 🧪 | 🤖 |
| 91 | T091 | [CCNL RSA e Strutture Residenziali Socio-Assistenziali (AIOP)](rsa-aiop.md) | residenze sanitarie assistenziali — personale non medico | ~17k | 2012 | ⚠️ | seniority | 0 / 31 / 2 / 0 | 🧪 | 🤖 |
| 92 | G091 | [CCNL Radiotelevisivo — Settore Radiofonico](radiotelevisive-radiofonico.md) | radiotelevisione — settore radiofonico | — | 2026 | ⚠️ | seniority | 0 / 0 / 20 / 1 | 🧪 | 🤖 |
| 93 | G091 | [CCNL Radiotelevisivo — Settore Televisivo Multimediale](radiotelevisive-televisivo.md) | radiotelevisione — settore televisivo multimediale | — | 2026 | ⚠️ | seniority | 0 / 0 / 38 / 1 | 🧪 | 🤖 |
| 94 | K711 | [CCNL Recapito Corrispondenza (FISE-ARE)](recapito-corrispondenza-fise.md) | Recapito corrispondenza e spedizioni | ~1k | 2023 | ✅ | — | 0 / 47 / 1 / 1 | 🧪 | 🤖 |
| 95 | T271 | [CCNL Scuole Materne — FISM](scuole-materne-fism.md) | istruzione privata cattolica per l'infanzia | ~30k | — | ⚠️ | base_salary, seniority | 0 / 47 / 2 / 0 | 🧪 | 🤖 |
| 96 | T231 | [CCNL Scuole Private Laiche (ANINSEI-Assoscuola)](scuole-private-laiche-aninsei.md) | istruzione privata laica | ~25k | — | ⚠️ | seniority | 0 / 43 / 2 / 0 | 🧪 | 🤖 |
| 97 | K721 | [CCNL Servizi Postali in Appalto (FISE-ARE)](servizi-postali-appalto-fise.md) | Servizi postali in appalto e recapito | ~1k | 2023 | ⚠️ | base_salary, seniority | 0 / 49 / 2 / 0 | 🧪 | 🤖 |
| 98 | K511 | [CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)](multiservizi-anip.md) | multiservizi | ~580k | — | ⚠️ | base_salary, bilateral_funds | 57 / 93 / 0 / 0 | 🧪 | 🤖 |
| 99 | A181 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Impiegati)](sistemazioni-idraulico-forestali-impiegati.md) | sistemazioni idraulico-forestali e idraulico-agrarie — impiegati | ~430 (impiegati subset) | 2025 | ⚠️ | base_salary, inps_employer, seniority | 0 / 27 / 2 / 1 | 🧪 | 🤖 |
| 100 | A181 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Operai OTI)](sistemazioni-idraulico-forestali-operai.md) | sistemazioni idraulico-forestali e idraulico-agrarie — operai a tempo indeterminato | ~430 (operai OTI subset) | 2025 | ⚠️ | base_salary, inps_employer, seniority | 0 / 20 / 2 / 1 | 🧪 | 🤖 |
| 101 | K411 | [CCNL Telecomunicazioni — Assotelecomunicazioni (Asstel)](telecomunicazioni-asstel.md) | telecomunicazioni | ~110k | 2025 | ⚠️ | inps_employer, seniority | 0 / 45 / 2 / 0 | 🧪 | 🤖 |
| 102 | H012 | [CCNL Terziario Distribuzione e Servizi — Confesercenti](terziario-confesercenti.md) | Terziario distribuzione e servizi | ~230k | 2024 | ⚠️ | base_salary, bilateral_funds, overtime, seniority, sickness, territorial_supplement, una_tantum | 75 / 0 / 0 / 0 | 🏭 | 🧑 |
| 103 | H011 | [CCNL Terziario, Distribuzione e Servizi (Confcommercio)](commercio-confcommercio.md) | terziario | ~800k | 2024 | ⚠️ | bilateral_funds, seniority, sickness | 69 / 0 / 0 / 0 | 👁 | 🧑 |
| 104 | D018 | [CCNL Tessile-Abbigliamento-Moda PMI (Uniontessile-Confapi)](tessile-pmi-uniontessile.md) | tessile abbigliamento moda PMI | ~48k | 2025 | ⚠️ | base_salary, pension_fund_contribution | 0 / 0 / 43 / 1 | 🧪 | 🔍 |
| 105 | I810 | [CCNL Trasporto Aereo — Gestori Aeroportuali](trasporto-aereo-assaeroporti.md) | trasporto aereo | ~40k | 2025 | ⚠️ | base_salary, seniority | 0 / 72 / 2 / 0 | 🧪 | 🤖 |
| 106 | I911 | [CCNL Trasporto a Fune (Funivie Terrestri ed Aeree) - ANEF](funivie-anef.md) | Trasporto a fune | ~15k | 2025 | ⚠️ | seniority | 0 / 47 / 1 / 1 | 🧪 | 🤖 |
| 107 | H058 | [CCNL Turismo (Assoturismo-Confesercenti)](turismo-confesercenti.md) | turismo — alberghi, campeggi, pubblici esercizi, agenzie di viaggi | — | 2024 | ⚠️ | seniority, trattamento_integrativo | 0 / 57 / 1 / 0 | 🧪 | 🤖 |
| 108 | H052 | [CCNL Turismo — Federalberghi/Faita](turismo-federalberghi.md) | Turismo | ~220k | 2024 | ⚠️ | base_salary, bilateral_funds, seniority, sickness, trattamento_integrativo | 71 / 1 / 0 / 0 | 🏭 | 🧑 |
| 109 | B132 | [CCNL Vetro (Industrie) — Settori Meccanizzati (Prime Lavorazioni)](vetro-meccanizzato-assovetro.md) | vetro industria — settori meccanizzati | ~28k | 2026 | ⚠️ | base_salary | 0 / 0 / 35 / 1 | 🧪 | 🔍 |
| 110 | HV17 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG](vigilanza-privata-federdat-gpg.md) | vigilanza privata — guardie particolari giurate (GPG) | ~45k | 2023 | ⚠️ | seniority | 0 / 48 / 1 / 1 | 🧪 | 🤖 |
| 111 | HV17 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — SF](vigilanza-privata-federdat-sf.md) | vigilanza privata — servizi fiduciari (SF) | ~40k | 2023 | ⚠️ | seniority | 0 / 46 / 2 / 1 | 🧪 | 🤖 |
| 112 | H0B1 | [CCNL per i dipendenti da agenti immobiliari professionali e mandatari a titolo oneroso](agenti-immobiliari-fiaip.md) | agenzie immobiliari | — | 2025 | ⚠️ | base_salary, bilateral_funds, pension_fund_contribution, seniority, una_tantum | 0 / 0 / 30 / 1 | 🧪 | 🤖 |
| 113 | IC91 | [CCNL per i dipendenti da autoscuole, scuole nautiche e studi di consulenza automobilistica](autoscuole-unasca.md) | autoscuole e consulenza automobilistica | — | 2023 | ⚠️ | bilateral_funds, health_fund_employer, seniority | 0 / 32 / 2 / 0 | 🧪 | 🤖 |
| 114 | H05Y | [CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo](pubblici-esercizi-fipe-angem.md) | turismo | ~350k | — | ⚠️ | base_salary, bilateral_funds, overtime, seniority, sickness, trattamento_integrativo | 61 / 2 / 0 / 0 | 🏭 | 🧑 |
| 115 | H05Y | [CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo - Ristorazione collettiva (aziende dell'art. 1 c. 1 par. II)](pubblici-esercizi-fipe-angem-ristorazione-collettiva.md) | turismo | ~350k | — | ⚠️ | base_salary, bilateral_funds, overtime, seniority, trattamento_integrativo | 61 / 2 / 0 / 0 | 🏭 | 🧑 |
| 116 | E042 | [CCNL per i dipendenti dalle aziende di lavorazione della foglia di tabacco secco allo stato sciolto](tabacco-apti.md) | lavorazione foglia di tabacco | ~2k | 2025 | ⚠️ | pension_fund_contribution, seniority | 36 / 0 / 22 / 1 | 🧪 | 🔍 |
| 117 | H442 | [CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)](studi-professionali-confprofessioni.md) | terziario | ~350k | — | ⚠️ | base_salary, bilateral_funds, inps_employer, overtime, seniority, sickness | 46 / 0 / 0 / 0 | 🏭 | 🧑 |
| 118 | K521 | [CCNL per i dipendenti delle imprese artigiane esercenti servizi di pulizia, disinfezione, disinfestazione, derattizzazione e sanificazione](pulizia-artigianato-confartigianato.md) | pulizia artigianato | ~84505 | 2025 | ⚠️ | base_salary, bilateral_funds, holiday_work, inps_employer, leave, night_work, overtime, seniority | 56 / 0 / 30 / 1 | 🧪 | 🤖 |
| 119 | D121 | [CCNL per i lavoratori addetti all'industria delle calzature](calzaturiero-assocalzaturifici.md) | industria | ~75k | — | ⚠️ | seniority | 0 / 37 / 1 / 1 | 🧪 | 🤖 |
| 120 | C021 | [CCNL per i lavoratori addetti all'industria orafa, argentiera e della gioielleria (Federorafi)](orafi-argentieri-industria-federorafi.md) | industria | ~18k | — | ⚠️ | seniority | 0 / 40 / 2 / 0 | 🧪 | 🤖 |
| 121 | D111 | [CCNL per i lavoratori addetti alle industrie delle pelli e dei succedanei della pelle (Assopellettieri)](pelli-cuoio-industria-assopellettieri.md) | industria | ~17k | — | ⚠️ | base_salary, seniority | 0 / 35 / 1 / 1 | 🧪 | 🤖 |
| 122 | E012 | [CCNL per i lavoratori dell'industria alimentare (Federalimentare)](alimentari-federalimentare.md) | industria | ~145k | — | ⚠️ | base_salary, bilateral_funds, overtime, sickness | 75 / 0 / 0 / 0 | 🏭 | 🧑 |
| 123 | B101 | [CCNL per i lavoratori dell'industria conciaria (UNIC)](concia-unic.md) | industria | ~22.6k | — | ⚠️ | overtime, seniority | 57 / 1 / 0 / 0 | 👁 | 🧑 |
| 124 | F051 | [CCNL per i lavoratori dell'industria del legno, del sughero, del mobile, dell'arredamento e delle industrie affini (Federlegno-Arredo)](legno-arredamento-federlegno.md) | industria | ~90k | — | ⚠️ | base_salary, seniority | 0 / 88 / 2 / 0 | 🧪 | 🤖 |
| 125 | D014 | [CCNL per i lavoratori dell'industria tessile, abbigliamento, moda (SMI)](tessile-smi.md) | industria | ~160k | — | ⚠️ | seniority | 0 / 47 / 1 / 1 | 🧪 | 🤖 |
| 126 | J271 | [CCNL per i lavoratori delle Banche di Credito Cooperativo, Casse Rurali ed Artigiane](bcc-credito-cooperativo.md) | credito | ~33k | — | ⚠️ | base_salary, inps_employer, seniority | 35 / 7 / 0 / 1 | 🧪 | 🤖 |
| 127 | K051 | [CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)](elettrico-elettricita-futura.md) | industria | ~60k | — | ⚠️ | seniority | 0 / 77 / 1 / 1 | 🧪 | 🤖 |
| 128 | J241 | [CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)](bancari-abi.md) | credito | ~270k | 2023 | ⚠️ | inps_employer, overtime, seniority, sickness | 43 / 2 / 0 / 0 | 🧪 | 🤖 |
| 129 | K461 | [CCNL per i lavoratori dipendenti delle aziende termali](aziende-termali-federterme.md) | turismo termale | — | — | ⚠️ | base_salary, bilateral_funds, inps_employer, seniority, trattamento_integrativo | 0 / 64 / 1 / 1 | 🧪 | 🤖 |
| 130 | J121 | [CCNL per il personale dipendente non dirigente delle imprese di assicurazione (ANIA)](assicurazioni-ania.md) | assicurazioni | ~45k | 2026 | ⚠️ | base_salary, inps_employer, seniority | 0 / 30 / 1 / 1 | 🧪 | 🤖 |
| 131 | N/A | [DPR 24 marzo 2025, n. 53 — Forze di Polizia ad ordinamento civile (Triennio 2022-2024)](forze-polizia-ordinamento-civile.md) | Pubblica Sicurezza — Forze di Polizia ad ordinamento civile | ~130k | 2025 | ⚠️ | inps_employer | 0 / 70 / 1 / 1 | 🧪 | 🤖 |
| 132 | H008 | [Distribuzione Moderna Organizzata — Federdistribuzione](dmo-federdistribuzione.md) | terziario | ~460k | — | ⚠️ | base_salary, bilateral_funds, overtime, seniority, sickness, territorial_supplement | 77 / 1 / 0 / 0 | 🏭 | 🧑 |

[^2]: DPR 53/2025 -- Compensation for Forze di Polizia ad ordinamento civile is set by Presidential Decree, not a CNEL-registered agreement. D.P.R. 24 marzo 2025, n. 53 (GU n. 91, 18 April 2025, SO).
[^3]: Approximate estimates of the represented population. Contracts can cover overlapping populations, so the figures do not add up. Sources: CNEL, INPS, Ministero del Lavoro, CCNL renewal communications.
[^4]: Salary tables extracted from official CCNL documents using AI-assisted tooling, no manual human review. Verify against the official source before use in production.
