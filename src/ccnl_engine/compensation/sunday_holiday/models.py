"""The holidays a CCNL pays a further day for when they fall on a Sunday."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["ExHolidayPay", "SundayHolidayPay"]


class ExHolidayPay(BaseModel):
    """The pay of the ex holiday of 4 November in a month of the CCNL's own.

    Chimica art. 13 pays, "in occasione del pagamento della retribuzione del
    mese di agosto, a fronte della ex festività del 4 novembre", 8/173 of
    the monthly pay, in place of the treatment of a holiday on a Sunday.

    Attributes:
        month: The month whose pay carries it.
        hours: The hours of hourly pay it is (Chimica: 8).
        hourly_divisor: The divisor of the hourly pay (Chimica: 173).
        provenance: The CCNL clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    month: int = Field(ge=1, le=12)
    hours: Decimal = Field(gt=0)
    hourly_divisor: Decimal = Field(gt=0)
    provenance: RuleProvenance


class SundayHolidayPay(BaseModel):
    """The CCNL clause that pays a holiday falling on a Sunday.

    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily
    quota for the civil holidays of 25 April, 1 May and 2 June falling on a
    Sunday; a CCNL extends it to other holidays.

    Attributes:
        holidays: The day codes of the national holiday calendar (``MM-DD``
            or ``easter_monday``) the CCNL pays on a Sunday; ``11-04`` for
            4 November, celebrated on the first Sunday of November (L.
            54/1977 art. 1 c. 2), paid with the same quota.
        divisor: The divisor of the daily pay the clause names (Chimica
            art. 20 point 4: 25); ``None`` for the CCNL absence divisor.
        excluded: The allowance codes the clause leaves out of the monthly
            pay (Concia art. 46 lett. g: the quadri function allowance).
        ex_november_fourth: The pay of 4 November in another month and
            share, in place of the quota of ``11-04``.
        provenance: The CCNL clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    holidays: tuple[str, ...] = Field(min_length=1)
    divisor: Decimal | None = Field(default=None, gt=0)
    excluded: frozenset[str] = frozenset()
    ex_november_fourth: ExHolidayPay | None = None
    provenance: RuleProvenance
