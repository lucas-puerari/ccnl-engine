<!-- auto-generated; run: uv run python scripts/documentation/review_plan/generate.py -->

# Review plan

The CCNLs of one tax sector share its INPS and tax rules, so the plan groups them by sector: the shared rules are verified once for the group, and the CCNL of the first review round anchors it. Before rules derived from the same source are promoted for the other CCNLs of a group, at least one more CCNL of the group is reviewed in full.

Groups are ordered by the workers they cover, then by their weak (`assumed` or `missing`) rules; the CCNLs within a group follow the same order. *Aggregator* marks a CCNL whose main source is a table service rather than a contracting party or an official body: its rules are the first to re-source. Workers is the estimate each CCNL file declares: the CCNLs of one comparto (such as the four Istruzione e Ricerca sections) repeat its figure, so a group total overstates the workers and serves only to rank the groups.

| Group | CCNLs | Workers | Weak | Derived | Verified | Aggregator | Anchor |
|---|---:|---:|---:|---:|---:|---:|---|
| pubblica-amministrazione | 14 | 7 548 000 | 14 | 208 | 186 | 0 | `funzioni-centrali-aran` |
| terziario | 43 | 4 977 055 | 170 | 1535 | 660 | 4 | `commercio-confcommercio`, `sanita-privata-aiop-aris` |
| industria | 48 | 4 946 900 | 216 | 2285 | 654 | 15 | `logistica-trasporto-confetra`, `metalmeccanico-federmeccanica` |
| lavoro-domestico | 3 | 1 800 000 | 0 | 3 | 56 | 0 | `lavoro-domestico-non-convivente` |
| artigianato | 8 | 1 244 505 | 37 | 305 | 95 | 2 | `metalmeccanico-artigianato` |
| agricoltura | 9 | 752 860 | 19 | 240 | 42 | 5 | `operai-agricoli-florovivaisti` |
| edilizia | 4 | 710 000 | 4 | 118 | 78 | 0 | `edilizia-ance` |
| credito | 3 | 348 000 | 3 | 39 | 78 | 0 | `bancari-abi` |

## pubblica-amministrazione

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`universita-aran`](../contracts/universita-aran.md) | 1 200 000 | exploratory | 5 | 4 | 20 | party or official | none | none |
| [`afam-aran`](../contracts/afam-aran.md) | 1 200 000 | exploratory | 2 | 13 | 24 | party or official | none | none |
| [`enti-ricerca-aran`](../contracts/enti-ricerca-aran.md) | 1 200 000 | exploratory | 1 | 4 | 32 | party or official | none | none |
| [`istruzione-ricerca-aran`](../contracts/istruzione-ricerca-aran.md) | 1 200 000 | exploratory | 1 | 41 | 48 | party or official | none | none |
| [`universita-tecnologi-aran`](../contracts/universita-tecnologi-aran.md) | 1 200 000 | exploratory | 1 | 4 | 2 | party or official | none | none |
| [`sanita-aran`](../contracts/sanita-aran.md) | 580 000 | reviewed | 0 | 5 | 16 | party or official | maintainer | 2027-01-31 |
| [`funzioni-locali-aran`](../contracts/funzioni-locali-aran.md) | 400 000 | reviewed | 0 | 9 | 18 | party or official | maintainer | 2027-01-31 |
| [`funzioni-centrali-aran`](../contracts/funzioni-centrali-aran.md) (anchor) | 250 000 | reviewed | 0 | 5 | 26 | party or official | maintainer | 2027-12-31 |
| [`forze-polizia-ordinamento-civile`](../contracts/forze-polizia-ordinamento-civile.md) | 130 000 | exploratory | 2 | 70 | 0 | party or official | none | none |
| [`dirigenza-sanitaria-medico-veterinaria-aran`](../contracts/dirigenza-sanitaria-medico-veterinaria-aran.md) | 100 000 | exploratory | 2 | 8 | 0 | party or official | none | none |
| [`dirigenza-sanitaria-area-sanita-aran`](../contracts/dirigenza-sanitaria-area-sanita-aran.md) | 37 000 | exploratory | 0 | 10 | 0 | party or official | none | none |
| [`dirigenza-funzioni-centrali-aran`](../contracts/dirigenza-funzioni-centrali-aran.md) | 30 000 | exploratory | 0 | 13 | 0 | party or official | none | none |
| [`dirigenza-funzioni-locali-aran`](../contracts/dirigenza-funzioni-locali-aran.md) | 13 000 | exploratory | 0 | 9 | 0 | party or official | none | none |
| [`dirigenza-istruzione-ricerca-aran`](../contracts/dirigenza-istruzione-ricerca-aran.md) | 8 000 | exploratory | 0 | 13 | 0 | party or official | none | none |

