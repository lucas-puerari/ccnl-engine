<!-- auto-generated; run: uv run python scripts/docs/gen_capability_matrix.py -->

<!-- generated: 2026-10-09 -->

# Capability Matrix

What the engine computes for fiscal year 2026, and how far the bundled
data behind it is backed by sources. Generated from the capability registry
(`knowledge/capabilities/data/2026.json`), the provenance records of the
payable rules, the `missing` notes and the model limitations of the 126
bundled CCNLs. The
runtime capability report of every run, the [CCNL Coverage
index](index.md) and this page all derive from the same registry.

→ [Provenance statuses](../trust/provenance.md) ·
[Assurance of a result](../trust/index.md)

## Capabilities

Each capability declares:

- **Implementation:** `native` (bundled rules and request facts),
  `caller_supplied` (a caller rate or amount stands in for a rule),
  `partial` (only the listed variants) or `unsupported`.
- **Applies when:** `always`; `decided` by its decision owner; `event`
  (the request declares an event of the capability); `termination_run`
  (the run closes the employment); `outside_input` (the request has no
  field for the fact that makes it apply: a case with that fact is outside
  the engine input).
- **Handler:** the code that decides and traces it (`pipeline`, `event`,
  `decision`); an unsupported capability has none.
- **Facts:** the request facts it reads; for an `outside_input` capability,
  the fact the request lacks.

A run reports every capability as `applicable`, `not_applicable` or
`outside_input`. Only an applicable capability can leave a gap: an
unsupported one blocks payment, a partial one that executed makes the
coverage partial and blocks payment too.

| Label | Meaning |
|---|---|
| verified | Implemented; a named person checked every bundled rule it reads |
| caller-supplied | Computed from caller rates or amounts that stand in for a rule |
| implemented | Computed; the bundled rules it reads, if any, cite a source |
| simplified | Partial, or reads an `assumed` or `missing` rule |
| unavailable | Not computed by the engine |

Rules counts the payable rules of the bundle each capability reads, by
provenance status: verified / derived / assumed / missing. "none bundled"
means the capability reads no bundled table: it computes from engine
formulas or caller-declared amounts.

| Layer | native | caller_supplied | partial | unsupported |
|---|---:|---:|---:|---:|
| gross | 3 | 1 | 0 | 4 |
| net | 17 | 1 | 2 | 8 |
| work_rules | 3 | 6 | 0 | 3 |

