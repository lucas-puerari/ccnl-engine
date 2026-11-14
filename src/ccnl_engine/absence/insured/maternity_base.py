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

    Art. 23 D.Lgs. 151/2001 pays the leave on the pay of the month before,
    and INPS computes it as the sickness base: "la retribuzione media
    globale giornaliera da prendere a base per il calcolo dell'indennità
    giornaliera di maternità ... è identica a quella da prendere a base per
    il calcolo dell'indennità giornaliera di malattia" (INPS circ. 10/1980
    par. 2.4).  An impiegata's pay over 30 (or over the days worked or paid
    of a month not worked in full), an operaia's over the days worked or
    paid, the monthly share of the extra months over 30 or 25
    (:func:`~ccnl_engine.sickness.base.rules.daily_base`).

    Returns:
        ``(rmgg, computable)``: the base, ``None`` when the stated pay does
        not give one (an operaia without her days, a month not worked in
        full without the pay of a whole month) or no pay is stated; whether
        the engine can compute a base once the pay is stated.
    """
    computable = category is not None and monthly_payments is not None
    if not computable or base is None or monthly_payments is None:
        return None, computable
    return daily_base(base, category, monthly_payments), True
