"""Caps, durations and codes of the contribution exemptions.

INPS circ. 90/2025 (young), 91/2025 (women), 10/2026 (ZES) and 82/2026
(mothers): the monthly cap is cut to 1/31 a day for an employment that
starts or ends in the month ("€16,12 (€500/31 gg)") and in proportion for
a part-time worker; the exemption is shown per worker in the UniEmens
<CodiceCausale> of <InfoAggcausaliContrib>.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, Decimal

from ccnl_engine.contribution.exemption.inputs import (
    ContributionExemption,
    ExemptionMeasure,
)
from ccnl_engine.pay_item.rounding.policies import money

__all__ = ["MeasureRule", "measure_rule", "month_cap", "months_of"]

_CENT = Decimal("0.01")
_DAYS = 31


@dataclass(frozen=True)
class MeasureRule:
    """What the law fixes for one measure.

    Attributes:
        cap: Monthly cap of the exemption.
        last_start: Last day a hire may start it.
        code: UniEmens <CodiceCausale>.
        managers: Whether a dirigente may take it.
    """

    cap: Decimal
    last_start: date
    code: str
    managers: bool


_RULES = {
    ExemptionMeasure.YOUNG: MeasureRule(Decimal(500), date(2026, 4, 30), "EG35", False),
    ExemptionMeasure.WOMEN: MeasureRule(Decimal(650), date(2026, 12, 31), "ED25", True),
    ExemptionMeasure.ZES: MeasureRule(Decimal(650), date(2026, 4, 30), "EZES", False),
    ExemptionMeasure.MOTHERS: MeasureRule(
        Decimal("666.66"), date(2026, 12, 31), "ELM3", True
    ),
}
#: Local variants: art. 22 c. 3 (650 EUR, ES35) and the ZES women (EDZE).
_LOCAL = {
    ExemptionMeasure.YOUNG: (Decimal(650), "ES35"),
    ExemptionMeasure.WOMEN: (Decimal(650), "EDZE"),
}


def measure_rule(exemption: ContributionExemption) -> MeasureRule:
    """Return the rule of the measure, its local variant when stated.

    Returns:
        The cap, last start, code and dirigenti of the measure.
    """
    rule = _RULES[exemption.measure]
    if not exemption.territorial:
        return rule
    cap, code = _LOCAL[exemption.measure]
    return MeasureRule(cap, rule.last_start, code, rule.managers)


def months_of(exemption: ContributionExemption, *, fixed_term: bool) -> int:
    """Return the months the exemption lasts from its start.

    L. 199/2025 art. 1 c. 212: 12 months for a fixed-term hire, 18 from the
    hire for one made permanent, 24 for a permanent hire; 24 for the DL
    60/2024 measures.

    Returns:
        The duration in months.
    """
    if exemption.measure is not ExemptionMeasure.MOTHERS:
        return 24
    if exemption.made_permanent:
        return 18
    return 12 if fixed_term else 24


def month_cap(cap: Decimal, days: int | None, part_time: Decimal | None) -> Decimal:
    """Return the cap of a month.

    Args:
        cap: Monthly cap of the measure.
        days: Days of the month the exemption covers when it does not
            cover the whole month; ``None`` for a whole month.
        part_time: Part-time ratio, ``None`` for a full-time worker.

    Returns:
        ``cap``, or its daily 1/31, cut to the cent as INPS prints it
        (500/31 = 16.12), times the days; times the part-time ratio,
        rounded to the cent.
    """
    month = cap if days is None else (cap / _DAYS).quantize(_CENT, ROUND_DOWN) * days
    scaled = month if part_time is None else month * part_time
    return money(scaled)
