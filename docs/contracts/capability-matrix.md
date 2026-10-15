<!-- auto-generated; run: uv run python scripts/documentation/capability_matrix/generate.py -->

<!-- generated: 2026-10-15 -->

# Capability Matrix

What the engine computes for fiscal year 2027, and how far the bundled
data behind it is backed by sources. Generated from the capability registry
(`knowledge/capability/registry/2027.json`), the provenance records of the
payable rules, the `missing` notes and the model limitations of the 132
bundled CCNLs. The
runtime capability report of every run, the [CCNL Coverage
index](index.md) and this page all derive from the same registry.

→ [Provenance statuses](../trust/provenance.md) ·
[Assurance of a result](../trust/index.md)

## Capabilities

Each capability has a **scope** on these pages: `core` (computed or decided
on every run: the path the contracts index rates), `scenario` (an event, a
termination, or a decided capability the engine covers only in part) or
`outside_input`. Each also declares:

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

| Scope | native | caller_supplied | partial | unsupported |
|---|---:|---:|---:|---:|
| core | 20 | 0 | 0 | 0 |
| scenario | 4 | 9 | 2 | 1 |
| outside_input | 0 | 0 | 0 | 14 |

| Capability | Description | Scope | Layer | Implementation | Applies when | Handler | Facts | Variants | Label | Rules (v / d / a / m) |
|---|---|---|---|---|---|---|---|---|---|---|
| `base_salary` | Paga base contrattuale | core | gross | native | always | pipeline | — | — | simplified | 1425 / 4084 / 660 / 59 |
| `seniority` | Scatti di anzianità | core | gross | native | decided | decision | `employment.seniority` | — | simplified | 21 / 98 / 13 / 0 |
| `worker_category` | Categoria lavoratore (dichiarata o fissata dal livello) | core | gross | native | decided | decision | `employment.category` | — | implemented | none bundled |
| `inps_employee` | Contributi INPS a carico dipendente | core | net | native | always | pipeline | — | — | simplified | 21 / 24 / 48 / 0 |
| `inps_employer` | Contributi INPS a carico azienda | core | net | native | always | pipeline | — | — | simplified | 29 / 24 / 56 / 0 |
| `inail` | Premio INAIL a carico azienda | outside_input | net | unsupported | outside_input | — | `employer.inail_tariff_rate` | — | unavailable | none bundled |
| `contribution_exemption` | Esonero contributivo | outside_input | net | unsupported | outside_input | — | `employer.contribution_exemption` | — | unavailable | none bundled |
| `fiscal_adjustment` | Conguaglio IRPEF da assistenza fiscale o periodo precedente | outside_input | net | unsupported | outside_input | — | `facts.fiscal_adjustment` | — | unavailable | none bundled |
| `maternity_leave` | Indennità maternità INPS | outside_input | work_rules | unsupported | outside_input | — | `facts.events[maternity_leave]` | — | unavailable | none bundled |
| `workplace_injury` | Indennità infortunio INAIL | outside_input | work_rules | unsupported | outside_input | — | `facts.events[workplace_injury]` | — | unavailable | none bundled |
| `termination_residual_leave` | Monetizzazione ferie e permessi residui alla cessazione | scenario | gross | unsupported | termination_run | — | `facts.residual_leave_hours` | — | unavailable | none bundled |
| `termination_tfr` | Liquidazione TFR a tassazione separata (importo e aliquota dal chiamante) | scenario | net | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `contract_renewal_arrears` | Arretrati rinnovo contratto: tassazione separata se di anni precedenti (aliquota dal chiamante), ordinaria se dell'anno | scenario | gross | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `una_tantum` | Una tantum contrattuale | outside_input | gross | unsupported | outside_input | — | `facts.events[una_tantum]` | — | unavailable | none bundled |
| `personal_withholdings` | Trattenute personali (pignoramenti, cessioni del quinto, prestiti) | outside_input | net | unsupported | outside_input | — | `facts.personal_withholdings` | — | unavailable | none bundled |
| `additional_irpef_base` | Redditi di altri sostituti nella base IRPEF del conguaglio | outside_input | net | unsupported | outside_input | — | `facts.other_withholding_agents_income` | — | unavailable | none bundled |
| `health_fund_employee` | Fondo sanitario integrativo a carico dipendente | outside_input | net | unsupported | outside_input | — | `employment.health_fund` | — | unavailable | none bundled |
| `health_fund_employer` | Fondo sanitario integrativo a carico azienda | outside_input | net | unsupported | outside_input | — | `employment.health_fund` | — | unavailable | none bundled |
| `territorial_supplement` | Integrazione da contratto territoriale | outside_input | gross | unsupported | outside_input | — | `employment.territorial_agreement` | — | unavailable | none bundled |
| `company_supplement` | Integrazione da contratto aziendale | outside_input | gross | unsupported | outside_input | — | `employment.company_agreement` | — | unavailable | none bundled |
| `tfr` | Trattamento di Fine Rapporto | core | net | native | always | pipeline | `employment.tfr_treasury_fund` | — | simplified | 18 / 0 / 18 / 0 |
| `tfr_revaluation` | Rivalutazione del fondo TFR al 31 dicembre e imposta sostitutiva (art. 2120 c. 4 c.c.) | core | net | native | decided | decision | `employment.tfr_fund` | — | implemented | 1 / 2 / 0 / 0 |
| `irpef` | IRPEF (sostituto d'imposta) | core | net | native | always | pipeline | — | — | simplified | 24 / 0 / 24 / 0 |
| `trattamento_integrativo` | Trattamento integrativo (ex bonus 80€) | core | net | native | decided | decision | — | — | simplified | 8 / 0 / 8 / 0 |
| `ulteriore_detrazione_lavoro` | Ulteriore detrazione lavoro dipendente | core | net | native | decided | decision | — | — | simplified | 8 / 0 / 8 / 0 |
| `somma_esente` | Somma esente L. 207/2024 art. 1 c. 4 | core | net | native | decided | decision | — | — | simplified | 1 / 0 / 1 / 0 |
| `withholding_shortfall` | Ritenute non capienti riportate ai cedolini successivi | core | net | native | decided | decision | — | — | implemented | none bundled |
| `shortfall_deferral` | Differimento scritto dell'IRPEF incapiente del conguaglio con interessi 0,50% mensile (art. 23 c. 3 DPR 600/1973) | core | net | native | decided | decision | — | — | implemented | none bundled |
| `foreign_tax_credit` | Credito imposte estere art. 165 TUIR al conguaglio | scenario | net | partial | decided | decision | — | declared_foreign_tax_at_conguaglio | simplified | none bundled |
| `addizionale_regionale` | Addizionale regionale IRPEF | core | net | native | decided | decision | `facts.regione` | — | simplified | 1 / 0 / 1 / 0 |
| `addizionale_comunale` | Addizionale comunale IRPEF | core | net | native | decided | decision | `facts.comune_belfiore` | — | simplified | 0 / 1 / 1 / 0 |
| `family_deductions` | Detrazioni familiari a carico (Art. 12 TUIR) | core | net | native | decided | decision | `facts.family_composition`, `current_year` | children, other_dependants, sole_parent_first_child, spouse, spouse_increase_bands | simplified | 4 / 0 / 4 / 0 |
| `art15_deductions` | Detrazioni Art. 15 TUIR (interessi mutuo e oneri) | outside_input | net | unsupported | outside_input | — | `facts.art15_expenses` | — | unavailable | none bundled |
| `overtime` | Lavoro straordinario e supplementare | scenario | work_rules | caller_supplied | event | event | — | ccnl_band_multiplier, caller_multiplier | caller-supplied | 82 / 303 / 7 / 0 |
| `night_work` | Lavoro notturno | scenario | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `holiday_work` | Lavoro festivo | scenario | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `shift_work` | Lavoro a turni | scenario | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `standby` | Reperibilità (importi del CCNL per livello) | scenario | work_rules | native | event | event | — | — | implemented | none bundled |
| `absence` | Assenze ingiustificate | scenario | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `leave` | Ferie e permessi ROL | outside_input | work_rules | unsupported | outside_input | — | `facts.events[leave]` | — | unavailable | none bundled |
| `sickness` | Malattia: episodi su più periodi, carenza, fasce INPS e integrazione CCNL | scenario | work_rules | native | event | event | — | multi_period_episode, inps_bands_and_carenza, ccnl_tiers | simplified | 34 / 200 / 9 / 0 |
| `fringe_benefit` | Fringe benefit (informativo) | scenario | work_rules | native | event | event | — | — | simplified | 0 / 1 / 1 / 0 |
| `travel_allowance` | Indennità di trasferta (importo giornaliero dal chiamante, quota esente art. 51 c. 5 TUIR) | scenario | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `welfare` | Welfare aziendale (informativo) | scenario | work_rules | native | event | event | — | — | implemented | none bundled |
| `bonus_pdr` | Premio di risultato PDR (informativo) | core | net | native | decided | decision | — | — | simplified | 0 / 1 / 1 / 0 |
| `rinnovo_substitute_tax` | Imposta sostitutiva aumenti da rinnovo L. 199/2025 art. 1 c. 7 | core | net | native | decided | decision | `prior_year` | — | simplified | 0 / 1 / 1 / 0 |
| `notte_festivi_turni_substitute_tax` | Imposta sostitutiva notturno, festivo e turni L. 199/2025 art. 1 cc. 10-11 | core | net | native | decided | decision | `prior_year` | — | simplified | 0 / 1 / 1 / 0 |
| `bilateral_funds` | Fondi bilaterali (importi dal chiamante) | scenario | work_rules | caller_supplied | event | event | — | — | caller-supplied | none bundled |
| `pension_fund_contribution` | Previdenza complementare CCNL su adesione e contributo contrattuale | scenario | net | partial | decided | decision | `employment.pension_fund` | ccnl_fund_on_enrolment, ccnl_contractual_contribution | simplified | 39 / 113 / 25 / 0 |
| `assistance_contribution` | Contributi di assistenza contrattuale per ora retribuita (Cas.Sa.Colf, lavoro domestico) | core | net | native | decided | decision | `facts.contributable_hours` | — | verified | 3 / 0 / 0 / 0 |

## CCNL coverage

The same cells as the [CCNL Coverage index](index.md). **Limits** names the
capabilities a `missing` note or a model limitation with a monetary impact
of the contract file lowers to partial. **Rules** counts the payable rules
of the contract file by provenance status: verified / derived / assumed /
missing. The `assumed` and `missing` ones are listed in the shrink-only
evidence baseline (`scripts/provenance/baseline.json`), so these counts
never grow.

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |


| # | CCNL | Core | Limits | Rules (v / d / a / m) |
|---|---|:---:|---|---|
| 1 | [CCNL Acconciatura ed Estetica — Confartigianato/CNA](acconciatura-estetica-confartigianato.md) | ⚠️ | base_salary, inps_employer | 0 / 29 / 1 / 0 |
| 2 | [CCNL Agenzie Marittime Raccomandatarie, Agenzie Aeree e Mediatori Marittimi](agenzie-marittime-i481.md) | ⚠️ | base_salary, seniority | 0 / 36 / 2 / 0 |
| 3 | [CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio](agenzie-viaggio-fiavet.md) | ⚠️ | seniority, trattamento_integrativo | 0 / 68 / 1 / 1 |
| 4 | [CCNL Alimentaristi Cooperative (Fedagripesca/Legacoop Agroalimentare/AGCI-Agrital)](alimentaristi-cooperative-e016.md) | ⚠️ | base_salary, seniority | 0 / 70 / 1 / 1 |
| 5 | [CCNL Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)](panificazione-artigianato-confartigianato.md) | ⚠️ | inps_employer, territorial_supplement | 1 / 47 / 0 / 0 |
| 6 | [CCNL Area Comunicazione — Artigianato](comunicazione-artigianato-confartigianato.md) | ⚠️ | base_salary, inps_employer, worker_category | 0 / 40 / 1 / 0 |
| 7 | [CCNL Area Dirigenza Funzioni Centrali 2022-2024 — ARAN](dirigenza-funzioni-centrali-aran.md) | ✅ | — | 0 / 13 / 0 / 0 |
| 8 | [CCNL Area Dirigenza Funzioni Locali 2022-2024 — ARAN](dirigenza-funzioni-locali-aran.md) | ✅ | — | 0 / 9 / 0 / 0 |
| 9 | [CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN](dirigenza-istruzione-ricerca-aran.md) | ✅ | — | 0 / 13 / 0 / 0 |
| 10 | [CCNL Area Legno-Lapidei — Artigianato](legno-lapidei-artigianato-confartigianato.md) | ⚠️ | base_salary, inps_employer | 0 / 38 / 2 / 0 |
| 11 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)](dirigenza-sanitaria-medico-veterinaria-aran.md) | ⚠️ | base_salary | 0 / 8 / 1 / 1 |
| 12 | [CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi, fisici, chimici)](dirigenza-sanitaria-area-sanita-aran.md) | ⚠️ | base_salary | 0 / 10 / 0 / 0 |
| 13 | [CCNL Area Tessile-Moda e Chimica-Ceramica — Artigianato](tessile-moda-artigianato-confartigianato.md) | ⚠️ | base_salary, inps_employer, seniority | 0 / 36 / 1 / 0 |
| 14 | [CCNL Attivita Agromeccaniche (Contoterzismo) CAI Agromec-FAI-FLAI-UILA](contoterzismo-caiagromec.md) | ⚠️ | inps_employer | 0 / 48 / 1 / 1 |
| 15 | [CCNL Attivita Minerarie (ASSORISORSE)](attivita-minerarie-assorisorse.md) | ⚠️ | base_salary, seniority | 0 / 0 / 38 / 1 |
| 16 | [CCNL Attività Ferroviarie — AGENS](trasporto-ferroviario-agens.md) | ⚠️ | base_salary, seniority | 0 / 55 / 1 / 1 |
| 17 | [CCNL Autoferrotranvieri e Internavigatori (Mobilita/TPL)](autoferrotranvieri-internavigatori.md) | ⚠️ | inps_employer, seniority | 0 / 138 / 1 / 1 |
| 18 | [CCNL Autorimesse, Noleggio Automezzi e Parcheggi (ANIASA)](autorimesse-ic35.md) | ⚠️ | base_salary, seniority | 0 / 95 / 1 / 1 |
| 19 | [CCNL Autostrade e Trafori Concessionari](autostrade-trafori.md) | ⚠️ | seniority | 0 / 140 / 1 / 1 |
| 20 | [CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)](ced-assoced.md) | ⚠️ | base_salary, inps_employer | 0 / 44 / 1 / 1 |
| 21 | [CCNL Carta e Cartone — Aziende Industriali (Assocarta)](carta-cartone-assocarta.md) | ⚠️ | seniority | 0 / 74 / 2 / 0 |
| 22 | [CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)](sanita-privata-aiop-aris.md) | ✅ | overtime | 36 / 1 / 0 / 0 |
| 23 | [CCNL Cemento, Calce e Gesso — Industria (Federbeton)](cemento-calce-gesso-industria.md) | ⚠️ | base_salary, seniority | 0 / 80 / 2 / 0 |
| 24 | [CCNL Ceramica Industria (Confindustria-Assopiastrelle)](ceramica-industria-confindustria.md) | ⚠️ | seniority | 0 / 60 / 1 / 1 |
| 25 | [CCNL Chimica e Affini PMI — Unionchimica Confapi](chimica-affini-pmi-unionchimica.md) | ⚠️ | base_salary, seniority | 0 / 21 / 1 / 1 |
| 26 | [CCNL Comparto Funzioni Centrali — Triennio 2022-2024](funzioni-centrali-aran.md) | ⚠️ | inps_employer | 26 / 5 / 0 / 0 |
| 27 | [CCNL Comparto Funzioni Locali 2022-2024 — ARAN](funzioni-locali-aran.md) | ⚠️ | base_salary | 18 / 9 / 0 / 0 |
| 28 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN](istruzione-ricerca-aran.md) | ⚠️ | inps_employee, overtime | 48 / 6 / 36 / 0 |
| 29 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, AFAM (Alta formazione artistica, musicale e coreutica)](afam-aran.md) | ✅ | pension_fund_contribution, sickness | 24 / 13 / 2 / 0 |
| 30 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, Enti pubblici di ricerca (ASI compresa)](enti-ricerca-aran.md) | ⚠️ | base_salary, pension_fund_contribution, sickness | 32 / 4 / 1 / 0 |
| 31 | [CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, Università (personale tecnico-amministrativo e CEL)](universita-aran.md) | ✅ | pension_fund_contribution, sickness | 20 / 4 / 5 / 0 |
| 32 | [CCNL Comparto Istruzione e Ricerca 2025-2027 (trattamento economico) - ARAN, Università, tecnologi a tempo indeterminato](universita-tecnologi-aran.md) | ✅ | pension_fund_contribution, sickness | 2 / 4 / 1 / 0 |
| 33 | [CCNL Comparto Sanità 2022-2024 — ARAN](sanita-aran.md) | ⚠️ | base_salary | 16 / 5 / 0 / 0 |
| 34 | [CCNL Comunicazione, Informatica e Servizi Innovativi PMI — Settore Informatico](informatica-pmi-unimatica.md) | ⚠️ | base_salary, seniority | 0 / 40 / 2 / 0 |
| 35 | [CCNL Consorzi Agrari (ASSOCAP-FLAI-FAI-UILA)](consorzi-agrari-assocap.md) | ⚠️ | base_salary, health_fund_employer, inps_employer | 0 / 36 / 1 / 1 |
| 36 | [CCNL Consorzi di Bonifica (SNEBI-FLAI-FAI-FILBI)](consorzi-di-bonifica-snebi.md) | ⚠️ | base_salary, inps_employer, seniority | 0 / 56 / 1 / 1 |
| 37 | [CCNL Cooperative Sociali (Confcooperative/Legacoop/AGCI)](cooperative-sociali.md) | ⚠️ | base_salary, inps_employer | 62 / 1 / 0 / 0 |
| 38 | [CCNL Cooperative e Consorzi Agricoli](cooperative-consorzi-agricoli.md) | ⚠️ | base_salary, inps_employer, seniority | 32 / 9 / 1 / 0 |
| 39 | [CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa](federcasa.md) | ✅ | — | 0 / 23 / 2 / 0 |
| 40 | [CCNL Dipendenti Piccola e Media Industria Alimentare (Unionalimentari-Confapi)](alimentari-pmi-unionalimentari.md) | ⚠️ | base_salary | 0 / 44 / 1 / 1 |
| 41 | [CCNL Dipendenti da Proprietari di Fabbricati (Confedilizia)](portieri-fabbricati-confedilizia.md) | ⚠️ | seniority | 0 / 37 / 1 / 1 |
| 42 | [CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)](farmacie-municipalizzate-assofarm.md) | ⚠️ | inps_employer, seniority | 0 / 45 / 2 / 0 |
| 43 | [CCNL Dipendenti delle Farmacie Private](farmacie-private-h121.md) | ⚠️ | seniority | 0 / 37 / 1 / 1 |
| 44 | [CCNL Distribuzione Cooperativa (ANCC-Coop / Confcooperative Consumo)](distribuzione-cooperativa-ancc.md) | ⚠️ | seniority | 0 / 62 / 2 / 0 |
| 45 | [CCNL Edilizia PMI CONFAPI ANIEM](edilizia-pmi-confapi-aniem.md) | ⚠️ | base_salary, bilateral_funds, pension_fund_contribution, seniority | 14 / 30 / 2 / 0 |
| 46 | [CCNL Edilizia e Affini Artigianato](edilizia-artigianato-cna.md) | ⚠️ | bilateral_funds, inps_employer, pension_fund_contribution, seniority | 0 / 72 / 1 / 0 |
| 47 | [CCNL Edilizia — Cooperative (ANCPL/Legacoop/Confcooperative/AGCI)](edilizia-cooperative-ancpl.md) | ⚠️ | seniority | 0 / 57 / 1 / 1 |
| 48 | [CCNL Edilizia — Industria (ANCE), impiegati e quadri](edilizia-ance-impiegati.md) | ⚠️ | base_salary, seniority, sickness | 32 / 23 / 0 / 0 |
| 49 | [CCNL Edilizia — Industria (ANCE), operai](edilizia-ance.md) | ⚠️ | base_salary, overtime, sickness | 31 / 8 / 0 / 0 |
| 50 | [CCNL Energia e Petrolio (Confindustria Energia)](energia-petrolio-confindustria.md) | ✅ | — | 0 / 170 / 1 / 1 |
| 51 | [CCNL Esercizi Cinematografici e Cinema-Teatrali (ANEC)](esercizi-cinematografici-anec.md) | ⚠️ | inps_employer, seniority | 0 / 54 / 2 / 0 |
| 52 | [CCNL Fiori Freschi Recisi, Verde e Piante Ornamentali (ANCEF)](fiori-recisi-ancef.md) | ⚠️ | seniority | 0 / 38 / 1 / 1 |
| 53 | [CCNL Formazione Professionale (CNOS-FAP/CIOFS-FP/FORMA/CNF)](formazione-professionale.md) | ✅ | — | 0 / 33 / 1 / 1 |
| 54 | [CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas](gas-acqua-utilitalia.md) | ⚠️ | inps_employer, seniority | 0 / 62 / 2 / 0 |
| 55 | [CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)](gomma-plastica-federazione-gomma-plastica.md) | ⚠️ | base_salary, seniority | 0 / 77 / 1 / 1 |
| 56 | [CCNL Grafica e Editoria Industria (AIEG-Acigraf)](grafica-editoria-aieg.md) | ⚠️ | seniority | 0 / 71 / 1 / 1 |
| 57 | [CCNL Gruppo ANAS](anas.md) | ⚠️ | seniority | 0 / 42 / 2 / 0 |
| 58 | [CCNL Igiene Ambientale — Servizi Ambientali e di Igiene Urbana](igiene-ambientale-utilitalia.md) | ⚠️ | inps_employer, pension_fund_contribution, seniority | 0 / 143 / 1 / 1 |
| 59 | [CCNL Impianti e Attività Sportive Profit e No-profit](impianti-sportivi-sport.md) | ⚠️ | base_salary, overtime, sickness | 0 / 32 / 1 / 1 |
| 60 | [CCNL Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti](impiegati-tecnici-agricoli.md) | ⚠️ | base_salary, bilateral_funds, inps_employer | 0 / 15 / 1 / 1 |
| 61 | [CCNL Industria Chimica e Farmaceutica (Federchimica-Farmindustria-Assistal)](chimica-farmaceutica-federchimica.md) | ⚠️ | base_salary | 111 / 5 / 0 / 0 |
| 62 | [CCNL Industria Turistica (Federturismo Confindustria)](industria-turistica-federturismo.md) | ⚠️ | seniority, trattamento_integrativo | 0 / 46 / 1 / 0 |
| 63 | [CCNL Industrie Cineaudiovisive (ANICA)](cinema-audiovisivi-industria.md) | ⚠️ | bilateral_funds, inps_employer | 0 / 62 / 1 / 1 |
| 64 | [CCNL Istituti e Imprese di Vigilanza Privata e Servizi Fiduciari — ASSIV/ANIVP/UNIV (GPG)](vigilanza-privata-assiv.md) | ⚠️ | inps_employer, seniority | 0 / 48 / 2 / 0 |
| 65 | [CCNL Istituzioni Formative Private (Scuole Private Religiose) — AGIDAE](scuole-private-agidae.md) | ✅ | — | 0 / 43 / 1 / 1 |
| 66 | [CCNL Istituzioni Socio-Assistenziali — UNEBA](uneba-uneba.md) | ⚠️ | base_salary, seniority | 0 / 41 / 2 / 0 |
| 67 | [CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)](istituzioni-servizi-socio-assistenziali-anaste.md) | ⚠️ | seniority | 0 / 31 / 2 / 0 |
| 68 | [CCNL Lapidei — Industria (Confindustria Marmomacchine/ANEPLA)](lapidei-industria.md) | ⚠️ | base_salary, inps_employer, seniority | 0 / 79 / 1 / 1 |
| 69 | [CCNL Laterizi e Manufatti Cementizi - Industria](laterizi-industria-f021.md) | ⚠️ | base_salary, seniority | 0 / 98 / 2 / 0 |
| 70 | [CCNL Lavanderie Industriali (Assosistema Confindustria)](lavanderie-industriali-assosistema.md) | ⚠️ | seniority | 0 / 37 / 1 / 1 |
| 71 | [CCNL Lavoratori Dipendenti Organizzazioni Sindacali (UNSIC/CONFSAL)](ooss-unsic-confsal.md) | ⚠️ | base_salary, seniority | 0 / 19 / 2 / 0 |
| 72 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi a orario ridotto, art. 14 c. 2)](lavoro-domestico-convivente-orario-ridotto.md) | ⚠️ | assistance_contribution, base_salary, inps_employer, overtime, sickness | 13 / 2 / 0 / 0 |
| 73 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)](lavoro-domestico-convivente.md) | ⚠️ | assistance_contribution, base_salary, inps_employer, seniority, sickness | 26 / 1 / 0 / 0 |
| 74 | [CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)](lavoro-domestico-non-convivente.md) | ⚠️ | assistance_contribution, base_salary, seniority, sickness | 16 / 1 / 0 / 0 |
| 75 | [CCNL Logistica, Trasporto Merci e Spedizione (Confetra)](logistica-trasporto-confetra.md) | ⚠️ | overtime, seniority | 62 / 1 / 0 / 0 |
| 76 | [CCNL Logistica, Trasporto Merci e Spedizione (Confetra) - Personale viaggiante](logistica-trasporto-confetra-viaggiante.md) | ⚠️ | base_salary, seniority | 53 / 30 / 0 / 0 |
| 77 | [CCNL Marittimi — Industria Armatoriale (CONFITARMA)](marittimi-industria-armatoriale.md) | ⚠️ | seniority | 0 / 40 / 2 / 0 |
| 78 | [CCNL Materiali da Costruzione PMI — Lapidei (CONFAPI ANIEM)](materiali-costruzione-lapidei-confapi.md) | ⚠️ | inps_employer, pension_fund_contribution | 0 / 0 / 70 / 0 |
| 79 | [CCNL Metalmeccanica - Cooperative](metalmeccanica-cooperative.md) | ⚠️ | base_salary, seniority | 0 / 45 / 1 / 1 |
| 80 | [CCNL Metalmeccanica e Installazione di Impianti — Artigianato](metalmeccanico-artigianato.md) | ⚠️ | inps_employer, overtime | 32 / 49 / 0 / 0 |
| 81 | [CCNL Metalmeccanici Piccola Industria (CONFIMI IMPRESA MECCANICA)](metalmeccanico-confimi-pmi.md) | ✅ | overtime | 0 / 44 / 0 / 1 |
| 82 | [CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)](metalmeccanico-confapi.md) | ⚠️ | base_salary, pension_fund_contribution | 58 / 7 / 0 / 0 |
| 83 | [CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)](metalmeccanico-federmeccanica.md) | ⚠️ | overtime, seniority | 85 / 0 / 0 / 0 |
| 84 | [CCNL Noleggio Autobus con Conducente (ANAV)](noleggio-autobus-conducente-anav.md) | ⚠️ | base_salary, seniority, una_tantum | 0 / 0 / 70 / 1 |
| 85 | [CCNL Occhiali e Occhialeria — Industria (ANFAO)](occhiali-occhialeria-industria.md) | ⚠️ | base_salary, seniority | 0 / 88 / 1 / 1 |
| 86 | [CCNL Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA](operai-agricoli-florovivaisti.md) | ⚠️ | base_salary, bilateral_funds, inail, inps_employee, inps_employer, seniority, sickness, territorial_supplement | 5 / 13 / 1 / 1 |
| 87 | [CCNL Organizzazioni Allevatori, Consorzi ed Enti Zootecnici (AIA-FLAI-FAI-UILA)](organizzazioni-allevatori-aia.md) | ⚠️ | base_salary, inps_employer | 0 / 20 / 1 / 1 |
| 88 | [CCNL Ortofrutticoli ed Agrumari (Import-Export)](ortofrutticoli-agrumari.md) | ⚠️ | base_salary, leave, seniority, sickness | 0 / 0 / 53 / 1 |
| 89 | [CCNL Panificazione e Settori Affini — Industria (Assipan/Fiesa)](panificazione-assipan.md) | ⚠️ | seniority | 0 / 48 / 1 / 1 |
| 90 | [CCNL Poste Italiane S.p.A. (personale non dirigente)](poste-italiane-k700.md) | ⚠️ | base_salary, inps_employer | 0 / 53 / 2 / 0 |
| 91 | [CCNL RSA e Strutture Residenziali Socio-Assistenziali (AIOP)](rsa-aiop.md) | ⚠️ | seniority | 0 / 31 / 2 / 0 |
| 92 | [CCNL Radiotelevisivo — Settore Radiofonico](radiotelevisive-radiofonico.md) | ⚠️ | seniority | 0 / 0 / 20 / 1 |
| 93 | [CCNL Radiotelevisivo — Settore Televisivo Multimediale](radiotelevisive-televisivo.md) | ⚠️ | seniority | 0 / 0 / 38 / 1 |
| 94 | [CCNL Recapito Corrispondenza (FISE-ARE)](recapito-corrispondenza-fise.md) | ✅ | — | 0 / 47 / 1 / 1 |
| 95 | [CCNL Scuole Materne — FISM](scuole-materne-fism.md) | ⚠️ | base_salary, seniority | 0 / 47 / 2 / 0 |
| 96 | [CCNL Scuole Private Laiche (ANINSEI-Assoscuola)](scuole-private-laiche-aninsei.md) | ⚠️ | seniority | 0 / 43 / 2 / 0 |
| 97 | [CCNL Servizi Postali in Appalto (FISE-ARE)](servizi-postali-appalto-fise.md) | ⚠️ | base_salary, seniority | 0 / 49 / 2 / 0 |
| 98 | [CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)](multiservizi-anip.md) | ⚠️ | base_salary | 57 / 93 / 0 / 0 |
| 99 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Impiegati)](sistemazioni-idraulico-forestali-impiegati.md) | ⚠️ | base_salary, inps_employer, seniority | 0 / 27 / 2 / 1 |
| 100 | [CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Operai OTI)](sistemazioni-idraulico-forestali-operai.md) | ⚠️ | base_salary, inps_employer, seniority | 0 / 20 / 2 / 1 |
| 101 | [CCNL Telecomunicazioni — Assotelecomunicazioni (Asstel)](telecomunicazioni-asstel.md) | ⚠️ | inps_employer, seniority | 0 / 45 / 2 / 0 |
| 102 | [CCNL Terziario Distribuzione e Servizi — Confesercenti](terziario-confesercenti.md) | ⚠️ | base_salary, seniority, sickness, una_tantum | 75 / 0 / 0 / 0 |
| 103 | [CCNL Terziario, Distribuzione e Servizi (Confcommercio)](commercio-confcommercio.md) | ⚠️ | seniority, sickness | 69 / 0 / 0 / 0 |
| 104 | [CCNL Tessile-Abbigliamento-Moda PMI (Uniontessile-Confapi)](tessile-pmi-uniontessile.md) | ⚠️ | base_salary, pension_fund_contribution | 0 / 0 / 43 / 1 |
| 105 | [CCNL Trasporto Aereo — Gestori Aeroportuali](trasporto-aereo-assaeroporti.md) | ⚠️ | base_salary, seniority | 0 / 72 / 2 / 0 |
| 106 | [CCNL Trasporto a Fune (Funivie Terrestri ed Aeree) - ANEF](funivie-anef.md) | ⚠️ | seniority | 0 / 47 / 1 / 1 |
| 107 | [CCNL Turismo (Assoturismo-Confesercenti)](turismo-confesercenti.md) | ⚠️ | seniority, trattamento_integrativo | 0 / 57 / 1 / 0 |
| 108 | [CCNL Turismo — Federalberghi/Faita](turismo-federalberghi.md) | ⚠️ | base_salary, seniority, sickness, trattamento_integrativo | 71 / 1 / 0 / 0 |
| 109 | [CCNL Vetro (Industrie) — Settori Meccanizzati (Prime Lavorazioni)](vetro-meccanizzato-assovetro.md) | ⚠️ | base_salary | 0 / 0 / 35 / 1 |
| 110 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG](vigilanza-privata-federdat-gpg.md) | ⚠️ | seniority | 0 / 48 / 1 / 1 |
| 111 | [CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — SF](vigilanza-privata-federdat-sf.md) | ⚠️ | seniority | 0 / 46 / 2 / 1 |
| 112 | [CCNL per i dipendenti da agenti immobiliari professionali e mandatari a titolo oneroso](agenti-immobiliari-fiaip.md) | ⚠️ | base_salary, bilateral_funds, pension_fund_contribution, seniority, una_tantum | 0 / 0 / 30 / 1 |
| 113 | [CCNL per i dipendenti da autoscuole, scuole nautiche e studi di consulenza automobilistica](autoscuole-unasca.md) | ⚠️ | bilateral_funds, health_fund_employer, seniority | 0 / 32 / 2 / 0 |
| 114 | [CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo](pubblici-esercizi-fipe-angem.md) | ⚠️ | base_salary, overtime, seniority, sickness, trattamento_integrativo | 61 / 2 / 0 / 0 |
| 115 | [CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo - Ristorazione collettiva (aziende dell'art. 1 c. 1 par. II)](pubblici-esercizi-fipe-angem-ristorazione-collettiva.md) | ⚠️ | base_salary, overtime, seniority, trattamento_integrativo | 61 / 2 / 0 / 0 |
| 116 | [CCNL per i dipendenti dalle aziende di lavorazione della foglia di tabacco secco allo stato sciolto](tabacco-apti.md) | ⚠️ | pension_fund_contribution, seniority | 0 / 0 / 58 / 1 |
| 117 | [CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)](studi-professionali-confprofessioni.md) | ⚠️ | base_salary, inps_employer, seniority | 46 / 0 / 0 / 0 |
| 118 | [CCNL per i dipendenti delle imprese artigiane esercenti servizi di pulizia, disinfezione, disinfestazione, derattizzazione e sanificazione](pulizia-artigianato-confartigianato.md) | ⚠️ | base_salary, bilateral_funds, holiday_work, inps_employer, leave, night_work, overtime, seniority | 0 / 0 / 86 / 1 |
| 119 | [CCNL per i lavoratori addetti all'industria delle calzature](calzaturiero-assocalzaturifici.md) | ⚠️ | seniority | 0 / 37 / 1 / 1 |
| 120 | [CCNL per i lavoratori addetti all'industria orafa, argentiera e della gioielleria (Federorafi)](orafi-argentieri-industria-federorafi.md) | ⚠️ | seniority | 0 / 40 / 2 / 0 |
| 121 | [CCNL per i lavoratori addetti alle industrie delle pelli e dei succedanei della pelle (Assopellettieri)](pelli-cuoio-industria-assopellettieri.md) | ⚠️ | base_salary, seniority | 0 / 35 / 1 / 1 |
| 122 | [CCNL per i lavoratori dell'industria alimentare (Federalimentare)](alimentari-federalimentare.md) | ⚠️ | base_salary, overtime, sickness | 75 / 0 / 0 / 0 |
| 123 | [CCNL per i lavoratori dell'industria conciaria (UNIC)](concia-unic.md) | ⚠️ | overtime, seniority | 57 / 1 / 0 / 0 |
| 124 | [CCNL per i lavoratori dell'industria del legno, del sughero, del mobile, dell'arredamento e delle industrie affini (Federlegno-Arredo)](legno-arredamento-federlegno.md) | ⚠️ | base_salary, seniority | 0 / 88 / 2 / 0 |
| 125 | [CCNL per i lavoratori dell'industria tessile, abbigliamento, moda (SMI)](tessile-smi.md) | ⚠️ | seniority | 0 / 47 / 1 / 1 |
| 126 | [CCNL per i lavoratori delle Banche di Credito Cooperativo, Casse Rurali ed Artigiane](bcc-credito-cooperativo.md) | ⚠️ | base_salary, inps_employer, seniority | 35 / 7 / 0 / 1 |
| 127 | [CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)](elettrico-elettricita-futura.md) | ⚠️ | seniority | 0 / 77 / 1 / 1 |
| 128 | [CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)](bancari-abi.md) | ⚠️ | base_salary, inps_employer, seniority | 37 / 8 / 0 / 0 |
| 129 | [CCNL per i lavoratori dipendenti delle aziende termali](aziende-termali-federterme.md) | ⚠️ | base_salary, bilateral_funds, inps_employer, seniority, trattamento_integrativo | 0 / 64 / 1 / 1 |
| 130 | [CCNL per il personale dipendente non dirigente delle imprese di assicurazione (ANIA)](assicurazioni-ania.md) | ⚠️ | base_salary, inps_employer, seniority | 0 / 30 / 1 / 1 |
| 131 | [DPR 24 marzo 2025, n. 53 — Forze di Polizia ad ordinamento civile (Triennio 2022-2024)](forze-polizia-ordinamento-civile.md) | ⚠️ | inps_employer | 0 / 70 / 1 / 1 |
| 132 | [Distribuzione Moderna Organizzata — Federdistribuzione](dmo-federdistribuzione.md) | ⚠️ | base_salary, seniority, sickness, territorial_supplement | 77 / 1 / 0 / 0 |
