<!-- auto-generated; run: uv run python scripts/docs/gen_capability_matrix.py -->

<!-- generated: 2026-09-27 -->

# Capability Matrix

What the engine computes for fiscal year 2026, and how far the bundled
data behind it is backed by sources. Generated from the capability catalog,
the provenance records of the payable rules and the `coverage` blocks of the
125 bundled CCNLs.

→ [CCNL Coverage index](index.md) ·
[Provenance statuses](../trust/provenance.md)

## Capabilities

| Label | Meaning |
|---|---|
| verified | Implemented; a named person checked every bundled rule it reads |
| implemented | Computed; the bundled rules it reads, if any, cite a source |
| simplified | Computed partially, or reads an `assumed` or `missing` rule |
| unavailable | Not computed by the engine |

Rules counts the payable rules of the bundle each capability reads, by
provenance status: verified / derived / assumed / missing. "none bundled"
means the capability reads no bundled table: it computes from engine
formulas or caller-declared amounts.

| Capability | Description | Catalog | Label | Rules (v / d / a / m) |
|---|---|---|---|---|
| `base_salary` | Paga base contrattuale | computed | simplified | 0 / 5129 / 466 / 0 |
| `seniority` | Scatti di anzianità | computed | simplified | 0 / 119 / 6 / 0 |
| `worker_category` | Categoria lavoratore (dichiarata o fissata dal livello) | computed | implemented | none bundled |
| `inps_employee` | Contributi INPS a carico dipendente | computed | simplified | 0 / 12 / 3 / 0 |
| `inps_employer` | Contributi INPS a carico azienda | computed | simplified | 0 / 19 / 4 / 0 |
| `inail` | INAIL (caller-declared rate) | partially_computed | simplified | none bundled |
| `contribution_exemption` | Esonero contributivo (caller-declared) | partially_computed | simplified | none bundled |
| `fiscal_adjustment` | Conguaglio IRPEF da periodo precedente (caller-declared) | partially_computed | simplified | none bundled |
| `maternity_leave` | Indennità maternità INPS (caller-declared) | partially_computed | simplified | none bundled |
| `workplace_injury` | Indennità infortuno INAIL (caller-declared) | partially_computed | simplified | none bundled |
| `termination_residual_leave` | Monetizzazione ferie residue (caller-declared) | partially_computed | simplified | none bundled |
| `termination_tfr` | Liquidazione TFR (caller-declared) | partially_computed | simplified | none bundled |
| `contract_renewal_arrears` | Arretrati rinnovo contratto (caller-declared) | partially_computed | simplified | none bundled |
| `una_tantum` | Una tantum (caller-declared) | partially_computed | simplified | none bundled |
| `personal_withholdings` | Ritenute personali (caller-declared) | partially_computed | simplified | none bundled |
| `additional_irpef_base` | Base aggiuntiva IRPEF (caller-declared) | partially_computed | simplified | none bundled |
| `health_fund_employee` | Fondo sanitario a carico dipendente (caller-declared) | partially_computed | simplified | none bundled |
| `health_fund_employer` | Fondo sanitario a carico azienda (caller-declared) | partially_computed | simplified | none bundled |
| `territorial_supplement` | Integrazione territoriale (caller-declared) | partially_computed | simplified | none bundled |
| `company_supplement` | Integrazione aziendale (caller-declared) | partially_computed | simplified | none bundled |
| `tfr` | Trattamento di Fine Rapporto | computed | implemented | 0 / 8 / 0 / 0 |
| `irpef` | IRPEF (sostituto d'imposta) | computed | implemented | 0 / 24 / 0 / 0 |
| `trattamento_integrativo` | Trattamento integrativo (ex bonus 80€) | computed | implemented | 0 / 8 / 0 / 0 |
| `ulteriore_detrazione_lavoro` | Ulteriore detrazione lavoro dipendente | computed | implemented | 0 / 8 / 0 / 0 |
| `somma_esente` | Somma esente L. 207/2024 art. 1 c. 4 | computed | simplified | 0 / 0 / 8 / 0 |
| `withholding_shortfall` | Ritenute non capienti riportate ai cedolini successivi | computed | implemented | none bundled |
| `shortfall_deferral` | Differimento scritto dell'IRPEF incapiente del conguaglio con interessi 0,50% mensile (art. 23 c. 3 DPR 600/1973) | computed | implemented | none bundled |
| `foreign_tax_credit` | Credito imposte estere art. 165 TUIR al conguaglio (imposta estera dichiarata; riporti e redditi di anni precedenti non calcolati) | partially_computed | simplified | none bundled |
| `addizionale_regionale` | Addizionale regionale IRPEF | computed | implemented | 0 / 1 / 0 / 0 |
| `addizionale_comunale` | Addizionale comunale IRPEF | computed | implemented | 0 / 1 / 0 / 0 |
| `family_deductions` | Detrazioni familiari a carico | computed | implemented | 0 / 3 / 0 / 0 |
| `art15_deductions` | Detrazioni Art. 15 (interessi mutuo e oneri) | partially_computed | simplified | none bundled |
| `overtime` | Lavoro straordinario e supplementare | computed | implemented | none bundled |
| `night_work` | Lavoro notturno | computed | implemented | none bundled |
| `holiday_work` | Lavoro festivo | computed | implemented | none bundled |
| `shift_work` | Lavoro a turni | computed | implemented | none bundled |
| `absence` | Assenze ingiustificate | computed | implemented | none bundled |
| `leave` | Ferie e permessi ROL | computed | implemented | none bundled |
| `sickness` | Malattia | computed | implemented | none bundled |
| `fringe_benefit` | Fringe benefit (informativo) | computed | implemented | 0 / 1 / 0 / 0 |
| `welfare` | Welfare aziendale (informativo) | computed | implemented | none bundled |
| `bonus_pdr` | Premio di risultato PDR (informativo) | computed | implemented | 0 / 1 / 0 / 0 |
| `rinnovo_substitute_tax` | Imposta sostitutiva aumenti da rinnovo L. 199/2025 art. 1 c. 7 (reddito precedente dichiarato) | partially_computed | simplified | 0 / 1 / 0 / 0 |
| `notte_festivi_turni_substitute_tax` | Imposta sostitutiva notturno, festivo e turni L. 199/2025 art. 1 cc. 10-11 (reddito precedente dichiarato) | partially_computed | simplified | 0 / 1 / 0 / 0 |
| `bilateral_funds` | Fondi bilaterali (informativo) | computed | implemented | none bundled |
| `pension_fund_contribution` | Previdenza complementare CCNL su adesione (misure compensative D.Lgs. 252/2005 art. 10 non calcolate) | partially_computed | simplified | 0 / 12 / 2 / 0 |

## CCNL coverage

| | |
|---|---|
| ✅ | Implemented |
| ⚠️ | Partial, see contract notes |
| 🚫 | Out of scope |
| 🔲 | Not yet implemented |

**L1 (gross):** base salary, seniority, fixed allowances, additional months.
**L2 (net):** INPS contributions, TFR, IRPEF, surtax, family deductions.
**OT / Night / Holiday / Absence / Sick / Leave / Bonus / Benefits /
Welfare / Fringe / Fam.Ded. / Co.Agr. / Terr.Agr.:** L3 work-rules
per-feature status.


| # | CCNL | L1 | L2 | OT | Night | Holiday | Absence | Sick | Leave | Bonus | Benefits | Welfare | Fringe | Fam.Ded. | Co.Agr. | Terr.Agr. |
|---|---|:---:|:---:| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | [CCNL Acconciatura ed Estetica — Confartigianato/CNA](acconciatura-estetica-confartigianato.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 2 | [CCNL Agenzie Marittime Raccomandatarie, Agenzie Aeree e Mediatori Marittimi](agenzie-marittime-i481.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 3 | [CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio](agenzie-viaggio-fiavet.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 4 | [CCNL Alimentaristi Cooperative (Fedagripesca/Legacoop Agroalimentare/AGCI-Agrital)](alimentaristi-cooperative-e016.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 5 | [CCNL Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)](panificazione-artigianato-confartigianato.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 6 | [CCNL Area Comunicazione — Artigianato](comunicazione-artigianato-confartigianato.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 7 | [CCNL Area Dirigenza Funzioni Centrali 2022-2024 — ARAN](dirigenza-funzioni-centrali-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 8 | [CCNL Area Dirigenza Funzioni Locali 2022-2024 — ARAN](dirigenza-funzioni-locali-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 9 | [CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN](dirigenza-istruzione-ricerca-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 10 | [CCNL Area Legno-Lapidei — Artigianato](legno-lapidei-artigianato-confartigianato.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 11 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)](dirigenza-sanitaria-medico-veterinaria-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 12 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi, fisici, chimici)](dirigenza-sanitaria-area-sanita-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 13 | [CCNL Area Tessile-Moda e Chimica-Ceramica — Artigianato](tessile-moda-artigianato-confartigianato.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 14 | [CCNL Attivita Agromeccaniche (Contoterzismo) CAI Agromec-FAI-FLAI-UILA](contoterzismo-caiagromec.md) | ✅ | 🚫 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 15 | [CCNL Attivita Minerarie (ASSORISORSE)](attivita-minerarie-assorisorse.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 16 | [CCNL Attività Ferroviarie — AGENS](trasporto-ferroviario-agens.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 17 | [CCNL Autoferrotranvieri e Internavigatori (Mobilita/TPL)](autoferrotranvieri-internavigatori.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 18 | [CCNL Autorimesse, Noleggio Automezzi e Parcheggi (ANIASA)](autorimesse-ic35.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 19 | [CCNL Autostrade e Trafori Concessionari](autostrade-trafori.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 20 | [CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)](ced-assoced.md) | ✅ | ⚠️ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 21 | [CCNL Carta e Cartone — Aziende Industriali (Assocarta)](carta-cartone-assocarta.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 22 | [CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)](sanita-privata-aiop-aris.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 23 | [CCNL Cemento, Calce e Gesso — Industria (Federbeton)](cemento-calce-gesso-industria.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 24 | [CCNL Ceramica Industria (Confindustria-Assopiastrelle)](ceramica-industria-confindustria.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 25 | [CCNL Chimica e Affini PMI — Unionchimica Confapi](chimica-affini-pmi-unionchimica.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 26 | [CCNL Comparto Funzioni Centrali — Triennio 2022-2024](funzioni-centrali-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 27 | [CCNL Comparto Funzioni Locali 2022-2024 — ARAN](funzioni-locali-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 28 | [CCNL Comparto Istruzione e Ricerca 2022-2024 — ARAN](istruzione-ricerca-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 29 | [CCNL Comparto Sanità 2022-2024 — ARAN](sanita-aran.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 30 | [CCNL Comunicazione, Informatica e Servizi Innovativi PMI — Settore Informatico](informatica-pmi-unimatica.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 31 | [CCNL Consorzi Agrari (ASSOCAP-FLAI-FAI-UILA)](consorzi-agrari-assocap.md) | ✅ | 🚫 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 32 | [CCNL Consorzi di Bonifica (SNEBI-FLAI-FAI-FILBI)](consorzi-di-bonifica-snebi.md) | ✅ | 🚫 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 33 | [CCNL Cooperative Sociali (Confcooperative/Legacoop/AGCI)](cooperative-sociali.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 34 | [CCNL Cooperative e Consorzi Agricoli](cooperative-consorzi-agricoli.md) | ✅ | ⚠️ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 35 | [CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa](federcasa.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 36 | [CCNL Dipendenti Piccola e Media Industria Alimentare (Unionalimentari-Confapi)](alimentari-pmi-unionalimentari.md) | ✅ | 🚫 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 37 | [CCNL Dipendenti da Proprietari di Fabbricati (Confedilizia)](portieri-fabbricati-confedilizia.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 38 | [CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)](farmacie-municipalizzate-assofarm.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 39 | [CCNL Dipendenti delle Farmacie Private](farmacie-private-h121.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 40 | [CCNL Distribuzione Cooperativa (ANCC-Coop / Confcooperative Consumo)](distribuzione-cooperativa-ancc.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 41 | [CCNL Edilizia PMI CONFAPI ANIEM](edilizia-pmi-confapi-aniem.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 42 | [CCNL Edilizia e Affini Artigianato](edilizia-artigianato-cna.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 43 | [CCNL Edilizia — Cooperative (ANCPL/Legacoop/Confcooperative/AGCI)](edilizia-cooperative-ancpl.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 44 | [CCNL Edilizia — Industria (ANCE)](edilizia-ance.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 45 | [CCNL Energia e Petrolio (Confindustria Energia)](energia-petrolio-confindustria.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 46 | [CCNL Esercizi Cinematografici e Cinema-Teatrali (ANEC)](esercizi-cinematografici-anec.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 47 | [CCNL Fiori Freschi Recisi, Verde e Piante Ornamentali (ANCEF)](fiori-recisi-ancef.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 48 | [CCNL Formazione Professionale (CNOS-FAP/CIOFS-FP/FORMA/CNF)](formazione-professionale.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 49 | [CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas](gas-acqua-utilitalia.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 50 | [CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)](gomma-plastica-federazione-gomma-plastica.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 51 | [CCNL Grafica e Editoria Industria (AIEG-Acigraf)](grafica-editoria-aieg.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 52 | [CCNL Gruppo ANAS](anas.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 53 | [CCNL Igiene Ambientale — Servizi Ambientali e di Igiene Urbana](igiene-ambientale-utilitalia.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 54 | [CCNL Impianti e Attività Sportive Profit e No-profit](impianti-sportivi-sport.md) | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 55 | [CCNL Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti](impiegati-tecnici-agricoli.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 56 | [CCNL Industria Chimica e Farmaceutica (Federchimica-Farmindustria-Assistal)](chimica-farmaceutica-federchimica.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 57 | [CCNL Industria Turistica (Federturismo Confindustria)](industria-turistica-federturismo.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 58 | [CCNL Industrie Cineaudiovisive (ANICA)](cinema-audiovisivi-industria.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 59 | [CCNL Istituti e Imprese di Vigilanza Privata e Servizi Fiduciari — ASSIV/ANIVP/UNIV (GPG)](vigilanza-privata-assiv.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 60 | [CCNL Istituzioni Formative Private (Scuole Private Religiose) — AGIDAE](scuole-private-agidae.md) | ✅ | ⚠️ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 61 | [CCNL Istituzioni Socio-Assistenziali — UNEBA](uneba-uneba.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 62 | [CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)](istituzioni-servizi-socio-assistenziali-anaste.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 63 | [CCNL Lapidei — Industria (Confindustria Marmomacchine/ANEPLA)](lapidei-industria.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 64 | [CCNL Laterizi e Manufatti Cementizi - Industria](laterizi-industria-f021.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 65 | [CCNL Lavanderie Industriali (Assosistema Confindustria)](lavanderie-industriali-assosistema.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 66 | [CCNL Lavoratori Dipendenti Organizzazioni Sindacali (UNSIC/CONFSAL)](ooss-unsic-confsal.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 67 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)](lavoro-domestico-convivente.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 68 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)](lavoro-domestico-non-convivente.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 69 | [CCNL Logistica, Trasporto Merci e Spedizione (Confetra)](logistica-trasporto-confetra.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 70 | [CCNL Marittimi — Industria Armatoriale (CONFITARMA)](marittimi-industria-armatoriale.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 71 | [CCNL Materiali da Costruzione PMI — Lapidei (CONFAPI ANIEM)](materiali-costruzione-lapidei-confapi.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 72 | [CCNL Metalmeccanica - Cooperative](metalmeccanica-cooperative.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 73 | [CCNL Metalmeccanica e Installazione di Impianti — Artigianato](metalmeccanico-artigianato.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 74 | [CCNL Metalmeccanici Piccola Industria (CONFIMI IMPRESA MECCANICA)](metalmeccanico-confimi-pmi.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 75 | [CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)](metalmeccanico-confapi.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 76 | [CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)](metalmeccanico-federmeccanica.md) | ✅ | ✅ | ✅ | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 77 | [CCNL Noleggio Autobus con Conducente (ANAV)](noleggio-autobus-conducente-anav.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 78 | [CCNL Occhiali e Occhialeria — Industria (ANFAO)](occhiali-occhialeria-industria.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 79 | [CCNL Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA](operai-agricoli-florovivaisti.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 80 | [CCNL Organizzazioni Allevatori, Consorzi ed Enti Zootecnici (AIA-FLAI-FAI-UILA)](organizzazioni-allevatori-aia.md) | ✅ | 🚫 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 81 | [CCNL Ortofrutticoli ed Agrumari (Import-Export)](ortofrutticoli-agrumari.md) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 82 | [CCNL Panificazione e Settori Affini — Industria (Assipan/Fiesa)](panificazione-assipan.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 83 | [CCNL Poste Italiane S.p.A. (personale non dirigente)](poste-italiane-k700.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 84 | [CCNL RSA e Strutture Residenziali Socio-Assistenziali (AIOP)](rsa-aiop.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 85 | [CCNL Radiotelevisivo — Settore Radiofonico](radiotelevisive-radiofonico.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 86 | [CCNL Radiotelevisivo — Settore Televisivo Multimediale](radiotelevisive-televisivo.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 87 | [CCNL Recapito Corrispondenza (FISE-ARE)](recapito-corrispondenza-fise.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 88 | [CCNL Scuole Materne — FISM](scuole-materne-fism.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 89 | [CCNL Scuole Private Laiche (ANINSEI-Assoscuola)](scuole-private-laiche-aninsei.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 90 | [CCNL Servizi Postali in Appalto (FISE-ARE)](servizi-postali-appalto-fise.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 91 | [CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)](multiservizi-anip.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 92 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Impiegati)](sistemazioni-idraulico-forestali-impiegati.md) | ✅ | ⚠️ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 93 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Operai OTI)](sistemazioni-idraulico-forestali-operai.md) | ✅ | ⚠️ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 94 | [CCNL Telecomunicazioni — Assotelecomunicazioni (Asstel)](telecomunicazioni-asstel.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 95 | [CCNL Terziario Distribuzione e Servizi — Confesercenti](terziario-confesercenti.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 96 | [CCNL Terziario, Distribuzione e Servizi (Confcommercio)](commercio-confcommercio.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 97 | [CCNL Tessile-Abbigliamento-Moda PMI (Uniontessile-Confapi)](tessile-pmi-uniontessile.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 98 | [CCNL Trasporto Aereo — Gestori Aeroportuali](trasporto-aereo-assaeroporti.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 99 | [CCNL Trasporto a Fune (Funivie Terrestri ed Aeree) - ANEF](funivie-anef.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 100 | [CCNL Turismo (Assoturismo-Confesercenti)](turismo-confesercenti.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 101 | [CCNL Turismo — Federalberghi/Faita](turismo-federalberghi.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 102 | [CCNL Turismo, Pubblici Esercizi e Ristorazione (Confcommercio)](turismo-confcommercio.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 103 | [CCNL Vetro (Industrie) — Settori Meccanizzati (Prime Lavorazioni)](vetro-meccanizzato-assovetro.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 104 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG](vigilanza-privata-federdat-gpg.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 105 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — SF](vigilanza-privata-federdat-sf.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 106 | [CCNL per i dipendenti da agenti immobiliari professionali e mandatari a titolo oneroso](agenti-immobiliari-fiaip.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 107 | [CCNL per i dipendenti da autoscuole, scuole nautiche e studi di consulenza automobilistica](autoscuole-unasca.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 108 | [CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo](pubblici-esercizi-fipe-angem.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 109 | [CCNL per i dipendenti dalle aziende di lavorazione della foglia di tabacco secco allo stato sciolto](tabacco-apti.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 110 | [CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)](studi-professionali-confprofessioni.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 111 | [CCNL per i dipendenti delle imprese artigiane esercenti servizi di pulizia, disinfezione, disinfestazione, derattizzazione e sanificazione](pulizia-artigianato-confartigianato.md) | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 112 | [CCNL per i lavoratori addetti all'industria delle calzature](calzaturiero-assocalzaturifici.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 113 | [CCNL per i lavoratori addetti all'industria orafa, argentiera e della gioielleria (Federorafi)](orafi-argentieri-industria-federorafi.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 114 | [CCNL per i lavoratori addetti alle industrie delle pelli e dei succedanei della pelle (Assopellettieri)](pelli-cuoio-industria-assopellettieri.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 115 | [CCNL per i lavoratori dell'industria alimentare (Federalimentare)](alimentari-federalimentare.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 116 | [CCNL per i lavoratori dell'industria conciaria (UNIC)](concia-unic.md) | ✅ | ✅ | ✅ | 🔲 | 🔲 | 🔲 | ⚠️ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 117 | [CCNL per i lavoratori dell'industria del legno, del sughero, del mobile, dell'arredamento e delle industrie affini (Federlegno-Arredo)](legno-arredamento-federlegno.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 118 | [CCNL per i lavoratori dell'industria tessile, abbigliamento, moda (SMI)](tessile-smi.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 119 | [CCNL per i lavoratori delle Banche di Credito Cooperativo, Casse Rurali ed Artigiane](bcc-credito-cooperativo.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 120 | [CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)](elettrico-elettricita-futura.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 121 | [CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)](bancari-abi.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 122 | [CCNL per i lavoratori dipendenti delle aziende termali](aziende-termali-federterme.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 123 | [CCNL per il personale dipendente non dirigente delle imprese di assicurazione (ANIA)](assicurazioni-ania.md) | ⚠️ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 124 | [DPR 24 marzo 2025, n. 53 — Forze di Polizia ad ordinamento civile (Triennio 2022-2024)](forze-polizia-ordinamento-civile.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
| 125 | [Distribuzione Moderna Organizzata — Federdistribuzione](dmo-federdistribuzione.md) | ✅ | ✅ | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 |
