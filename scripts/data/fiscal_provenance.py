"""Provenance records of the fiscal data blocks, keyed by file and block.

Every citation is copied from the notes or the ruleset ``source`` of the
file itself; where the data records none, from the docstring of the rule
model that consumes the block, and the record says so in
``transformation``.  No record is ``verified``: none of the files names a
reviewer and a date.  Validity is the one of the file's ruleset, so the
records carry no extraction trace.

The block key ``*`` is the file-level record of a surtax table.
"""

from __future__ import annotations

from typing import Any, Final

_FROM_MODEL = (
    "Citation taken from the docstring of the rule model that consumes the "
    "block; the data file records none."
)
_SHARED = (
    "Citation taken from the other 2026 sector files: the values are "
    "statutory and identical across sectors."
)


def _doc(
    document_id: str, title: str, kind: str, url: str | None = None
) -> dict[str, Any]:
    doc: dict[str, Any] = {"document_id": document_id, "title": title, "kind": kind}
    if url is not None:
        doc["url"] = url
    return doc


L_199_2025: Final = _doc(
    "l-199-2025",
    "L. 199/2025, legge di bilancio 2026",
    "legge",
    "https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art."
    "codiceRedazionale=26A00149&art.dataPubblicazioneGazzetta=2026-01-21&art."
    "flagTipoArticolo=0&art.idArticolo=1&art.idGruppo=1&art.idSottoArticolo=1&"
    "art.idSottoArticolo1=10&art.progressivo=1&art.versione=1",
)
L_207_2024: Final = _doc("l-207-2024", "L. 207/2024, legge di bilancio 2025", "legge")
L_92_2012: Final = _doc("l-92-2012", "L. 92/2012", "legge")
L_296_2006: Final = _doc("l-296-2006", "L. 296/2006, legge finanziaria 2007", "legge")
L_208_2015: Final = _doc("l-208-2015", "L. 208/2015, legge di stabilità 2016", "legge")
TUIR: Final = _doc("dpr-917-1986", "D.P.R. 22 dicembre 1986 n. 917 (TUIR)", "dpr")
DL_3_2020: Final = _doc("dl-3-2020", "D.L. 3/2020", "dl")
CODICE_CIVILE: Final = _doc("codice-civile", "Codice civile", "legge")
INPS_6_2026: Final = _doc(
    "inps-circolare-6-2026", "INPS Circolare n. 6 del 30 gennaio 2026", "inps_circolare"
)
INPS_9_2026: Final = _doc(
    "inps-circolare-9-2026",
    "INPS Circolare n. 9 del 3 febbraio 2026, contributi lavoro domestico 2026",
    "inps_circolare",
)
ADE_4E_2025: Final = _doc(
    "ade-circolare-4e-2025",
    "Agenzia delle Entrate, circolare 4/E/2025",
    "amministrazione",
)
MEF_COMUNALE: Final = _doc(
    "mef-addizionale-comunale-elenco-2026",
    "MEF, Dipartimento delle Finanze: addizionale comunale all'IRPEF, elenco "
    "generale 2026 (CSV, retrieved 2026-09-27)",
    "amministrazione",
    "https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/"
    "fiscalitalocale/addirpef_newDF/download/download.php?anno=2026",
)
MEF_REGIONALE: Final = _doc(
    "mef-addregirpef-2026",
    "MEF, Dipartimento delle Finanze: addizionale regionale all'IRPEF, "
    "aliquote applicabili 2026",
    "amministrazione",
    "https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/"
    "fiscalitalocale/addregirpef/sceltaregione.htm",
)
_KITECH_URL = "https://www.kitech.it/Contributi-previdenziali.aspx?p="


def _kitech(page: str, title: str) -> dict[str, Any]:
    return _doc(
        f"kitech-contributi-{page}",
        f"kitech.it, {title}",
        "rivista",
        _KITECH_URL + page,
    )


def _record(
    status: str,
    document: dict[str, Any] | None = None,
    section: str | None = None,
    *,
    note: str | None = None,
    transformation: str | None = None,
) -> dict[str, Any]:
    location = (
        None if document is None else {"source_document": document, "section": section}
    )
    record: dict[str, Any] = {"status": status, "location": location}
    if transformation is not None:
        record["transformation"] = transformation
    if note is not None:
        record["note"] = note
    return record