## terziario

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`commercio-confcommercio`](../contracts/commercio-confcommercio.md) (anchor) | 800 000 | reviewed | 0 | 0 | 69 | party or official | maintainer | 2027-03-31 |
| [`multiservizi-anip`](../contracts/multiservizi-anip.md) | 580 000 | exploratory | 0 | 93 | 57 | party or official | none | none |
| [`dmo-federdistribuzione`](../contracts/dmo-federdistribuzione.md) | 460 000 | production | 0 | 1 | 77 | party or official | maintainer | 2027-04-01 |
| [`cooperative-sociali`](../contracts/cooperative-sociali.md) | 380 000 | reviewed | 0 | 1 | 62 | party or official | maintainer | 2027-01-31 |
| [`pubblici-esercizi-fipe-angem`](../contracts/pubblici-esercizi-fipe-angem.md) | 350 000 | production | 0 | 2 | 61 | party or official | maintainer | 2027-06-01 |
| [`pubblici-esercizi-fipe-angem-ristorazione-collettiva`](../contracts/pubblici-esercizi-fipe-angem-ristorazione-collettiva.md) | 350 000 | production | 0 | 2 | 61 | party or official | maintainer | 2027-06-01 |
| [`studi-professionali-confprofessioni`](../contracts/studi-professionali-confprofessioni.md) | 350 000 | production | 0 | 0 | 46 | party or official | maintainer | 2027-04-30 |
| [`terziario-confesercenti`](../contracts/terziario-confesercenti.md) | 230 000 | production | 0 | 0 | 75 | party or official | maintainer | 2027-03-31 |
| [`turismo-federalberghi`](../contracts/turismo-federalberghi.md) | 220 000 | production | 0 | 1 | 71 | party or official | maintainer | 2027-04-30 |
| [`sanita-privata-aiop-aris`](../contracts/sanita-privata-aiop-aris.md) (anchor) | 150 000 | exploratory | 0 | 1 | 36 | party or official | maintainer | 2027-06-30 |
| [`uneba-uneba`](../contracts/uneba-uneba.md) | 130 000 | exploratory | 2 | 41 | 0 | party or official | none | none |
| [`autoferrotranvieri-internavigatori`](../contracts/autoferrotranvieri-internavigatori.md) | 120 000 | exploratory | 2 | 138 | 0 | party or official | none | none |
| [`istituzioni-servizi-socio-assistenziali-anaste`](../contracts/istituzioni-servizi-socio-assistenziali-anaste.md) | 120 000 | exploratory | 2 | 31 | 0 | party or official | none | none |
| [`vigilanza-privata-assiv`](../contracts/vigilanza-privata-assiv.md) | 85 000 | exploratory | 2 | 48 | 0 | party or official | none | none |
| [`distribuzione-cooperativa-ancc`](../contracts/distribuzione-cooperativa-ancc.md) | 63 000 | exploratory | 2 | 62 | 0 | aggregator | none | none |
| [`ortofrutticoli-agrumari`](../contracts/ortofrutticoli-agrumari.md) | 60 000 | exploratory | 9 | 0 | 45 | aggregator | none | none |
| [`farmacie-private-h121`](../contracts/farmacie-private-h121.md) | 60 000 | exploratory | 2 | 37 | 0 | party or official | none | none |
| [`scuole-private-agidae`](../contracts/scuole-private-agidae.md) | 50 000 | exploratory | 2 | 43 | 0 | party or official | none | none |
| [`vigilanza-privata-federdat-gpg`](../contracts/vigilanza-privata-federdat-gpg.md) | 45 000 | exploratory | 2 | 48 | 0 | party or official | none | none |
| [`autorimesse-ic35`](../contracts/autorimesse-ic35.md) | 41 000 | exploratory | 2 | 95 | 0 | party or official | none | none |
| [`vigilanza-privata-federdat-sf`](../contracts/vigilanza-privata-federdat-sf.md) | 40 000 | exploratory | 3 | 46 | 0 | party or official | none | none |
| [`portieri-fabbricati-confedilizia`](../contracts/portieri-fabbricati-confedilizia.md) | 40 000 | exploratory | 2 | 37 | 0 | party or official | none | none |
| [`industria-turistica-federturismo`](../contracts/industria-turistica-federturismo.md) | 40 000 | exploratory | 1 | 46 | 0 | aggregator | none | none |
| [`impianti-sportivi-sport`](../contracts/impianti-sportivi-sport.md) | 35 533 | exploratory | 2 | 32 | 0 | party or official | none | none |
| [`scuole-materne-fism`](../contracts/scuole-materne-fism.md) | 30 000 | exploratory | 2 | 47 | 0 | party or official | none | none |
| [`agenzie-viaggio-fiavet`](../contracts/agenzie-viaggio-fiavet.md) | 25 000 | exploratory | 2 | 68 | 0 | party or official | none | none |
| [`scuole-private-laiche-aninsei`](../contracts/scuole-private-laiche-aninsei.md) | 25 000 | exploratory | 2 | 43 | 0 | party or official | none | none |
| [`ced-assoced`](../contracts/ced-assoced.md) | 22 000 | exploratory | 2 | 44 | 0 | party or official | none | none |
| [`formazione-professionale`](../contracts/formazione-professionale.md) | 19 800 | exploratory | 2 | 33 | 0 | party or official | none | none |
| [`rsa-aiop`](../contracts/rsa-aiop.md) | 17 000 | exploratory | 2 | 31 | 0 | party or official | none | none |
| [`ooss-unsic-confsal`](../contracts/ooss-unsic-confsal.md) | 7 000 | exploratory | 2 | 19 | 0 | party or official | none | none |
| [`esercizi-cinematografici-anec`](../contracts/esercizi-cinematografici-anec.md) | 6 000 | exploratory | 2 | 54 | 0 | party or official | none | none |
| [`farmacie-municipalizzate-assofarm`](../contracts/farmacie-municipalizzate-assofarm.md) | 6 000 | exploratory | 2 | 45 | 0 | party or official | none | none |
| [`federcasa`](../contracts/federcasa.md) | 6 000 | exploratory | 2 | 23 | 0 | party or official | none | none |
| [`noleggio-autobus-conducente-anav`](../contracts/noleggio-autobus-conducente-anav.md) | 5 422 | exploratory | 71 | 0 | 0 | party or official | none | none |
| [`agenzie-marittime-i481`](../contracts/agenzie-marittime-i481.md) | 5 000 | exploratory | 2 | 36 | 0 | party or official | none | none |
| [`fiori-recisi-ancef`](../contracts/fiori-recisi-ancef.md) | 1 300 | exploratory | 2 | 38 | 0 | party or official | none | none |
| [`recapito-corrispondenza-fise`](../contracts/recapito-corrispondenza-fise.md) | 1 000 | exploratory | 2 | 47 | 0 | party or official | none | none |
| [`servizi-postali-appalto-fise`](../contracts/servizi-postali-appalto-fise.md) | 1 000 | exploratory | 2 | 49 | 0 | party or official | none | none |
| [`agenti-immobiliari-fiaip`](../contracts/agenti-immobiliari-fiaip.md) | none | exploratory | 31 | 0 | 0 | party or official | none | none |
| [`autoscuole-unasca`](../contracts/autoscuole-unasca.md) | none | exploratory | 2 | 32 | 0 | party or official | none | none |
| [`aziende-termali-federterme`](../contracts/aziende-termali-federterme.md) | none | exploratory | 2 | 64 | 0 | party or official | none | none |
| [`turismo-confesercenti`](../contracts/turismo-confesercenti.md) | none | exploratory | 1 | 57 | 0 | aggregator | none | none |

