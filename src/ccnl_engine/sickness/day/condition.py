"""The CCNL conditions of a sick day: the probation and a hospital stay."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.sickness.cumulation.rules import CcnlDay
    from ccnl_engine.sickness.day.models import SickPayRules

__all__ = ["day_conditions"]

_ZERO = Decimal(0)


def day_conditions(
    rules: SickPayRules, ccnl: CcnlDay, day: date, *, hospital: bool
) -> tuple[bool, Decimal]:
    """Return whether ``day`` is in a probation the CCNL pays after, and its stay share.

    Returns:
        The probation flag and the hospital share of the day, zero off a
        stay, in the probation or past the comporto.
    """
    until = rules.worker.probation_until
    on_probation = rules.ccnl.after_probation and until is not None and day <= until
    stay = rules.ccnl.hospital_employer_share
    if stay is None or not hospital or on_probation or ccnl.beyond_comporto:
        return on_probation, _ZERO
    return on_probation, stay
