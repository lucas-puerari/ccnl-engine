# CCNL Coverage

100+ contract configurations covering approximately **16 million employees** across
private and public sectors.

The 100+ configurations include 100+ distinct CCNLs — CCNL Lavoro Domestico is split
into two variants (convivente / non-convivente) and CCNL Vigilanza Privata FEDERDAT
into two profiles (GPG / Servizi Fiduciari) — plus one Presidential Decree (DPR
53/2025) for Forze di Polizia ad ordinamento civile. They cover 75+ of the ~99
private-sector CCNLs that CNEL classifies as major (>10,000 employees), plus 10
public-sector ARAN/DPR contracts covering approximately 2.8 million workers. Per CNEL
(II semester 2024), the ~99 major private-sector CCNLs together cover 13.4 million
workers — 96.9% of Italy's private-sector workforce.

→ [Domain: What is a CCNL](../domain/index.md) — terminology used in this table.

## Legend

| Symbol | Meaning |
|---|---|
| ✅ | Fully modelled; all salary tables and rules for this layer are in scope |
| ⚠️ | Partially modelled; see `coverage.notes` in the contract's JSON file |
| 🤖 | Extracted automatically (AI-assisted), no manual human review |
| 🧑 | Verified manually against the official source |

**Layer 1:** base salary, seniority increments, fixed allowances, additional months.  
**Layer 2:** part-time, fixed-term (NASpI), apprenticeship (percentage or under-classification).

## Matrix

