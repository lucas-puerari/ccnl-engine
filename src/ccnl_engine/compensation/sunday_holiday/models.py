"""The holidays a CCNL pays a further day for when they fall on a Sunday."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["SundayHolidayPay"]


class SundayHolidayPay(BaseModel):
    """The CCNL clause that pays a holiday falling on a Sunday.

    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily
    quota for the civil holidays of 25 April, 1 May and 2 June falling on a
    Sunday; a CCNL extends it to other holidays.

    Attributes:
        holidays: The day codes of the national holiday calendar (``MM-DD``
            or ``easter_monday``) the CCNL pays on a Sunday.
        divisor: The divisor of the daily pay the clause names (Chimica
            art. 20 point 4: 25); ``None`` for the CCNL absence divisor.
        excluded: The allowance codes the clause leaves out of the monthly
            pay (Concia art. 46 lett. g: the quadri function allowance).
        provenance: The CCNL clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    holidays: tuple[str, ...] = Field(min_length=1)
    divisor: Decimal | None = Field(default=None, gt=0)
    excluded: frozenset[str] = frozenset()
    provenance: RuleProvenance