def _derived(document: dict[str, Any], section: str, **kwargs: str) -> dict[str, Any]:
    return _record("derived", document, section, **kwargs)


_IRPEF = _derived(L_199_2025, "art. 1 c. 3")
_WORK_DEDUCTION = _derived(TUIR, "art. 13 c. 1")
_STERILIZZAZIONE = _derived(L_199_2025, "art. 1 c. 4")
_FIXED_TERM = _derived(L_92_2012, "art. 2 c. 28")
_TFR = _derived(CODICE_CIVILE, "art. 2120", transformation=_FROM_MODEL)
_TRATTAMENTO = _derived(
    DL_3_2020, "art. 1 (as amended by L. 207/2024)", transformation=_FROM_MODEL
)
_ULTERIORE = _derived(L_207_2024, "art. 1 c. 6", transformation=_FROM_MODEL)
_SOMMA_ESENTE = _record(
    "assumed",
    L_207_2024,
    "art. 1 c. 4",
    note=(
        "Band cut points 8 500 EUR and 15 000 EUR are reconstructions from "
        "worked examples, not verified against the primary source; rates "
        "7.1%/5.3%/4.8% and the 20 000 EUR ceiling are from AdE guidance."
    ),
)
_APPRENTICE = _derived(
    L_296_2006,
    "art. 1 c. 773; L. 92/2012 art. 2 cc. 36-37",
    transformation="Employer rate 10% + NASpI 1.31% + 0.30% = 11.61%.",
)


