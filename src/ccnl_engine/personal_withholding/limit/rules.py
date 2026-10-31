"""Norms the limits of the personal withholdings apply, with their sources.

Each limit names the rule it applies and quotes it from the Normattiva page
of the article in force on 31 October 2026, or on 1 January 2027 for art.
171 D.Lgs. 33/2025, which replaces art. 72-ter DPR 602/1973 from that day
with the same words; the sha256 is of the page fetched.  See
:mod:`~ccnl_engine.personal_withholding.rules` for how they combine.
"""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.personal_withholding.inputs import PersonalWithholdingKind
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.provenance.statute.rules import WITHHOLDING_CODE_FROM

__all__ = [
    "ASSIGNMENTS",
    "ASSIGNMENT_LIMIT",
    "FIFTH_LIMIT",
    "INSTALLMENT_LIMITS",
    "LegalLimit",
    "half_rule",
    "tax_collection_limit",
]

_K = PersonalWithholdingKind
#: Kinds agreed with a lender rather than ordered by a judge.
ASSIGNMENTS = frozenset({_K.SALARY_ASSIGNMENT, _K.PAYMENT_DELEGATION})
_NORMATTIVA = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
_DPR_180 = "decreto.del.presidente.della.repubblica:1950-01-05;180:1~art"
_VIG = "!vig=2026-10-31"


@dataclass(frozen=True)
class LegalLimit:
    """The rule a deduction was limited by.

    Attributes:
        rule: Rule id recorded on the decision, e.g. ``"cpc-art545-c4"``.
        source: Document, section and quote of the rule.
    """

    rule: str
    source: SourceLocation


def _limit(rule: str, document: SourceDocument, section: str, quote: str) -> LegalLimit:
    return LegalLimit(
        rule, SourceLocation(source_document=document, section=section, quote=quote)
    )


def _dpr_180(article: str, sha256: str) -> SourceDocument:
    return SourceDocument(
        document_id=f"dpr-180-1950-art{article}",
        title=f"D.P.R. 5 gennaio 1950, n. 180, art. {article}",
        kind=SourceKind.DPR,
        url=f"{_NORMATTIVA}{_DPR_180}{article}{_VIG}",
        sha256=sha256,
    )


_CPC_545 = SourceDocument(
    document_id="cpc-art545",
    title="Codice di procedura civile (R.D. 28 ottobre 1940, n. 1443), art. 545",
    kind=SourceKind.LEGGE,
    url=f"{_NORMATTIVA}regio.decreto:1940-10-28;1443:1~art545{_VIG}",
    sha256="1fa0acce41c8fa68d80eba137bd4fcbe903016fa97ac4df183cc0ce55897ce66",
)
_DPR_602 = SourceDocument(
    document_id="dpr-602-1973-art72ter",
    title="D.P.R. 29 settembre 1973, n. 602, art. 72-ter",
    kind=SourceKind.DPR,
    url=(
        f"{_NORMATTIVA}decreto.del.presidente.della.repubblica:1973-09-29;602"
        f"~art72ter{_VIG}"
    ),
    sha256="efb4ae0078b496a61cc525fea9f9198b95ec73c7170e120c6171fc8d4bcba049",
)
_DLGS_33 = SourceDocument(
    document_id="dlgs-33-2025-art171",
    title="D.Lgs. 24 marzo 2025, n. 33, testo unico versamenti e riscossione",
    kind=SourceKind.DLGS,
    url=f"{_NORMATTIVA}decreto.legislativo:2025-03-24;33:1~art171!vig=2027-01-01",
    sha256="3763d29c2c51ac792ff47a166fd563044120a235eaadab16bfe4fd3634544093",
)
_DPR_180_68 = _dpr_180(
    "68", "70f44d3ee380d39ae8491d440e39647795142cce7f5905dc4759eee278fa0203"
)