## industria

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`metalmeccanico-federmeccanica`](../contracts/metalmeccanico-federmeccanica.md) (anchor) | 1 700 000 | production | 0 | 0 | 86 | party or official | maintainer | 2027-06-01 |
| [`logistica-trasporto-confetra`](../contracts/logistica-trasporto-confetra.md) (anchor) | 430 000 | reviewed | 0 | 3 | 63 | party or official | maintainer | 2027-06-01 |
| [`logistica-trasporto-confetra-viaggiante`](../contracts/logistica-trasporto-confetra-viaggiante.md) | 430 000 | reviewed | 0 | 30 | 53 | party or official | maintainer | 2027-06-01 |
| [`metalmeccanico-confapi`](../contracts/metalmeccanico-confapi.md) | 350 000 | production | 0 | 7 | 58 | party or official | maintainer | 2027-05-01 |
| [`chimica-farmaceutica-federchimica`](../contracts/chimica-farmaceutica-federchimica.md) | 210 000 | production | 0 | 5 | 111 | party or official | maintainer | 2027-04-30 |
| [`tessile-smi`](../contracts/tessile-smi.md) | 160 000 | exploratory | 2 | 47 | 0 | party or official | none | none |
| [`alimentari-federalimentare`](../contracts/alimentari-federalimentare.md) | 145 000 | production | 0 | 0 | 75 | party or official | maintainer | 2027-04-30 |
| [`poste-italiane-k700`](../contracts/poste-italiane-k700.md) | 117 000 | exploratory | 2 | 53 | 0 | party or official | none | none |
| [`telecomunicazioni-asstel`](../contracts/telecomunicazioni-asstel.md) | 110 000 | exploratory | 2 | 45 | 0 | party or official | none | none |
| [`metalmeccanico-confimi-pmi`](../contracts/metalmeccanico-confimi-pmi.md) | 100 000 | exploratory | 1 | 44 | 0 | aggregator | none | none |
| [`gomma-plastica-federazione-gomma-plastica`](../contracts/gomma-plastica-federazione-gomma-plastica.md) | 90 000 | exploratory | 2 | 77 | 0 | aggregator | none | none |
| [`legno-arredamento-federlegno`](../contracts/legno-arredamento-federlegno.md) | 90 000 | exploratory | 2 | 88 | 0 | aggregator | none | none |
| [`calzaturiero-assocalzaturifici`](../contracts/calzaturiero-assocalzaturifici.md) | 75 000 | exploratory | 2 | 37 | 0 | aggregator | none | none |
| [`trasporto-ferroviario-agens`](../contracts/trasporto-ferroviario-agens.md) | 75 000 | exploratory | 2 | 55 | 0 | aggregator | none | none |
| [`grafica-editoria-aieg`](../contracts/grafica-editoria-aieg.md) | 70 000 | exploratory | 2 | 71 | 0 | aggregator | none | none |
| [`gas-acqua-utilitalia`](../contracts/gas-acqua-utilitalia.md) | 65 000 | exploratory | 2 | 62 | 0 | party or official | none | none |
| [`igiene-ambientale-utilitalia`](../contracts/igiene-ambientale-utilitalia.md) | 65 000 | exploratory | 2 | 143 | 0 | aggregator | none | none |
| [`elettrico-elettricita-futura`](../contracts/elettrico-elettricita-futura.md) | 60 000 | exploratory | 2 | 77 | 0 | aggregator | none | none |
| [`chimica-affini-pmi-unionchimica`](../contracts/chimica-affini-pmi-unionchimica.md) | 56 000 | exploratory | 2 | 21 | 0 | aggregator | none | none |
| [`tessile-pmi-uniontessile`](../contracts/tessile-pmi-uniontessile.md) | 48 000 | exploratory | 44 | 0 | 0 | aggregator | none | none |
| [`trasporto-aereo-assaeroporti`](../contracts/trasporto-aereo-assaeroporti.md) | 40 000 | exploratory | 2 | 72 | 0 | party or official | none | none |
| [`energia-petrolio-confindustria`](../contracts/energia-petrolio-confindustria.md) | 38 000 | exploratory | 2 | 170 | 0 | party or official | none | none |
| [`alimentari-pmi-unionalimentari`](../contracts/alimentari-pmi-unionalimentari.md) | 35 000 | exploratory | 2 | 44 | 0 | party or official | none | none |
| [`carta-cartone-assocarta`](../contracts/carta-cartone-assocarta.md) | 35 000 | exploratory | 2 | 74 | 0 | aggregator | none | none |
| [`vetro-meccanizzato-assovetro`](../contracts/vetro-meccanizzato-assovetro.md) | 28 000 | exploratory | 36 | 0 | 0 | aggregator | none | none |
| [`metalmeccanica-cooperative`](../contracts/metalmeccanica-cooperative.md) | 28 000 | exploratory | 2 | 45 | 0 | party or official | none | none |
| [`cemento-calce-gesso-industria`](../contracts/cemento-calce-gesso-industria.md) | 25 000 | exploratory | 2 | 80 | 0 | party or official | none | none |
| [`ceramica-industria-confindustria`](../contracts/ceramica-industria-confindustria.md) | 23 000 | exploratory | 2 | 60 | 0 | party or official | none | none |
| [`concia-unic`](../contracts/concia-unic.md) | 22 600 | reviewed | 0 | 1 | 57 | party or official | maintainer | 2027-01-31 |
| [`informatica-pmi-unimatica`](../contracts/informatica-pmi-unimatica.md) | 20 000 | exploratory | 2 | 40 | 0 | party or official | none | none |
| [`occhiali-occhialeria-industria`](../contracts/occhiali-occhialeria-industria.md) | 20 000 | exploratory | 2 | 88 | 0 | party or official | none | none |
| [`panificazione-assipan`](../contracts/panificazione-assipan.md) | 20 000 | exploratory | 2 | 48 | 0 | party or official | none | none |
| [`lapidei-industria`](../contracts/lapidei-industria.md) | 18 000 | exploratory | 2 | 79 | 0 | aggregator | none | none |
| [`orafi-argentieri-industria-federorafi`](../contracts/orafi-argentieri-industria-federorafi.md) | 18 000 | exploratory | 2 | 40 | 0 | party or official | none | none |
| [`laterizi-industria-f021`](../contracts/laterizi-industria-f021.md) | 17 000 | exploratory | 2 | 98 | 0 | party or official | none | none |
| [`lavanderie-industriali-assosistema`](../contracts/lavanderie-industriali-assosistema.md) | 17 000 | exploratory | 2 | 37 | 0 | party or official | none | none |
| [`pelli-cuoio-industria-assopellettieri`](../contracts/pelli-cuoio-industria-assopellettieri.md) | 17 000 | exploratory | 2 | 35 | 0 | party or official | none | none |
| [`alimentaristi-cooperative-e016`](../contracts/alimentaristi-cooperative-e016.md) | 15 000 | exploratory | 2 | 70 | 0 | aggregator | none | none |
| [`autostrade-trafori`](../contracts/autostrade-trafori.md) | 15 000 | exploratory | 2 | 140 | 0 | party or official | none | none |
| [`funivie-anef`](../contracts/funivie-anef.md) | 15 000 | exploratory | 2 | 47 | 0 | party or official | none | none |
| [`marittimi-industria-armatoriale`](../contracts/marittimi-industria-armatoriale.md) | 15 000 | exploratory | 2 | 40 | 0 | party or official | none | none |
| [`anas`](../contracts/anas.md) | 7 000 | exploratory | 2 | 42 | 0 | party or official | none | none |
| [`materiali-costruzione-lapidei-confapi`](../contracts/materiali-costruzione-lapidei-confapi.md) | 5 000 | exploratory | 22 | 8 | 40 | party or official | none | none |
| [`attivita-minerarie-assorisorse`](../contracts/attivita-minerarie-assorisorse.md) | 3 000 | exploratory | 3 | 0 | 36 | party or official | none | none |
| [`cinema-audiovisivi-industria`](../contracts/cinema-audiovisivi-industria.md) | 2 300 | exploratory | 2 | 62 | 0 | aggregator | none | none |
| [`tabacco-apti`](../contracts/tabacco-apti.md) | 2 000 | exploratory | 23 | 0 | 36 | party or official | none | none |
| [`radiotelevisive-televisivo`](../contracts/radiotelevisive-televisivo.md) | none | exploratory | 12 | 0 | 27 | party or official | none | none |
| [`radiotelevisive-radiofonico`](../contracts/radiotelevisive-radiofonico.md) | none | exploratory | 9 | 0 | 12 | party or official | none | none |