def _tax(**overrides: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the records of a sector tax file.

    Returns:
        The statutory records shared by every sector, with ``overrides``.
    """
    return {
        "irpef_brackets": _IRPEF,
        "work_deduction": _WORK_DEDUCTION,
        "sterilizzazione_detrazioni": _STERILIZZAZIONE,
        "fixed_term_additional_rate": _FIXED_TERM,
        "tfr": _TFR,
        "trattamento_integrativo": _TRATTAMENTO,
        "ulteriore_detrazione": _ULTERIORE,
        "somma_esente": _SOMMA_ESENTE,
    } | overrides


_WORK_DEDUCTION_216 = _derived(
    TUIR,
    "art. 13 c. 1",
    note="Statutory piecewise schedule per D.Lgs. 216/2023 and L. 207/2024.",
)

FISCAL_RECORDS: Final[dict[str, dict[str, dict[str, Any]]]] = {
    "tax/data/2026-agricoltura.json": _tax(),
    "tax/data/2026-artigianato.json": _tax(),
    "tax/data/2026-credito.json": _tax(work_deduction=_WORK_DEDUCTION_216),
    "tax/data/2026-edilizia.json": _tax(),
    "tax/data/2026-industria.json": _tax(),
    "tax/data/2026-lavoro-domestico.json": _tax(
        irpef_brackets=_derived(L_199_2025, "art. 1 c. 3", transformation=_SHARED),
        work_deduction=_derived(TUIR, "art. 13 c. 1", transformation=_SHARED),
    ),
    "tax/data/2026-pubblica-amministrazione.json": _tax(
        work_deduction=_WORK_DEDUCTION_216,
        fixed_term_additional_rate=_record(
            "assumed",
            note=(
                "Rate 0: the file cites nexumstp.it for the exclusion of public "
                "administrations from the NASpI addizionale; no clause located."
            ),
        ),
    ),
    "tax/data/2026-terziario.json": _tax(
        work_deduction=_derived(ADE_4E_2025, "p. 6"),
    ),
    "inps/data/2026-agricoltura.json": {
        "inps": _derived(
            _doc(
                "ciatreviso-contributi-2026",
                "CIA Treviso, contributi INPS e INAIL 2026 agricoli",
                "associazione",
                "https://ciatreviso.it/contributi-inps-inail-2026-agricoli-"
                "aliquote-e-le-scadenze-per-operai-otd-e-oti/",
            ),
            "OTI rates 2026",
            note="Employee 8.84%, employer 21.66%; IVS ceiling from INPS Circ. 6/2026.",
        ),
        "apprentice": _APPRENTICE,
    },
    "inps/data/2026-artigianato.json": {
        "inps": _record(
            "assumed",
            _kitech("1_1", "contributi previdenziali artigianato 2026"),
            "non-construction crafts sector 2026",
            note=(
                "Rate 26.93% (operai) and 24.71% (impiegati, quadri) from an "
                "aggregator; the INPS circular was not retrieved and the "
                "component breakdown does not reconcile."
            ),
        ),
        "apprentice": _APPRENTICE,
    },
    "inps/data/2026-credito.json": {
        "inps": _derived(
            _kitech("9_165", "contributi previdenziali credito 2026"),
            "Table 6.1",
            note=(
                "Fondo di solidarietà del credito presumed aggregated into the "
                "26.76% and 9.19% totals."
            ),
        ),
        "apprentice": _APPRENTICE,
    },
    "inps/data/2026-edilizia.json": {
        "inps": _record(
            "assumed",
            _kitech("5_152", "contributi previdenziali edilizia"),
            "1998 rate structure",
            note="Proxy values, estimated; not checked against the 2026 INPS circular.",
        ),
        "apprentice": _APPRENTICE,
    },
    "inps/data/2026-industria.json": {
        "inps": _derived(
            INPS_6_2026,
            "IVS rate and contribution ceiling 2026",
            transformation=(
                "Employer tiers are the sum of IVS, NASpI, CUAF, CIGO and FIS or "
                "CIGS listed in the file notes."
            ),
            note=(
                "CIGO, CIGS and the employee CIGS share per D.Lgs. 148/2015 artt. "
                "5 and 23, Circ. INPS 1/2026 and 5/2025."
            ),
        ),
        "apprentice": _APPRENTICE,
    },
    "inps/data/2026-lavoro-domestico.json": {
        "domestic_contributions": _derived(INPS_9_2026, "contribution table 2026"),
    },
    "inps/data/2026-pubblica-amministrazione.json": {
        "inps": _derived(
            _kitech("17_210", "contributi previdenziali dipendenti pubblici"),
            "CTPS",
            note="Employee 8.80%, employer 24.20%, corroborated by INPS sources.",
        ),
        "apprentice": _record(
            "assumed",
            note=(
                "Schema-required placeholder: apprenticeship does not apply to "
                "PA contracts."
            ),
        ),
    },
    "inps/data/2026-terziario.json": {
        "inps": _derived(
            _kitech("4_138", "contributi previdenziali terziario 2026"),
            "Table 7.1",
            note="Pages 4_136 and 4_134 for firms above 50 employees.",
        ),
        "apprentice": _APPRENTICE,
    },
    "surtax/data/regionale-2026.json": {
        "*": _derived(
            MEF_REGIONALE,
            "one page per region, anno 2026",
            note=(
                "Retrieved on 2026-09-27; every row carries the URL of its page. "
                "Not checked by a named reviewer."
            ),
        ),
    },
    "surtax/data/comunale-2026.json": {
        "*": _derived(
            MEF_COMUNALE,
            "elenco generale 2026",
            note=(
                "Rows without a 2026 delibera carry their own assumed record and "
                "the 2025 rates."
            ),
        ),
    },
    "tax/data/family-deductions-2026.json": {
        "spouse": _derived(TUIR, "art. 12 c. 1 lett. a; c. 4"),
        "spouse_increases": _derived(TUIR, "art. 12 c. 1 lett. b"),
        "children": _derived(TUIR, "art. 12 c. 1 lett. c"),
        "other_dependents": _derived(TUIR, "art. 12 c. 1 lett. d"),
    },
    "tax/data/variable-pay-rules.json": {
        "fringe_benefit": _derived(
            TUIR, "art. 51 c. 3", note="Thresholds per L. 207/2024 art. 1 c. 390."
        ),
        "pdr": _derived(
            L_208_2015,
            "art. 1 cc. 182-190",
            note=(
                "Substitute rate 1% within 5,000 EUR for 2026 per L. 199/2025 "
                "art. 1 c. 9."
            ),
        ),
        "rinnovo": {"status": "derived"},
        "notte_festivi_turni": {"status": "derived"},
    },
}
