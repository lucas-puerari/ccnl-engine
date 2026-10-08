"""Default cases of the pay of the days of an absence.

Part of :data:`tests.fixtures.default_cases.DEFAULT_CASES`: a day of
unpaid absence in January 2026 whose pay is stated, or left unknown.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.events import AbsenceEvent

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ccnl_engine.events import WorkEvent

__all__ = ["absence_cases"]


def _day_off(no_pay_due: bool | None) -> AbsenceEvent:
    return AbsenceEvent(
        date(2026, 1, 12), Decimal(8), Decimal("11.86"), no_pay_due=no_pay_due
    )


def absence_cases[C](
    pair: Callable[[WorkEvent, WorkEvent, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the pay of an absence, built with ``pair``.

    Returns:
        The cases keyed ``Type.field``.
    """
    return {
        "AbsenceEvent.no_pay_due": (
            pair(_day_off(True), _day_off(None), "no_pay_due"),
            pair(_day_off(False), _day_off(None), "no_pay_due"),
        ),
    }