| Capability | Description | Layer | Implementation | Applies when | Handler | Facts | Variants | Label | Rules (v / d / a / m) |
|---|---|---|---|---|---|---|---|---|---|
| `base_salary` | Paga base contrattuale | gross | native | always | pipeline | — | — | simplified | 0 / 5051 / 713 / 86 |
| `seniority` | Scatti di anzianità | gross | native | decided | decision | `employment.seniority` | — | simplified | 0 / 112 / 14 / 0 |
| `worker_category` | Categoria lavoratore (dichiarata o fissata dal livello) | gross | native | decided | decision | `employment.category` | — | implemented | none bundled |
| `inps_employee` | Contributi INPS a carico dipendente | net | native | always | pipeline | — | — | simplified | 0 / 0 / 28 / 0 |
| `inps_employer` | Contributi INPS a carico azienda | net | native | always | pipeline | — | — | simplified | 0 / 0 / 36 / 0 |
| `inail` | Premio INAIL a carico azienda | net | unsupported | outside_input | — | `employer.inail_tariff_rate` | — | unavailable | none bundled |
| `contribution_exemption` | Esonero contributivo | net | unsupported | outside_input | — | `employer.contribution_exemption` | — | unavailable | none bundled |
| `fiscal_adjustment` | Conguaglio IRPEF da assistenza fiscale o periodo precedente | net | unsupported | outside_input | — | `facts.fiscal_adjustment` | — | unavailable | none bundled |
| `maternity_leave` | Indennità maternità INPS | work_rules | unsupported | outside_input | — | `facts.events[maternity_leave]` | — | unavailable | none bundled |
| `workplace_injury` | Indennità infortunio INAIL | work_rules | unsupported | outside_input | — | `facts.events[workplace_injury]` | — | unavailable | none bundled |
| `termination_residual_leave` | Monetizzazione ferie e permessi residui alla cessazione | gross | unsupported | termination_run | — | `facts.residual_leave_hours` | — | unavailable | none bundled |
| `termination_tfr` | Liquidazione TFR a tassazione separata (importo e aliquota dal chiamante) | net | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `contract_renewal_arrears` | Arretrati rinnovo contratto: tassazione separata se di anni precedenti (aliquota dal chiamante), ordinaria se dell'anno | gross | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `una_tantum` | Una tantum contrattuale | gross | unsupported | outside_input | — | `facts.events[una_tantum]` | — | unavailable | none bundled |
| `personal_withholdings` | Trattenute personali (pignoramenti, cessioni del quinto, prestiti) | net | unsupported | outside_input | — | `facts.personal_withholdings` | — | unavailable | none bundled |
| `additional_irpef_base` | Redditi di altri sostituti nella base IRPEF del conguaglio | net | unsupported | outside_input | — | `facts.other_withholding_agents_income` | — | unavailable | none bundled |
| `health_fund_employee` | Fondo sanitario integrativo a carico dipendente | net | unsupported | outside_input | — | `employment.health_fund` | — | unavailable | none bundled |
| `health_fund_employer` | Fondo sanitario integrativo a carico azienda | net | unsupported | outside_input | — | `employment.health_fund` | — | unavailable | none bundled |
| `territorial_supplement` | Integrazione da contratto territoriale | gross | unsupported | outside_input | — | `employment.territorial_agreement` | — | unavailable | none bundled |
| `company_supplement` | Integrazione da contratto aziendale | gross | unsupported | outside_input | — | `employment.company_agreement` | — | unavailable | none bundled |
| `tfr` | Trattamento di Fine Rapporto | net | native | always | pipeline | `employment.tfr_treasury_fund` | — | simplified | 0 / 0 / 13 / 0 |
| `tfr_revaluation` | Rivalutazione del fondo TFR al 31 dicembre e imposta sostitutiva (art. 2120 c. 4 c.c.) | net | native | decided | decision | `employment.tfr_fund` | — | implemented | 0 / 3 / 0 / 0 |
| `irpef` | IRPEF (sostituto d'imposta) | net | native | always | pipeline | — | — | simplified | 0 / 0 / 24 / 0 |
| `trattamento_integrativo` | Trattamento integrativo (ex bonus 80€) | net | native | decided | decision | — | — | simplified | 0 / 0 / 8 / 0 |
| `ulteriore_detrazione_lavoro` | Ulteriore detrazione lavoro dipendente | net | native | decided | decision | — | — | simplified | 0 / 0 / 8 / 0 |
| `somma_esente` | Somma esente L. 207/2024 art. 1 c. 4 | net | native | decided | decision | — | — | implemented | 0 / 1 / 0 / 0 |
| `withholding_shortfall` | Ritenute non capienti riportate ai cedolini successivi | net | native | decided | decision | — | — | implemented | none bundled |
| `shortfall_deferral` | Differimento scritto dell'IRPEF incapiente del conguaglio con interessi 0,50% mensile (art. 23 c. 3 DPR 600/1973) | net | native | decided | decision | — | — | implemented | none bundled |
| `foreign_tax_credit` | Credito imposte estere art. 165 TUIR al conguaglio | net | partial | decided | decision | — | declared_foreign_tax_at_conguaglio | simplified | none bundled |
| `addizionale_regionale` | Addizionale regionale IRPEF | net | native | decided | decision | `facts.regione` | — | implemented | 0 / 1 / 0 / 0 |
| `addizionale_comunale` | Addizionale comunale IRPEF | net | native | decided | decision | `facts.comune_belfiore` | — | implemented | 0 / 1 / 0 / 0 |
| `family_deductions` | Detrazioni familiari a carico (Art. 12 TUIR) | net | native | decided | decision | `facts.family_composition`, `current_year` | children, other_dependants, sole_parent_first_child, spouse, spouse_increase_bands | implemented | 0 / 4 / 0 / 0 |
| `art15_deductions` | Detrazioni Art. 15 TUIR (interessi mutuo e oneri) | net | unsupported | outside_input | — | `facts.art15_expenses` | — | unavailable | none bundled |
| `overtime` | Lavoro straordinario e supplementare | work_rules | caller_supplied | event | event | — | ccnl_band_multiplier, caller_multiplier | caller-supplied | 0 / 371 / 12 / 0 |
| `night_work` | Lavoro notturno | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `holiday_work` | Lavoro festivo | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `shift_work` | Lavoro a turni | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `absence` | Assenze ingiustificate | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `leave` | Ferie e permessi ROL | work_rules | unsupported | outside_input | — | `facts.events[leave]` | — | unavailable | none bundled |
| `sickness` | Malattia: episodi su più periodi, carenza, fasce INPS e integrazione CCNL | work_rules | native | event | event | — | multi_period_episode, inps_bands_and_carenza, ccnl_tiers | simplified | 0 / 224 / 5 / 0 |
| `fringe_benefit` | Fringe benefit (informativo) | work_rules | native | event | event | — | — | implemented | 0 / 1 / 0 / 0 |
| `welfare` | Welfare aziendale (informativo) | work_rules | native | event | event | — | — | implemented | none bundled |
| `bonus_pdr` | Premio di risultato PDR (informativo) | net | native | decided | decision | — | — | simplified | 0 / 0 / 1 / 0 |
| `rinnovo_substitute_tax` | Imposta sostitutiva aumenti da rinnovo L. 199/2025 art. 1 c. 7 | net | native | decided | decision | `prior_year` | — | implemented | 0 / 1 / 0 / 0 |
| `notte_festivi_turni_substitute_tax` | Imposta sostitutiva notturno, festivo e turni L. 199/2025 art. 1 cc. 10-11 | net | native | decided | decision | `prior_year` | — | implemented | 0 / 1 / 0 / 0 |
| `bilateral_funds` | Fondi bilaterali (importi dal chiamante) | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `pension_fund_contribution` | Previdenza complementare CCNL su adesione e contributo contrattuale | net | partial | decided | decision | `employment.pension_fund` | ccnl_fund_on_enrolment, ccnl_contractual_contribution | simplified | 0 / 56 / 25 / 0 |
| `assistance_contribution` | Contributi di assistenza contrattuale per ora retribuita (Cas.Sa.Colf, lavoro domestico) | net | native | decided | decision | `facts.contributable_hours` | — | implemented | 0 / 3 / 0 / 0 |

## CCNL coverage

The same cells as the [CCNL Coverage index](index.md). **Limits** names the
capabilities a `missing` note or a model limitation with a monetary impact
of the contract file lowers to partial. **Rules** counts the payable rules
of the contract file by provenance status: verified / derived / assumed /
missing. The `assumed` and `missing` ones are listed in the shrink-only
evidence baseline (`scripts/ci/provenance_baseline.json`), so these counts
never grow.

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |


| # | CCNL | L1 | L2 | L3 | Limits | Rules (v / d / a / m) |
|---|---|:---:|:---:|:---:|---|---|
| 1 | [CCNL Acconciatura ed Estetica — Confartigianato/CNA](acconciatura-estetica-confartigianato.md) | 🔲 | 🔲 | 🔲 | base_salary | 0 / 28 / 1 / 1 |
| 2 | [CCNL Agenzie Marittime Raccomandatarie, Agenzie Aeree e Mediatori Marittimi](agenzie-marittime-i481.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 36 / 2 / 0 |
| 3 | [CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio](agenzie-viaggio-fiavet.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 68 / 1 / 1 |
| 4 | [CCNL Alimentaristi Cooperative (Fedagripesca/Legacoop Agroalimentare/AGCI-Agrital)](alimentaristi-cooperative-e016.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 70 / 1 / 1 |
| 5 | [CCNL Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)](panificazione-artigianato-confartigianato.md) | 🔲 | 🔲 | 🔲 | territorial_supplement | 0 / 46 / 1 / 1 |
| 6 | [CCNL Area Comunicazione — Artigianato](comunicazione-artigianato-confartigianato.md) | 🔲 | 🔲 | 🔲 | base_salary, worker_category | 0 / 39 / 1 / 1 |
| 7 | [CCNL Area Dirigenza Funzioni Centrali 2022-2024 — ARAN](dirigenza-funzioni-centrali-aran.md) | 🔲 | 🔲 | 🔲 | — | 0 / 9 / 1 / 1 |
| 8 | [CCNL Area Dirigenza Funzioni Locali 2022-2024 — ARAN](dirigenza-funzioni-locali-aran.md) | 🔲 | 🔲 | 🔲 | — | 0 / 5 / 1 / 1 |
| 9 | [CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN](dirigenza-istruzione-ricerca-aran.md) | 🔲 | 🔲 | 🔲 | — | 0 / 7 / 1 / 1 |
| 10 | [CCNL Area Legno-Lapidei — Artigianato](legno-lapidei-artigianato-confartigianato.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employer | 0 / 38 / 2 / 0 |
| 11 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)](dirigenza-sanitaria-medico-veterinaria-aran.md) | 🔲 | 🔲 | 🔲 | base_salary | 0 / 6 / 1 / 1 |
| 12 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi, fisici, chimici)](dirigenza-sanitaria-area-sanita-aran.md) | 🔲 | 🔲 | 🔲 | base_salary | 0 / 6 / 1 / 1 |
| 13 | [CCNL Area Tessile-Moda e Chimica-Ceramica — Artigianato](tessile-moda-artigianato-confartigianato.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employer, seniority | 0 / 35 / 1 / 1 |
| 14 | [CCNL Attivita Agromeccaniche (Contoterzismo) CAI Agromec-FAI-FLAI-UILA](contoterzismo-caiagromec.md) | 🔲 | 🔲 | 🔲 | — | 0 / 48 / 1 / 1 |
| 15 | [CCNL Attivita Minerarie (ASSORISORSE)](attivita-minerarie-assorisorse.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 0 / 38 / 1 |
| 16 | [CCNL Attività Ferroviarie — AGENS](trasporto-ferroviario-agens.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 55 / 1 / 1 |
| 17 | [CCNL Autoferrotranvieri e Internavigatori (Mobilita/TPL)](autoferrotranvieri-internavigatori.md) | 🔲 | 🔲 | 🔲 | inps_employer, seniority | 0 / 138 / 1 / 1 |
| 18 | [CCNL Autorimesse, Noleggio Automezzi e Parcheggi (ANIASA)](autorimesse-ic35.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 95 / 1 / 1 |
| 19 | [CCNL Autostrade e Trafori Concessionari](autostrade-trafori.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 140 / 1 / 1 |
| 20 | [CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)](ced-assoced.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employer | 0 / 44 / 1 / 1 |
| 21 | [CCNL Carta e Cartone — Aziende Industriali (Assocarta)](carta-cartone-assocarta.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 71 / 2 / 0 |
| 22 | [CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)](sanita-privata-aiop-aris.md) | 🔲 | 🔲 | 🔲 | — | 0 / 35 / 2 / 0 |
| 23 | [CCNL Cemento, Calce e Gesso — Industria (Federbeton)](cemento-calce-gesso-industria.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 80 / 2 / 0 |
| 24 | [CCNL Ceramica Industria (Confindustria-Assopiastrelle)](ceramica-industria-confindustria.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 60 / 1 / 1 |
| 25 | [CCNL Chimica e Affini PMI — Unionchimica Confapi](chimica-affini-pmi-unionchimica.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 21 / 1 / 1 |
| 26 | [CCNL Comparto Funzioni Centrali — Triennio 2022-2024](funzioni-centrali-aran.md) | 🔲 | 🔲 | 🔲 | inps_employer | 0 / 27 / 1 / 1 |
| 27 | [CCNL Comparto Funzioni Locali 2022-2024 — ARAN](funzioni-locali-aran.md) | 🔲 | 🔲 | 🔲 | base_salary, company_supplement | 0 / 19 / 1 / 1 |
| 28 | [CCNL Comparto Istruzione e Ricerca 2022-2024 — ARAN](istruzione-ricerca-aran.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 19 / 1 / 1 |
| 29 | [CCNL Comparto Sanità 2022-2024 — ARAN](sanita-aran.md) | 🔲 | 🔲 | 🔲 | base_salary | 0 / 17 / 1 / 1 |
| 30 | [CCNL Comunicazione, Informatica e Servizi Innovativi PMI — Settore Informatico](informatica-pmi-unimatica.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 40 / 2 / 0 |
| 31 | [CCNL Consorzi Agrari (ASSOCAP-FLAI-FAI-UILA)](consorzi-agrari-assocap.md) | 🔲 | 🔲 | 🔲 | base_salary, health_fund_employer | 0 / 36 / 1 / 1 |
| 32 | [CCNL Consorzi di Bonifica (SNEBI-FLAI-FAI-FILBI)](consorzi-di-bonifica-snebi.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 56 / 1 / 1 |
| 33 | [CCNL Cooperative Sociali (Confcooperative/Legacoop/AGCI)](cooperative-sociali.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 58 / 2 / 1 |
| 34 | [CCNL Cooperative e Consorzi Agricoli](cooperative-consorzi-agricoli.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 40 / 2 / 0 |
| 35 | [CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa](federcasa.md) | 🔲 | 🔲 | 🔲 | — | 0 / 23 / 2 / 0 |
| 36 | [CCNL Dipendenti Piccola e Media Industria Alimentare (Unionalimentari-Confapi)](alimentari-pmi-unionalimentari.md) | 🔲 | 🔲 | 🔲 | base_salary | 0 / 44 / 1 / 1 |
| 37 | [CCNL Dipendenti da Proprietari di Fabbricati (Confedilizia)](portieri-fabbricati-confedilizia.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 37 / 1 / 1 |
| 38 | [CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)](farmacie-municipalizzate-assofarm.md) | 🔲 | 🔲 | 🔲 | inps_employer, seniority | 0 / 45 / 2 / 0 |
| 39 | [CCNL Dipendenti delle Farmacie Private](farmacie-private-h121.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 37 / 1 / 1 |
| 40 | [CCNL Distribuzione Cooperativa (ANCC-Coop / Confcooperative Consumo)](distribuzione-cooperativa-ancc.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 62 / 2 / 0 |
| 41 | [CCNL Edilizia PMI CONFAPI ANIEM](edilizia-pmi-confapi-aniem.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 35 / 2 / 0 |
| 42 | [CCNL Edilizia e Affini Artigianato](edilizia-artigianato-cna.md) | 🔲 | 🔲 | 🔲 | bilateral_funds, pension_fund_contribution, seniority | 0 / 71 / 1 / 1 |
| 43 | [CCNL Edilizia — Cooperative (ANCPL/Legacoop/Confcooperative/AGCI)](edilizia-cooperative-ancpl.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 57 / 1 / 1 |
| 44 | [CCNL Edilizia — Industria (ANCE)](edilizia-ance.md) | 🔲 | 🔲 | 🔲 | pension_fund_contribution, seniority | 0 / 43 / 2 / 0 |
| 45 | [CCNL Energia e Petrolio (Confindustria Energia)](energia-petrolio-confindustria.md) | 🔲 | 🔲 | 🔲 | — | 0 / 170 / 1 / 1 |
| 46 | [CCNL Esercizi Cinematografici e Cinema-Teatrali (ANEC)](esercizi-cinematografici-anec.md) | 🔲 | 🔲 | 🔲 | inps_employer, seniority | 0 / 52 / 2 / 0 |
| 47 | [CCNL Fiori Freschi Recisi, Verde e Piante Ornamentali (ANCEF)](fiori-recisi-ancef.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 38 / 1 / 1 |
| 48 | [CCNL Formazione Professionale (CNOS-FAP/CIOFS-FP/FORMA/CNF)](formazione-professionale.md) | 🔲 | 🔲 | 🔲 | — | 0 / 33 / 1 / 1 |
| 49 | [CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas](gas-acqua-utilitalia.md) | 🔲 | 🔲 | 🔲 | inps_employer, seniority | 0 / 62 / 2 / 0 |
| 50 | [CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)](gomma-plastica-federazione-gomma-plastica.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 77 / 1 / 1 |
| 51 | [CCNL Grafica e Editoria Industria (AIEG-Acigraf)](grafica-editoria-aieg.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 67 / 1 / 1 |
| 52 | [CCNL Gruppo ANAS](anas.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 42 / 2 / 0 |
| 53 | [CCNL Igiene Ambientale — Servizi Ambientali e di Igiene Urbana](igiene-ambientale-utilitalia.md) | 🔲 | 🔲 | 🔲 | inps_employer, seniority | 0 / 106 / 1 / 1 |
| 54 | [CCNL Impianti e Attività Sportive Profit e No-profit](impianti-sportivi-sport.md) | 🔲 | 🔲 | 🔲 | base_salary, overtime, sickness | 0 / 32 / 1 / 1 |
| 55 | [CCNL Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti](impiegati-tecnici-agricoli.md) | 🔲 | 🔲 | 🔲 | base_salary, bilateral_funds | 0 / 15 / 1 / 1 |
| 56 | [CCNL Industria Chimica e Farmaceutica (Federchimica-Farmindustria-Assistal)](chimica-farmaceutica-federchimica.md) | 🔲 | 🔲 | 🔲 | — | 0 / 98 / 1 / 1 |
| 57 | [CCNL Industria Turistica (Federturismo Confindustria)](industria-turistica-federturismo.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 45 / 1 / 1 |
| 58 | [CCNL Industrie Cineaudiovisive (ANICA)](cinema-audiovisivi-industria.md) | 🔲 | 🔲 | 🔲 | bilateral_funds | 0 / 62 / 1 / 1 |
| 59 | [CCNL Istituti e Imprese di Vigilanza Privata e Servizi Fiduciari — ASSIV/ANIVP/UNIV (GPG)](vigilanza-privata-assiv.md) | 🔲 | 🔲 | 🔲 | inps_employer, seniority | 0 / 48 / 2 / 0 |
| 60 | [CCNL Istituzioni Formative Private (Scuole Private Religiose) — AGIDAE](scuole-private-agidae.md) | 🔲 | 🔲 | 🔲 | — | 0 / 43 / 1 / 1 |
| 61 | [CCNL Istituzioni Socio-Assistenziali — UNEBA](uneba-uneba.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 41 / 2 / 0 |
| 62 | [CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)](istituzioni-servizi-socio-assistenziali-anaste.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 31 / 2 / 0 |
| 63 | [CCNL Lapidei — Industria (Confindustria Marmomacchine/ANEPLA)](lapidei-industria.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 79 / 1 / 1 |
| 64 | [CCNL Laterizi e Manufatti Cementizi - Industria](laterizi-industria-f021.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 98 / 2 / 0 |
| 65 | [CCNL Lavanderie Industriali (Assosistema Confindustria)](lavanderie-industriali-assosistema.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 37 / 1 / 1 |
| 66 | [CCNL Lavoratori Dipendenti Organizzazioni Sindacali (UNSIC/CONFSAL)](ooss-unsic-confsal.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 19 / 2 / 0 |
| 67 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi a orario ridotto, art. 14 c. 2)](lavoro-domestico-convivente-orario-ridotto.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employee, inps_employer | 0 / 13 / 0 / 1 |
| 68 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)](lavoro-domestico-convivente.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employee, inps_employer, seniority | 0 / 25 / 0 / 1 |
| 69 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)](lavoro-domestico-non-convivente.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employee, seniority | 0 / 15 / 0 / 1 |
| 70 | [CCNL Logistica, Trasporto Merci e Spedizione (Confetra)](logistica-trasporto-confetra.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 43 / 2 / 0 |
| 71 | [CCNL Marittimi — Industria Armatoriale (CONFITARMA)](marittimi-industria-armatoriale.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 40 / 2 / 0 |
| 72 | [CCNL Materiali da Costruzione PMI — Lapidei (CONFAPI ANIEM)](materiali-costruzione-lapidei-confapi.md) | 🔲 | 🔲 | 🔲 | pension_fund_contribution | 0 / 0 / 70 / 0 |
| 73 | [CCNL Metalmeccanica - Cooperative](metalmeccanica-cooperative.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 45 / 1 / 1 |
| 74 | [CCNL Metalmeccanica e Installazione di Impianti — Artigianato](metalmeccanico-artigianato.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 79 / 1 / 1 |
| 75 | [CCNL Metalmeccanici Piccola Industria (CONFIMI IMPRESA MECCANICA)](metalmeccanico-confimi-pmi.md) | 🔲 | 🔲 | 🔲 | overtime | 0 / 44 / 0 / 1 |
| 76 | [CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)](metalmeccanico-confapi.md) | 🔲 | 🔲 | 🔲 | base_salary, pension_fund_contribution, seniority | 0 / 45 / 1 / 1 |
| 77 | [CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)](metalmeccanico-federmeccanica.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 60 / 6 / 0 |
| 78 | [CCNL Noleggio Autobus con Conducente (ANAV)](noleggio-autobus-conducente-anav.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority, una_tantum | 0 / 0 / 70 / 1 |
| 79 | [CCNL Occhiali e Occhialeria — Industria (ANFAO)](occhiali-occhialeria-industria.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 88 / 1 / 1 |
| 80 | [CCNL Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA](operai-agricoli-florovivaisti.md) | 🔲 | 🔲 | 🔲 | base_salary, bilateral_funds, inail, inps_employee, inps_employer, seniority, territorial_supplement | 0 / 18 / 1 / 1 |
| 81 | [CCNL Organizzazioni Allevatori, Consorzi ed Enti Zootecnici (AIA-FLAI-FAI-UILA)](organizzazioni-allevatori-aia.md) | 🔲 | 🔲 | 🔲 | base_salary | 0 / 20 / 1 / 1 |
| 82 | [CCNL Ortofrutticoli ed Agrumari (Import-Export)](ortofrutticoli-agrumari.md) | 🔲 | 🔲 | 🔲 | base_salary, leave, seniority, sickness | 0 / 0 / 53 / 1 |
| 83 | [CCNL Panificazione e Settori Affini — Industria (Assipan/Fiesa)](panificazione-assipan.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 48 / 1 / 1 |
| 84 | [CCNL Poste Italiane S.p.A. (personale non dirigente)](poste-italiane-k700.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employer | 0 / 53 / 2 / 0 |
| 85 | [CCNL RSA e Strutture Residenziali Socio-Assistenziali (AIOP)](rsa-aiop.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 31 / 2 / 0 |
| 86 | [CCNL Radiotelevisivo — Settore Radiofonico](radiotelevisive-radiofonico.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 0 / 20 / 1 |
| 87 | [CCNL Radiotelevisivo — Settore Televisivo Multimediale](radiotelevisive-televisivo.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 0 / 38 / 1 |
| 88 | [CCNL Recapito Corrispondenza (FISE-ARE)](recapito-corrispondenza-fise.md) | 🔲 | 🔲 | 🔲 | — | 0 / 47 / 1 / 1 |
| 89 | [CCNL Scuole Materne — FISM](scuole-materne-fism.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 47 / 2 / 0 |
| 90 | [CCNL Scuole Private Laiche (ANINSEI-Assoscuola)](scuole-private-laiche-aninsei.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 43 / 2 / 0 |
| 91 | [CCNL Servizi Postali in Appalto (FISE-ARE)](servizi-postali-appalto-fise.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 49 / 2 / 0 |
| 92 | [CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)](multiservizi-anip.md) | 🔲 | 🔲 | 🔲 | inps_employee, seniority | 0 / 148 / 2 / 0 |
| 93 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Impiegati)](sistemazioni-idraulico-forestali-impiegati.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 27 / 2 / 1 |
| 94 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Operai OTI)](sistemazioni-idraulico-forestali-operai.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 20 / 2 / 1 |
| 95 | [CCNL Telecomunicazioni — Assotelecomunicazioni (Asstel)](telecomunicazioni-asstel.md) | 🔲 | 🔲 | 🔲 | inps_employer, seniority | 0 / 45 / 2 / 0 |
| 96 | [CCNL Terziario Distribuzione e Servizi — Confesercenti](terziario-confesercenti.md) | 🔲 | 🔲 | 🔲 | seniority, una_tantum | 0 / 62 / 2 / 0 |
| 97 | [CCNL Terziario, Distribuzione e Servizi (Confcommercio)](commercio-confcommercio.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 7 / 62 / 0 |
| 98 | [CCNL Tessile-Abbigliamento-Moda PMI (Uniontessile-Confapi)](tessile-pmi-uniontessile.md) | 🔲 | 🔲 | 🔲 | base_salary, pension_fund_contribution | 0 / 0 / 43 / 1 |
| 99 | [CCNL Trasporto Aereo — Gestori Aeroportuali](trasporto-aereo-assaeroporti.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 72 / 2 / 0 |
| 100 | [CCNL Trasporto a Fune (Funivie Terrestri ed Aeree) - ANEF](funivie-anef.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 47 / 1 / 1 |
| 101 | [CCNL Turismo (Assoturismo-Confesercenti)](turismo-confesercenti.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 56 / 1 / 1 |
| 102 | [CCNL Turismo — Federalberghi/Faita](turismo-federalberghi.md) | 🔲 | 🔲 | 🔲 | seniority, worker_category | 0 / 68 / 1 / 1 |
| 103 | [CCNL Turismo, Pubblici Esercizi e Ristorazione (Confcommercio)](turismo-confcommercio.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 58 / 1 / 1 |
| 104 | [CCNL Vetro (Industrie) — Settori Meccanizzati (Prime Lavorazioni)](vetro-meccanizzato-assovetro.md) | 🔲 | 🔲 | 🔲 | base_salary | 0 / 0 / 35 / 1 |
| 105 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG](vigilanza-privata-federdat-gpg.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 48 / 1 / 1 |
| 106 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — SF](vigilanza-privata-federdat-sf.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 46 / 2 / 1 |
| 107 | [CCNL per i dipendenti da agenti immobiliari professionali e mandatari a titolo oneroso](agenti-immobiliari-fiaip.md) | 🔲 | 🔲 | 🔲 | base_salary, bilateral_funds, pension_fund_contribution, seniority, una_tantum | 0 / 0 / 30 / 1 |
| 108 | [CCNL per i dipendenti da autoscuole, scuole nautiche e studi di consulenza automobilistica](autoscuole-unasca.md) | 🔲 | 🔲 | 🔲 | bilateral_funds, health_fund_employer, seniority | 0 / 32 / 2 / 0 |
| 109 | [CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo](pubblici-esercizi-fipe-angem.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 61 / 1 / 1 |
| 110 | [CCNL per i dipendenti dalle aziende di lavorazione della foglia di tabacco secco allo stato sciolto](tabacco-apti.md) | 🔲 | 🔲 | 🔲 | pension_fund_contribution, seniority | 0 / 0 / 58 / 1 |
| 111 | [CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)](studi-professionali-confprofessioni.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 42 / 2 / 0 |
| 112 | [CCNL per i dipendenti delle imprese artigiane esercenti servizi di pulizia, disinfezione, disinfestazione, derattizzazione e sanificazione](pulizia-artigianato-confartigianato.md) | 🔲 | 🔲 | 🔲 | base_salary, bilateral_funds, holiday_work, inps_employer, leave, night_work, overtime, seniority | 0 / 0 / 86 / 1 |
| 113 | [CCNL per i lavoratori addetti all'industria delle calzature](calzaturiero-assocalzaturifici.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 37 / 1 / 1 |
| 114 | [CCNL per i lavoratori addetti all'industria orafa, argentiera e della gioielleria (Federorafi)](orafi-argentieri-industria-federorafi.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 40 / 2 / 0 |
| 115 | [CCNL per i lavoratori addetti alle industrie delle pelli e dei succedanei della pelle (Assopellettieri)](pelli-cuoio-industria-assopellettieri.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 35 / 1 / 1 |
| 116 | [CCNL per i lavoratori dell'industria alimentare (Federalimentare)](alimentari-federalimentare.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 73 / 2 / 0 |
| 117 | [CCNL per i lavoratori dell'industria conciaria (UNIC)](concia-unic.md) | 🔲 | 🔲 | 🔲 | overtime, seniority, sickness | 0 / 57 / 0 / 1 |
| 118 | [CCNL per i lavoratori dell'industria del legno, del sughero, del mobile, dell'arredamento e delle industrie affini (Federlegno-Arredo)](legno-arredamento-federlegno.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 88 / 2 / 0 |
| 119 | [CCNL per i lavoratori dell'industria tessile, abbigliamento, moda (SMI)](tessile-smi.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 47 / 1 / 1 |
| 120 | [CCNL per i lavoratori delle Banche di Credito Cooperativo, Casse Rurali ed Artigiane](bcc-credito-cooperativo.md) | 🔲 | 🔲 | 🔲 | base_salary, seniority | 0 / 40 / 1 / 1 |
| 121 | [CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)](elettrico-elettricita-futura.md) | 🔲 | 🔲 | 🔲 | seniority | 0 / 77 / 1 / 1 |
| 122 | [CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)](bancari-abi.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employer, seniority | 0 / 42 / 1 / 1 |
| 123 | [CCNL per i lavoratori dipendenti delle aziende termali](aziende-termali-federterme.md) | 🔲 | 🔲 | 🔲 | base_salary, bilateral_funds, inps_employer, seniority | 0 / 64 / 1 / 1 |
| 124 | [CCNL per il personale dipendente non dirigente delle imprese di assicurazione (ANIA)](assicurazioni-ania.md) | 🔲 | 🔲 | 🔲 | base_salary, inps_employer, seniority | 0 / 29 / 1 / 1 |
| 125 | [DPR 24 marzo 2025, n. 53 — Forze di Polizia ad ordinamento civile (Triennio 2022-2024)](forze-polizia-ordinamento-civile.md) | 🔲 | 🔲 | 🔲 | inps_employer | 0 / 70 / 1 / 1 |
| 126 | [Distribuzione Moderna Organizzata — Federdistribuzione](dmo-federdistribuzione.md) | 🔲 | 🔲 | 🔲 | seniority, territorial_supplement | 0 / 73 / 2 / 0 |
