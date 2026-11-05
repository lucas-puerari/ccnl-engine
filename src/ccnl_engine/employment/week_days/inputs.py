"""The working days of the full-time week of the employment.

Some CCNLs set the daily pay by the days the full-time week is spread over:
"La determinazione della retribuzione giornaliera si ottiene dividendo la
retribuzione mensile per 22 nel caso di settimana corta e per 26 nel caso
di prestazione su sei giorni settimanali" (Pulizia artigianato art. 34;
Logistica art. 61 c. 3, Multiservizi art. 19, BCC art. 114 alike).
"""

from __future__ import annotations

from ccnl_engine.errors import InvalidInputError

__all__ = ["WEEK_DAYS", "check_week_days"]

#: The full-time weeks a CCNL sets a daily divisor for: five or six days.
WEEK_DAYS = frozenset({5, 6})
_PATH = "Employment.full_time_week_days"
_FEATURE = "employment_facts"


def check_week_days(value: object) -> int | None:
    """Return the working days of the full-time week, validated.

    Returns:
        ``value``, 5 or 6, or ``None`` when not stated.

    Raises:
        InvalidInputError: When ``value`` is not ``None``, 5 or 6.
    """
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value not in WEEK_DAYS:
        msg = f"{_PATH} must be 5 or 6 working days, or None; got {value!r}"
        raise InvalidInputError(msg, field=_PATH, feature=_FEATURE)
    return value