#: Art. 545 c. 4 c.p.c.: a fifth for taxes and for any other credit.
FIFTH_LIMIT = _limit(
    "cpc-art545-c4",
    _CPC_545,
    "art. 545 c. 4",
    "Tali somme possono essere pignorate nella misura di un quinto per i "
    "tributi dovuti allo Stato, alle province e ai comuni, ed in eguale "
    "misura per ogni altro credito.",
)
#: Art. 5 DPR 180/1950: a salary assignment up to a fifth of the net pay.
ASSIGNMENT_LIMIT = _limit(
    "dpr180-1950-art5",
    _dpr_180("5", "461c2014ffdc7d93ddc0761877b9cd4b4964c256165ef252412a3c38a78a4919"),
    "art. 5 c. 1",
    "fino al quinto dell'ammontare di tali emolumenti valutato al netto di ritenute",
)
_ASSIGNMENT_AND_DELEGATION = _limit(
    "dpr180-1950-art70",
    _dpr_180("70", "de142ea046d558236c9525ce89761b62b410fab9af044ad5e3e384ad7680e32f"),
    "art. 70",
    "Nel caso di concorso di cessione e delegazione, non può superarsi il "
    "limite della metà dello stipendio o salario",
)
#: Rule of the stated monthly amount of the kinds that state one.
INSTALLMENT_LIMITS = {
    _K.MAINTENANCE: _limit(
        "cpc-art545-c3",
        _CPC_545,
        "art. 545 c. 3",
        "possono essere pignorate per crediti alimentari nella misura "
        "autorizzata dal presidente del tribunale o da un giudice da lui "
        "delegato",
    ),
    _K.PAYMENT_DELEGATION: _ASSIGNMENT_AND_DELEGATION,
}
_CONCURRENT_CAUSES = _limit(
    "cpc-art545-c5",
    _CPC_545,
    "art. 545 c. 5",
    "Il pignoramento per il simultaneo concorso delle cause indicate "
    "precedentemente non può estendersi oltre alla metà dell'ammontare delle "
    "somme predette.",
)
_GARNISHMENT_FIRST = _limit(
    "dpr180-1950-art68-c1",
    _DPR_180_68,
    "art. 68 c. 1",
    "la cessione, fermo restando il limite di cui al primo comma dell'art. 5, "
    "non può essere fatta se non limitatamente alla differenza tra i due "
    "quinti dello stipendio o salario valutati al netto delle ritenute e la "
    "quota colpita da sequestri o pignoramenti",
)
_ASSIGNMENT_FIRST = _limit(
    "dpr180-1950-art68-c2",
    _DPR_180_68,
    "art. 68 c. 2",
    "non si può sequestrare o pignorare se non la differenza fra la metà "
    "dello stipendio o salario valutati al netto di ritenute e la quota ceduta",
)
_DELEGATION_AND_GARNISHMENT = _limit(
    "dpr180-1950-art69",
    _dpr_180("69", "d238cd504a6f2b35902ab516ae514c6e2ae3aba6d357c03b685902c3c18d62a0"),
    "art. 69",
    "sono consentite soltanto sulla differenza fra la metà dello stipendio, "
    "salario o pensione valutati al netto di ritenute e le somme "
    "precedentemente vincolate",
)
_TAX_COLLECTION_72TER = _limit(
    "dpr602-1973-art72ter",
    _DPR_602,
    "art. 72-ter c. 1-2",
    "in misura pari ad un decimo per importi fino a 2.500 euro e in misura "
    "pari ad un settimo per importi superiori a 2.500 euro e non superiori a "
    "5.000 euro",
)
_TAX_COLLECTION_171 = _limit(
    "dlgs33-2025-art171",
    _DLGS_33,
    "art. 171 c. 1-2",
    "in misura pari a un decimo per importi fino a 2.500 euro e in misura "
    "pari a un settimo per importi superiori a 2.500 euro e non superiori a "
    "5.000 euro",
)


def tax_collection_limit(year: int) -> LegalLimit:
    """Return the rule of the agente della riscossione for a payment year.

    Returns:
        Art. 171 D.Lgs. 33/2025 from 2027, art. 72-ter DPR 602/1973 before
        (Normattiva: "Testo in vigore dal: 3-12-2016 al: 31-12-2026").
    """
    if year >= WITHHOLDING_CODE_FROM:
        return _TAX_COLLECTION_171
    return _TAX_COLLECTION_72TER


def half_rule(
    kind: PersonalWithholdingKind, earlier: frozenset[PersonalWithholdingKind]
) -> LegalLimit:
    """Return the rule of the combined limit ``kind`` meets after ``earlier``.

    Returns:
        For a salary assignment, art. 68 c. 1 DPR 180/1950 after a
        garnishment, art. 70 after a delegation; for a delegation, art. 69
        after a garnishment, art. 70 after an assignment; for a
        garnishment, art. 68 c. 2 after a salary assignment, art. 69 after a
        delegation, art. 545 c. 5 c.p.c. after garnishments only.
    """
    garnished = bool(earlier - ASSIGNMENTS)
    if kind is _K.SALARY_ASSIGNMENT:
        return _GARNISHMENT_FIRST if garnished else _ASSIGNMENT_AND_DELEGATION
    if kind is _K.PAYMENT_DELEGATION:
        return _DELEGATION_AND_GARNISHMENT if garnished else _ASSIGNMENT_AND_DELEGATION
    if _K.SALARY_ASSIGNMENT in earlier:
        return _ASSIGNMENT_FIRST
    if _K.PAYMENT_DELEGATION in earlier:
        return _DELEGATION_AND_GARNISHMENT
    return _CONCURRENT_CAUSES