## lavoro-domestico

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`lavoro-domestico-convivente`](../contracts/lavoro-domestico-convivente.md) | 900 000 | reviewed | 0 | 1 | 26 | party or official | maintainer | 2027-01-31 |
| [`lavoro-domestico-non-convivente`](../contracts/lavoro-domestico-non-convivente.md) (anchor) | 900 000 | reviewed | 0 | 0 | 17 | party or official | maintainer | 2027-01-31 |
| [`lavoro-domestico-convivente-orario-ridotto`](../contracts/lavoro-domestico-convivente-orario-ridotto.md) | none | reviewed | 0 | 2 | 13 | party or official | maintainer | 2027-01-31 |

## artigianato

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`edilizia-artigianato-cna`](../contracts/edilizia-artigianato-cna.md) | 350 000 | exploratory | 1 | 72 | 0 | party or official | none | none |
| [`metalmeccanico-artigianato`](../contracts/metalmeccanico-artigianato.md) (anchor) | 350 000 | exploratory | 0 | 43 | 38 | party or official | maintainer | 2027-01-31 |
| [`tessile-moda-artigianato-confartigianato`](../contracts/tessile-moda-artigianato-confartigianato.md) | 120 000 | exploratory | 1 | 36 | 0 | aggregator | none | none |
| [`legno-lapidei-artigianato-confartigianato`](../contracts/legno-lapidei-artigianato-confartigianato.md) | 95 000 | exploratory | 2 | 38 | 0 | aggregator | none | none |
| [`acconciatura-estetica-confartigianato`](../contracts/acconciatura-estetica-confartigianato.md) | 95 000 | exploratory | 1 | 29 | 0 | party or official | none | none |
| [`panificazione-artigianato-confartigianato`](../contracts/panificazione-artigianato-confartigianato.md) | 90 000 | exploratory | 0 | 47 | 1 | party or official | maintainer | 2027-01-31 |
| [`pulizia-artigianato-confartigianato`](../contracts/pulizia-artigianato-confartigianato.md) | 84 505 | exploratory | 31 | 0 | 56 | party or official | none | none |
| [`comunicazione-artigianato-confartigianato`](../contracts/comunicazione-artigianato-confartigianato.md) | 60 000 | exploratory | 1 | 40 | 0 | party or official | none | none |

