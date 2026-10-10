"""Rule ids and sources of the withholding on employment income, per tax year.

Art. 23 D.P.R. 600/1973 is in force until 31 December 2026 (Normattiva: "in
vigore dal 21-5-2022 al 31-12-2026").  From 1 January 2027 the testo unico
of D.Lgs. 33/2025 applies (art. 243 c. 1, as amended by D.L. 200/2025 art. 4
c. 4); its art. 33 carries the same rules with renumbered commi: art. 23 c. 1
is art. 33 c. 1, art. 23 c. 3 (conguaglio, shortfall and written deferral)
is art. 33 c. 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)

__all__ = ["WithholdingRule", "WithholdingTopic", "withholding_rule"]

#: First tax year of the testo unico of D.Lgs. 33/2025 (art. 243).
_TESTO_UNICO_FROM = 2027

_DPR_600 = SourceDocument(
    document_id="dpr-600-1973",
    title="D.P.R. 29 settembre 1973, n. 600",
    kind=SourceKind.DPR,
    url=(
        "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
        "decreto.del.presidente.della.repubblica:1973-09-29;600~art23"
        "!vig=2026-12-31"
    ),
)
_DLGS_33 = SourceDocument(
    document_id="dlgs-33-2025",
    title="D.Lgs. 24 marzo 2025, n. 33, testo unico versamenti e riscossione",
    kind=SourceKind.DLGS,
    url=(
        "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
        "decreto.legislativo:2025-03-24;33:1~art33"
    ),
)


class WithholdingTopic(StrEnum):
    """Comma of the withholding rule a decision applies."""

    #: Who withholds: the sostituti d'imposta.
    AGENTS = "agents"
    #: Conguaglio, what the pay cannot cover and its written deferral.
    CONGUAGLIO = "conguaglio"


#: Comma of art. 23 D.P.R. 600/1973 and of art. 33 D.Lgs. 33/2025 per topic.
_COMMA: dict[WithholdingTopic, tuple[int, int]] = {
    WithholdingTopic.AGENTS: (1, 1),
    WithholdingTopic.CONGUAGLIO: (3, 4),
}


@dataclass(frozen=True)
class WithholdingRule:
    """The withholding rule in force for one tax year.

    Attributes:
        rule: Rule id, e.g. ``"dpr600-1973-art23-c3"``.
        source: Document and section of the rule.
        citation: Short citation for messages, e.g.
            ``"art. 23 c. 3 DPR 600/1973"``.
    """

    rule: str
    source: SourceLocation
    citation: str


def withholding_rule(topic: WithholdingTopic, tax_year: int) -> WithholdingRule:
    """Return the withholding rule on ``topic`` in force for ``tax_year``.

    Returns:
        Art. 33 D.Lgs. 33/2025 from 2027, art. 23 D.P.R. 600/1973 before.
    """
    dpr_comma, dlgs_comma = _COMMA[topic]
    if tax_year >= _TESTO_UNICO_FROM:
        section = f"art. 33 c. {dlgs_comma}"
        return WithholdingRule(
            rule=f"dlgs33-2025-art33-c{dlgs_comma}",
            source=SourceLocation(source_document=_DLGS_33, section=section),
            citation=f"{section} D.Lgs. 33/2025",
        )
    section = f"art. 23 c. {dpr_comma}"
    return WithholdingRule(
        rule=f"dpr600-1973-art23-c{dpr_comma}",
        source=SourceLocation(source_document=_DPR_600, section=section),
        citation=f"{section} DPR 600/1973",
    )
