"""The INPS daily base of a sickness episode and the INPS share of its days.

The *retribuzione media globale giornaliera* (RMGG) is the pay of the month
before the illness and the monthly share of the recurring payments outside
it (INPS circ. 134368 A.G.O. 14 of 28 January 1981, point 11):

- impiegato (point 11.2): the sum divided by 30; when the month was not
  worked in full, the pay divided by its days worked or paid, Sundays and
  paid holidays included, plus the share of a whole month divided by 30;
- operaio (point 11.3): the pay divided by the days worked or paid in the
  month, plus the monthly share divided by 25.

The monthly share is a twelfth of the additional months of the CCNL on the
pay of a whole month (circ. 55/2024 Allegato 1: the *retribuzione teorica*
times the number of monthly payments) and of the other recurring payments
of the year.  INPS pays its share on every calendar day the certificate
covers.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.category.models import WorkerCategory

if TYPE_CHECKING:
    from ccnl_engine.sickness.base.inputs import InpsSicknessBase
    from ccnl_engine.sickness.models import SicknessEpisode
    from ccnl_engine.sickness.term.rules import SicknessTerms

__all__ = ["daily_base", "episode_daily_base"]

_MONTHS = Decimal(12)
#: Divisor of an impiegato's month (point 11.2 letter c).
_CALENDAR_DIVISOR = Decimal(30)
#: Divisor of an operaio's monthly share of recurring payments (point 11.3 e).
_OPERAIO_SHARE_DIVISOR = Decimal(25)


def daily_base(
    base: InpsSicknessBase,
    category: WorkerCategory | None,
    monthly_payments: Decimal,
) -> Decimal | None:
    """Return the RMGG of an episode, unrounded.

    Args:
        base: The pay of the month before the illness.
        category: Category of the worker; an operaio divides by the days.
        monthly_payments: Monthly payments of a year under the CCNL in that
            month, the additional months included (``13`` for a 13th).

    Returns:
        The daily base; ``None`` when it cannot be told: an unknown
        category, an operaio whose days are not stated, or an impiegato of
        a month not worked in full without the pay of a whole month.
    """
    if category is None:
        return None
    extra = max(monthly_payments - _MONTHS, Decimal(0))
    whole = base.theoretical_pay if base.full_month_pay is None else base.full_month_pay
    share = (whole * extra + base.recurring_annual) / _MONTHS
    days = base.paid_days
    if category is WorkerCategory.OPERAIO:
        if days is None:
            return None
        return base.theoretical_pay / days + share / _OPERAIO_SHARE_DIVISOR
    if days is None:
        return (base.theoretical_pay + share) / _CALENDAR_DIVISOR
    if base.full_month_pay is None:
        return None
    return base.theoretical_pay / days + share / _CALENDAR_DIVISOR


def _stated(
    episode: SicknessEpisode, terms: SicknessTerms
) -> tuple[InpsSicknessBase, date] | None:
    """Return the base an episode reads and the first day of its illness.

    A relapse without a base of its own takes that of the episode it
    continues, as INPS pays the relapse as the same event.

    Returns:
        The stated base and the first day of the episode that states it;
        ``None`` when no episode of the chain states one.
    """
    episodes: dict[str | None, SicknessEpisode] = {
        e.episode_id: e for e in terms.history.episodes
    }
    current: SicknessEpisode | None = episode
    seen: set[str] = set()
    while current is not None and current.episode_id not in seen:
        if current.inps_base is not None:
            return current.inps_base, current.started_on
        seen.add(current.episode_id)
        current = episodes.get(current.relapse_of)
    return None


def episode_daily_base(
    episode: SicknessEpisode, terms: SicknessTerms
) -> Decimal | None:
    """Return the RMGG the INPS share of ``episode`` is computed on.

    The monthly payments are those of the CCNL on the last day of the
    month before the illness.

    Returns:
        The daily base; ``None`` under a sector regime, without a stated
        base or when :func:`daily_base` cannot tell it.
    """
    stated = None if not terms.general_regime else _stated(episode, terms)
    if stated is None or terms.monthly_payments is None:
        return None
    base, started_on = stated
    month_before = started_on.replace(day=1) - timedelta(days=1)
    period = terms.monthly_payments.period_at(month_before)
    if period is None or period.value is None:
        return None
    return daily_base(base, terms.category, period.value)