## agricoltura

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`operai-agricoli-florovivaisti`](../contracts/operai-agricoli-florovivaisti.md) (anchor) | 600 000 | exploratory | 2 | 9 | 10 | aggregator | maintainer | none |
| [`impiegati-tecnici-agricoli`](../contracts/impiegati-tecnici-agricoli.md) | 80 000 | exploratory | 2 | 15 | 0 | aggregator | none | none |
| [`cooperative-consorzi-agricoli`](../contracts/cooperative-consorzi-agricoli.md) | 60 000 | exploratory | 1 | 9 | 32 | party or official | maintainer | 2027-02-01 |
| [`consorzi-di-bonifica-snebi`](../contracts/consorzi-di-bonifica-snebi.md) | 4 000 | exploratory | 2 | 56 | 0 | party or official | none | none |
| [`contoterzismo-caiagromec`](../contracts/contoterzismo-caiagromec.md) | 4 000 | exploratory | 2 | 48 | 0 | party or official | none | none |
| [`consorzi-agrari-assocap`](../contracts/consorzi-agrari-assocap.md) | 2 000 | exploratory | 2 | 36 | 0 | aggregator | none | none |
| [`organizzazioni-allevatori-aia`](../contracts/organizzazioni-allevatori-aia.md) | 2 000 | exploratory | 2 | 20 | 0 | aggregator | none | none |
| [`sistemazioni-idraulico-forestali-impiegati`](../contracts/sistemazioni-idraulico-forestali-impiegati.md) | 430 | exploratory | 3 | 27 | 0 | aggregator | none | none |
| [`sistemazioni-idraulico-forestali-operai`](../contracts/sistemazioni-idraulico-forestali-operai.md) | 430 | exploratory | 3 | 20 | 0 | party or official | none | none |