| # | CNEL code | CCNL | Sector | Workers (~)[^1] | L1 | L2 | Extraction[^2] |
|---|---|---|---|---:|:---:|:---:|:---:|
| 1 | H011 | [Commercio — Confcommercio](commercio-confcommercio.md) | Terziario | ~800k | ✅ | ✅ | 🤖 |
| 2 | C011 | [Metalmeccanico — Federmeccanica/Assistal](metalmeccanico-federmeccanica.md) | Industria | ~1,7M | ✅ | ✅ | 🤖 |
| 3 | C018 | [Metalmeccanico PMI — Unionmeccanica-Confapi](metalmeccanico-confapi.md) | Industria | ~350k | ✅ | ✅ | 🤖 |
| 4 | B011 | [Chimica-Farmaceutica — Federchimica/Farmindustria/Assistal](chimica-farmaceutica-federchimica.md) | Industria | ~210k | ✅ | ✅ | 🤖 |
| 5 | H052 | [Turismo — Confcommercio](turismo-confcommercio.md) | Terziario | ~300k | ✅ | ✅ | 🤖 |
| 6 | F012 | [Edilizia — ANCE](edilizia-ance.md) | Edilizia | ~550k | ✅ | ✅ | 🤖 |
| 7 | T151 | [Cooperative Sociali — Confcooperative/Legacoop/AGCI](cooperative-sociali.md) | Terziario | ~380k | ✅ | ✅ | 🤖 |
| 8 | I100 | [Logistica, Trasporto Merci e Spedizione — Confetra](logistica-trasporto-confetra.md) | Industria | ~430k | ✅ | ✅ | 🤖 |
| 9 | K511 | [Servizi di Pulizia e Multiservizi — ANIP-Confindustria](multiservizi-anip.md) | Terziario | ~580k | ✅ | ✅ | 🤖 |
| 10 | H442 | [Studi e Attività Professionali — Confprofessioni](studi-professionali-confprofessioni.md) | Terziario | ~350k | ✅ | ✅ | 🤖 |
| 11 | J241 | [Credito — ABI](bancari-abi.md) | Credito | ~270k | ✅ | ✅ | 🤖 |
| 12 | D014 | [Tessile Abbigliamento Moda — SMI](tessile-smi.md) | Industria | ~160k | ✅ | ✅ | 🤖 |
| 13 | E012 | [Alimentari Industria — Federalimentare](alimentari-federalimentare.md) | Industria | ~145k | ✅ | ✅ | 🤖 |
| 14 | H008 | [Distribuzione Moderna Organizzata — Federdistribuzione](dmo-federdistribuzione.md) | Terziario | ~460k | ✅ | ✅ | 🤖 |
| 15 | C030 | [Metalmeccanica e Installazione Impianti — Artigianato](metalmeccanico-artigianato.md) | Artigianato | ~350k | ✅ | ✅ | 🤖 |
| 16 | B371 | [Gomma e Plastica Industria — Federazione Gomma Plastica](gomma-plastica-federazione-gomma-plastica.md) | Industria | ~90k | ✅ | ✅ | 🤖 |
| 17 | G011 | [Grafica e Editoria — AIEG-Acigraf](grafica-editoria-aieg.md) | Industria | ~70k | ✅ | ✅ | 🤖 |
| 18 | G022 | [Carta e Cartone — Assocarta](carta-cartone-assocarta.md) | Industria | ~35k | ✅ | ✅ | 🤖 |
| 19 | K411 | [Telecomunicazioni — Asstel](telecomunicazioni-asstel.md) | Industria | ~110k | ✅ | ✅ | 🤖 |
| 20 | HV40 | [Vigilanza Privata — ASSIV/ANIVP/UNIV (GPG)](vigilanza-privata-assiv.md) | Terziario | ~85k | ✅ | ✅ | 🤖 |
| 21 | F051 | [Legno e Arredamento — Federlegno-Arredo](legno-arredamento-federlegno.md) | Industria | ~90k | ✅ | ✅ | 🤖 |
| 22 | F015 | [Edilizia e Affini — CNA/Confartigianato/Casartigiani](edilizia-artigianato-cna.md) | Artigianato | ~350k | ✅ | ✅ | 🤖 |
| 23 | K321 | [Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas](gas-acqua-utilitalia.md) | Industria | ~65k | ✅ | ✅ | 🤖 |
| 24 | T141 | [Istituzioni Socio-Assistenziali — UNEBA](uneba-uneba.md) | Terziario | ~130k | ✅ | ✅ | 🤖 |
| 25 | H515 | [Acconciatura ed Estetica — Confartigianato/CNA](acconciatura-estetica-confartigianato.md) | Artigianato | ~95k | ✅ | ✅ | 🤖 |
| 26 | E015 | [Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)](panificazione-artigianato-confartigianato.md) | Artigianato | ~90k | ✅ | ✅ | 🤖 |
| 27 | I022 | [Autoferrotranvieri e Internavigatori (Mobilita/TPL) — AGENS/ASSTRA/ANAV](autoferrotranvieri-internavigatori.md) | Terziario | ~120k | ✅ | ✅ | 🤖 |
| 28 | J271 | [Credito Cooperativo (BCC/CRA) — Federcasse](bcc-credito-cooperativo.md) | Credito | ~33k | ✅ | ✅ | 🤖 |
| 29 | K051 | [Elettrico (produzione/distribuzione energia) — Elettricita Futura](elettrico-elettricita-futura.md) | Industria | ~60k | ✅ | ✅ | 🤖 |
| 30 | D121 | [Calzaturiero (industria delle calzature) — Assocalzaturifici](calzaturiero-assocalzaturifici.md) | Industria | ~75k | ✅ | ✅ | 🤖 |
| 31 | V751 | [Area Tessile-Moda e Chimica-Ceramica — Artigianato (Confartigianato/CNA)](tessile-moda-artigianato-confartigianato.md) | Artigianato | ~120k | ✅ | ✅ | 🤖 |
| 32 | F060 | [Area Legno-Lapidei — Artigianato (Confartigianato/CNA)](legno-lapidei-artigianato-confartigianato.md) | Artigianato | ~95k | ✅ | ✅ | 🤖 |
| 33 | G016 | [Area Comunicazione — Artigianato (Confartigianato/CNA)](comunicazione-artigianato-confartigianato.md) | Artigianato | ~60k | ✅ | ✅ | 🤖 |
| 34 | B122 | [Ceramica Industria — Confindustria Ceramica (Assopiastrelle)](ceramica-industria-confindustria.md) | Industria | ~23k | ✅ | ✅ | 🤖 |
| 35 | C021 | [Orafi e Argentieri — Federorafi](orafi-argentieri-industria-federorafi.md) | Industria | ~18k | ✅ | ✅ | 🤖 |
| 36 | D111 | [Pelli e Cuoio Industria — Assopellettieri](pelli-cuoio-industria-assopellettieri.md) | Industria | ~17k | ✅ | ✅ | 🤖 |
| 37 | H05Y | [Pubblici Esercizi, Ristorazione Collettiva e Turismo — FIPE/ANGEM](pubblici-esercizi-fipe-angem.md) | Terziario | ~350k | ✅ | ✅ | 🤖 |
| 38 | H052 | [Agenzie di Viaggio e Turismo — Fiavet/Confcommercio](agenzie-viaggio-fiavet.md) | Terziario | ~25k | ✅ | ✅ | 🤖 |
| 39 | H012 | [Terziario Distribuzione e Servizi — Confesercenti](terziario-confesercenti.md) | Terziario | ~230k | ✅ | ✅ | 🤖 |
| 40 | H052 | [Turismo — Federalberghi/Faita](turismo-federalberghi.md) | Terziario | ~220k | ✅ | ✅ | 🤖 |
| 41 | S005 | [Funzioni Centrali 2022-2024 — ARAN (Ministeri, Agenzie, INPS, INAIL)](funzioni-centrali-aran.md) | Pubblica Amministrazione | ~250k | ✅ | ✅ | 🤖 |
| 42 | S105 | [Funzioni Locali 2022-2024 — ARAN (Comuni, Province, Regioni, CC)](funzioni-locali-aran.md) | Pubblica Amministrazione | ~400k | ✅ | ✅ | 🤖 |
| 43 | S205 | [Comparto Sanità 2022-2024 — ARAN (SSN non-dirigenza)](sanita-aran.md) | Pubblica Amministrazione | ~580k | ✅ | ✅ | 🤖 |
| 44 | S225 | [Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)](dirigenza-sanitaria-medico-veterinaria-aran.md) | Pubblica Amministrazione | ~100k | ✅ | ✅ | 🤖 |
| 45 | S225 | [Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari)](dirigenza-sanitaria-area-sanita-aran.md) | Pubblica Amministrazione | ~37k | ✅ | ✅ | 🤖 |
| 46 | S125 | [Area Dirigenza Funzioni Locali 2022-2024 — ARAN](dirigenza-funzioni-locali-aran.md) | Pubblica Amministrazione | ~13k | ✅ | ✅ | 🤖 |
| 47 | S025 | [Area Dirigenza Funzioni Centrali 2022-2024 — ARAN](dirigenza-funzioni-centrali-aran.md) | Pubblica Amministrazione | ~30k | ✅ | ✅ | 🤖 |
| 48 | S325 | [Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN](dirigenza-istruzione-ricerca-aran.md) | Pubblica Amministrazione | ~8k | ✅ | ✅ | 🤖 |
| 49 | S305 | [Comparto Istruzione e Ricerca 2022-2024 — ARAN](istruzione-ricerca-aran.md) | Pubblica Amministrazione | ~1,2M | ✅ | ✅ | 🤖 |
| 50 | T011 | [Case di Cura Private — AIOP/ARIS](sanita-privata-aiop-aris.md) | Sanità privata | ~150k | ✅ | ✅ | 🤖 |
| 51 | H501 | [Lavoro Domestico — conviventi](lavoro-domestico-convivente.md) | Lavoro Domestico | ~900k | ✅ | ✅ | 🤖 |
| 52 | H501 | [Lavoro Domestico — non conviventi](lavoro-domestico-non-convivente.md) | Lavoro Domestico | ~900k | ✅ | ✅ | 🤖 |
| 53 | A011 | [Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA](operai-agricoli-florovivaisti.md) | Agricoltura | ~600k | ✅ | ✅ | 🤖 |
| 54 | B018 | [Chimica e Affini PMI — Unionchimica Confapi](chimica-affini-pmi-unionchimica.md) | Chimica | ~56k | ✅ | ✅ | 🤖 |
| 55 | E023 | [Panificazione e Settori Affini Industria — Assipan](panificazione-assipan.md) | Alimentare | ~20k | ✅ | ✅ | 🤖 |
| 56 | I320 | [Attività Ferroviarie — AGENS](trasporto-ferroviario-agens.md) | Trasporto | ~75k | ✅ | ✅ | 🤖 |
| 57 | I810 | [Trasporto Aereo — Gestori Aeroportuali (Assaeroporti)](trasporto-aereo-assaeroporti.md) | Trasporto | ~40k | ✅ | ✅ | 🤖 |
| 58 | K540 | [Igiene Ambientale — Utilitalia/FISE](igiene-ambientale-utilitalia.md) | Industria | ~65k | ✅ | ✅ | 🤖 |
| 59 | A021 | [Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti](impiegati-tecnici-agricoli.md) | Agricoltura | ~80k | ✅ | ✅ | 🤖 |
| 60 | DPR 53/2025[^3] | [Forze di Polizia ad ordinamento civile 2022-2024](forze-polizia-ordinamento-civile.md) | Pubblica Amministrazione | ~130k | ✅ | ✅ | 🤖 |
| 61 | G029 | [Comunicazione, Informatica e Servizi Innovativi PMI — Unimatica-Confapi](informatica-pmi-unimatica.md) | Industria | ~20k | ✅ | ✅ | 🤖 |
| 62 | T241 | [Istituzioni Formative Private — AGIDAE](scuole-private-agidae.md) | Terziario | ~50k | ✅ | ⚠️ | 🤖 |
| 63 | J121 | [Assicurazioni — ANIA](assicurazioni-ania.md) | Credito | ~45k | ⚠️ | ✅ | 🤖 |
| 64 | B254 | [Energia e Petrolio — Confindustria Energia](energia-petrolio-confindustria.md) | Industria | ~38k | ✅ | ✅ | 🤖 |
| 65 | H016 | [Distribuzione Cooperativa — ANCC-Coop](distribuzione-cooperativa-ancc.md) | Terziario | ~63k | ✅ | ✅ | 🤖 |
| 66 | D0L1 | [Lavanderie Industriali — Assosistema](lavanderie-industriali-assosistema.md) | Industria | ~17k | ✅ | ✅ | 🤖 |
| 67 | H601 | [CED, ICT, Professioni Digitali e STP — Assoced](ced-assoced.md) | Terziario | ~22k | ✅ | ✅ | 🤖 |
| 68 | A051 | [Attivita Agromeccaniche (Contoterzismo) — CAI Agromec](contoterzismo-caiagromec.md) | Agricoltura | ~4k | ✅ | ✅ | 🤖 |
| 69 | A131 | [Consorzi di Bonifica — SNEBI](consorzi-di-bonifica-snebi.md) | Agricoltura | ~4k | ✅ | ✅ | 🤖 |
| 70 | A141 | [Consorzi Agrari — ASSOCAP](consorzi-agrari-assocap.md) | Agricoltura | ~2k | ✅ | ✅ | 🤖 |
| 71 | A221 | [Organizzazioni Allevatori e Enti Zootecnici — AIA](organizzazioni-allevatori-aia.md) | Agricoltura | ~2k | ✅ | ✅ | 🤖 |
| 72 | E018 | [Dipendenti PMI Alimentare — Unionalimentari-Confapi](alimentari-pmi-unionalimentari.md) | Alimentare | ~35k | ✅ | ✅ | 🤖 |
| 73 | K700 | [Poste Italiane S.p.A. (non dirigenti)](poste-italiane-k700.md) | Industria | ~117k | ✅ | ✅ | 🤖 |
| 74 | IC35 | [Autorimesse, Noleggio Automezzi e Parcheggi (ANIASA)](autorimesse-ic35.md) | Terziario | ~41k | ✅ | ✅ | 🤖 |
| 75 | H121 | [Dipendenti Farmacie Private (FEDERFARMA)](farmacie-private-h121.md) | Terziario | ~60k | ✅ | ✅ | 🤖 |
| 76 | I481 | [Agenzie Marittime Raccomandatarie — FEDERAGENTI](agenzie-marittime-i481.md) | Terziario | ~5k | ✅ | ✅ | 🤖 |
| 77 | F021 | [Laterizi e Manufatti Cementizi - Industria](laterizi-industria-f021.md) | Edilizia | ~17k | ✅ | ✅ | 🤖 |
| 78 | G211 | [Esercizi Cinematografici e Cinema-Teatrali (ANEC)](esercizi-cinematografici-anec.md) | Terziario | ~6k | ✅ | ✅ | 🤖 |
| 79 | H124 | [Farmacie Municipalizzate (ASSOFARM)](farmacie-municipalizzate-assofarm.md) | Terziario | ~6k | ✅ | ✅ | 🤖 |
| 80 | I911 | [Trasporto a Fune (Funivie Terrestri ed Aeree) — ANEF](funivie-anef.md) | Industria | ~15k | ✅ | ✅ | 🤖 |
| 81 | T611 | [Dipendenti Aziende Enti Pubblici Economici Federcasa](federcasa.md) | Case popolari | ~6k | ✅ | ✅ | 🤖 |
| 82 | H201 | [Fiori Freschi Recisi, Verde e Piante Ornamentali (ANCEF)](fiori-recisi-ancef.md) | Fiori recisi | ~1.3k | ✅ | ✅ | 🤖 |
| 83 | V925 | [Lavoratori Dipendenti Organizzazioni Sindacali (UNSIC/CONFSAL)](ooss-unsic-confsal.md) | OO.SS. | ~7k | ✅ | ✅ | 🤖 |
| 84 | K711 | [Recapito Corrispondenza (FISE-ARE)](recapito-corrispondenza-fise.md) | Recapito | ~1k | ✅ | ✅ | 🤖 |
| 85 | K721 | [Servizi Postali in Appalto (FISE-ARE)](servizi-postali-appalto-fise.md) | Servizi postali | ~1k | ✅ | ✅ | 🤖 |
| 86 | H401 | [Dipendenti da Proprietari di Fabbricati — Confedilizia](portieri-fabbricati-confedilizia.md) | Terziario | ~40k | ✅ | ✅ | 🤖 |
| 87 | C016 | [Metalmeccanica — Cooperative (Legacoop/Confcooperative/AGI)](metalmeccanica-cooperative.md) | Industria cooperativa | ~28k | ✅ | ✅ | 🤖 |
| 88 | T231 | [Scuole Private Laiche — ANINSEI/Assoscuola](scuole-private-laiche-aninsei.md) | Istruzione privata laica | ~25k | ✅ | ✅ | 🤖 |
| 89 | T131 | [Istituzioni e Servizi Socio-Assistenziali — ANASTE](istituzioni-servizi-socio-assistenziali-anaste.md) | Servizi socio-assistenziali | ~120k | ✅ | ✅ | 🤖 |
| 90 | T271 | [Scuole Materne — FISM](scuole-materne-fism.md) | Istruzione privata cattolica | ~30k | ✅ | ✅ | 🤖 |
| 91 | D271 | [Occhiali e Occhialeria — Industria (ANFAO)](occhiali-occhialeria-industria.md) | Industria occhialeria | ~20k | ✅ | ✅ | 🤖 |
| 92 | F032 | [Cemento, Calce e Gesso — Industria (Federbeton)](cemento-calce-gesso-industria.md) | Industria cemento | ~25k | ✅ | ✅ | 🤖 |
| 93 | F041 | [Lapidei — Industria (Confindustria Marmomacchine/ANEPLA)](lapidei-industria.md) | Industria lapidea | ~18k | ✅ | ✅ | 🤖 |
| 94 | I391 | [Marittimi — Industria Armatoriale (CONFITARMA)](marittimi-industria-armatoriale.md) | Navigazione marittima | ~15k | ✅ | ✅ | 🤖 |
| 95 | H05B | [Industria Turistica — Federturismo Confindustria](industria-turistica-federturismo.md) | Turismo industria | ~40k | ✅ | ✅ | 🤖 |
| 96 | E016 | [Alimentaristi Cooperative (Fedagripesca/Legacoop/AGCI)](alimentaristi-cooperative-e016.md) | Industria alimentare cooperativa | ~15k | ✅ | ✅ | 🤖 |
| 97 | H058 | [Turismo — Assoturismo-Confesercenti](turismo-confesercenti.md) | Turismo terziario | — | ✅ | ✅ | 🤖 |
| 98 | T091 | [RSA e Strutture Residenziali Socio-Assistenziali (AIOP)](rsa-aiop.md) | Sanità residenziale privata | ~17k | ✅ | ✅ | 🤖 |
| 99 | I192 | [Autostrade e Trafori Concessionari (AISCAT)](autostrade-trafori.md) | Autostrade e trafori | ~15k | ✅ | ✅ | 🤖 |
| 100 | A016 | [Cooperative e Consorzi Agricoli (AGCI/Confcooperative/Legacoop)](cooperative-consorzi-agricoli.md) | Agricoltura cooperativa | ~60k | ✅ | ⚠️ | 🤖 |
| 101 | T511 | [Gruppo ANAS](anas.md) | ANAS SpA — viabilità nazionale | ~7k | ✅ | ✅ | 🤖 |
| 102 | HV17 | [Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG](vigilanza-privata-federdat-gpg.md) | Vigilanza privata | ~45k | ⚠️ | ✅ | 🤖 |
| 103 | HV17 | [Vigilanza Privata e Servizi Fiduciari FEDERDAT — SF](vigilanza-privata-federdat-sf.md) | Servizi fiduciari | ~40k | ⚠️ | ✅ | 🤖 |

[^1]: Approximate estimates. Sources: CNEL, INPS, Ministero del Lavoro, CCNL renewal communications.
[^2]: Salary tables were extracted from official CCNL documents using AI-assisted tooling, without manual human review. Verify against the official source before use in production payroll systems.
[^3]: Compensation for Forze di Polizia ad ordinamento civile is set by Presidential Decree (DPR), not a CNEL-registered agreement. Applicable instrument: D.P.R. 24 marzo 2025, n. 53 (GU n. 91, 18 April 2025, SO).
