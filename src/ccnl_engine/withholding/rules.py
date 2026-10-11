"""Withholding rule ids per tax year and the IRPEF withheld on one run.

Art. 23 c. 2 DPR 600/1973 (Normattiva, text in force from 21 May 2022 to
31 December 2026) determines the withholding of each payment:

- lett. a) on the pay "corrisposti in ciascun periodo di paga, con le
  aliquote dell'imposta sul reddito delle persone fisiche, ragguagliando al
  periodo di paga i corrispondenti scaglioni annui di reddito, ed effettuando
  le detrazioni previste negli articoli 12 e 13 del citato testo unico,
  rapportate al periodo stesso";
- lett. b) "sulle mensilità aggiuntive e sui compensi della stessa natura,
  con le aliquote dell'imposta sul reddito delle persone fisiche,
  ragguagliando a mese i corrispondenti scaglioni annui di reddito", with no
  deduction.

AdE circ. 15/E/2007 par. 2.1 sets the reddito complessivo the deductions
are measured on: without other indication of the worker, "quello di lavoro
dipendente o assimilato o equiparato che nel corso dell'anno corrisponde",
the projected annual income.  Par. 2.4 counts among the compensi of lett. b)
the "gratifiche annuali di bilancio, i cosiddetti premi trimestrali,
semestrali e annuali", taxed apart from the pay of the period ("trattamento
autonomo", par. 2.1).

The deductions of the period are:

- art. 13 TUIR, the annual amount "rapportata al periodo di lavoro
  nell'anno" times the days of the pay period over the days of employment in
  the year, so the periods of the year add up to the annual amount, its
  minimum included (circ. 15/E/2007 par. 2.3: the minimum "deve quindi
  essere applicata per l'intero ammontare previsto e ragguagliata al periodo
  di paga"; par. 1.5.1: the days are those of the pay, the year of 365);
- art. 12 TUIR, a twelfth of the annual amount of each dependent in a month
  its conditions hold (c. 3: "rapportate a mese e competono dal mese in cui
  si sono verificate");
- the ulteriore detrazione of L. 207/2024 art. 1 c. 6, "rapportata al
  periodo di lavoro", recognized "all'atto dell'erogazione delle
  retribuzioni" (c. 7): the same day share as art. 13, on the pay of lett.
  a) only, since lett. b) allows no deduction.

A deduction above the tax of the period is lost to the period; the
conguaglio (art. 23 c. 3) settles the year on the annual figures.

Art. 23 D.P.R. 600/1973 is in force until 31 December 2026 (Normattiva: "in
vigore dal 21-5-2022 al 31-12-2026").  From 1 January 2027 the testo unico
of D.Lgs. 33/2025 applies (art. 243 c. 1, as amended by D.L. 200/2025 art. 4
c. 4); its art. 33 carries the same rules with renumbered commi: art. 23 c. 1
is art. 33 c. 1, art. 23 c. 3 (conguaglio, shortfall and written deferral)
is art. 33 c. 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.irpef.rules import period_irpef_gross
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)

if TYPE_CHECKING:
    from ccnl_engine.irpef.net.rules import NetIrpef
    from ccnl_engine.knowledge.sector.models import YearRules


__all__ = [
    "NO_PAY",
    "PayPeriod",
    "PeriodTax",
    "WithholdingRule",
    "WithholdingTopic",
    "period_tax",
    "withholding_rule",
]


_ZERO = Decimal(0)


@dataclass(frozen=True, slots=True)
class PayPeriod:
    """Pay of one run as art. 23 c. 2 DPR 600/1973 withholds it.

    Attributes:
        regular_taxable: Taxable of the pay of the period, lett. a).
        separate_taxable: Taxable of the mensilità aggiuntive and of the
            compensi of the same nature the run pays, lett. b).
        day_share: Share of the annual art. 13 deduction and ulteriore
            detrazione the period takes: days of the pay period over the days
            of employment in the year; zero for a run that takes no
            deduction.
        family: Art. 12 TUIR deductions of the month of the period.
    """

    regular_taxable: Decimal = _ZERO
    separate_taxable: Decimal = _ZERO
    day_share: Decimal = _ZERO
    family: Decimal = _ZERO

    @property
    def taxable(self) -> Decimal:
        """Employment income the run pays, lett. a) and b) together."""
        return self.regular_taxable + self.separate_taxable


#: A run that pays nothing: before the conguaglio it withholds nothing.
NO_PAY = PayPeriod()


@dataclass(frozen=True, slots=True)
class PeriodTax:
    """IRPEF of the period with and without the ulteriore detrazione.

    Attributes:
        withheld: IRPEF of the period.
        without_ulteriore: IRPEF of the period had the ulteriore detrazione
            not been recognized; the difference is what the run recognizes.
    """

    withheld: Decimal
    without_ulteriore: Decimal


def period_tax(period: PayPeriod, annual: NetIrpef, rules: YearRules) -> PeriodTax:
    """Return the IRPEF of the pay period under art. 23 c. 2 lett. a) and b).

    Args:
        period: Pay of the run.
        annual: Net IRPEF of the projected year, whose art. 13 deduction
            and ulteriore detrazione the period takes its share of.
        rules: Year rules with the annual brackets.

    Returns:
        The tax of lett. a), net of the deductions of the period and at
        least zero, plus the tax of lett. b); with and without the
        ulteriore detrazione.
    """
    regular = period_irpef_gross(period.regular_taxable, rules)
    separate = period_irpef_gross(period.separate_taxable, rules)
    deductions = money(annual.work_deduction * period.day_share) + period.family
    ulteriore = (
        _ZERO
        if annual.ulteriore is None
        else money(annual.ulteriore.amount * period.day_share)
    )
    without = max(_ZERO, regular - deductions)
    withheld = max(_ZERO, regular - deductions - ulteriore)
    return PeriodTax(withheld + separate, without + separate)


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
