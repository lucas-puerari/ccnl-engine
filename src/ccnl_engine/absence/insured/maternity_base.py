"""Maternity indemnity base from the preceding month."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.sickness.base.inputs import InpsSicknessBase
from ccnl_engine.sickness.base.rules import daily_base


def maternity_daily_base(
    base: InpsSicknessBase | None,
    category: WorkerCategory | None,
    monthly_payments: Decimal | None,
) -> tuple[Decimal | None, bool]:
    """Return the maternity daily base and whether the engine can compute one.

    Art. 23 c. 4 D.Lgs. 151/2001: the pay of the month before the leave
    over 30, with the daily rateo of the 13th and of the other payments
    (c. 2), as the sickness base of an impiegato.  The base of an operaia
    (c. 5) and of a month not worked in full is not computed.

    Returns:
        ``(rmgg, computable)``: the base, ``None`` without one; whether a
        stated base would give one.
    """
    computable = (
        category is not None
        and category is not WorkerCategory.OPERAIO
        and monthly_payments is not None
        and (base is None or base.paid_days is None)
    )
    if not computable or base is None or monthly_payments is None:
        return None, computable
    return daily_base(base, category, monthly_payments), True