## edilizia

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`edilizia-ance`](../contracts/edilizia-ance.md) (anchor) | 550 000 | production | 0 | 8 | 32 | party or official | maintainer | 2027-02-28 |
| [`edilizia-cooperative-ancpl`](../contracts/edilizia-cooperative-ancpl.md) | 90 000 | exploratory | 2 | 57 | 0 | party or official | none | none |
| [`edilizia-pmi-confapi-aniem`](../contracts/edilizia-pmi-confapi-aniem.md) | 70 000 | exploratory | 2 | 30 | 14 | party or official | maintainer | 2027-03-01 |
| [`edilizia-ance-impiegati`](../contracts/edilizia-ance-impiegati.md) | none | production | 0 | 23 | 32 | party or official | maintainer | 2027-02-28 |

## credito

| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Owner | Next review |
|---|---:|---|---:|---:|---:|---|---|---|
| [`bancari-abi`](../contracts/bancari-abi.md) (anchor) | 270 000 | exploratory | 0 | 2 | 43 | party or official | maintainer | 2027-03-31 |
| [`assicurazioni-ania`](../contracts/assicurazioni-ania.md) | 45 000 | exploratory | 2 | 30 | 0 | party or official | none | none |
| [`bcc-credito-cooperativo`](../contracts/bcc-credito-cooperativo.md) | 33 000 | exploratory | 1 | 7 | 35 | party or official | maintainer | 2027-06-30 |
