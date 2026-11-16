"""Hours the final settlement of a first- or third-level apprentice pays ratei at.

The run that closes the employment pays the month at the hours of the month
and the ratei of the extra months at the hours of the period they accrued
over, each weighed by its own share of school, training and work (D.Lgs.
81/2015 art. 43 c. 7, art. 45 c. 3).
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.employment.apprentice.inputs import (
    Apprentice,
    ApprenticeshipProgramme,
)
from ccnl_engine.errors import MissingRequiredFactError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.employment.inputs import FixedTerm, Permanent
    from ccnl_engine.extra_month.models import ExtraMonthAccrual

__all__ = ["ratei_apprentice"]

_PROFESSIONALISING = ApprenticeshipProgramme.PROFESSIONALISING


def ratei_apprentice(
    contract_type: Permanent | FixedTerm | Apprentice,
    settlements: Sequence[ExtraMonthAccrual],
    ccnl_id: str,
) -> Apprentice | None:
    """Return the apprentice whose hours are those the ratei accrued over.

    Returns:
        ``contract_type`` with :attr:`Apprentice.ratei_hours` as its hours,
        for a first- or third-level apprentice whose run liquidates some
        ratei; ``None`` for any other contract or run.

    Raises:
        MissingRequiredFactError: When such a run does not state
            :attr:`Apprentice.ratei_hours`.
    """
    if (
        not isinstance(contract_type, Apprentice)
        or contract_type.programme is _PROFESSIONALISING
        or all(s.accrued <= 0 for s in settlements)
    ):
        return None
    if contract_type.ratei_hours is None:
        msg = (
            f"the final settlement of a {contract_type.programme.value} "
            f"apprentice of '{ccnl_id}' needs the hours its ratei accrued over"
        )
        raise MissingRequiredFactError(
            msg,
            feature="apprenticeship",
            ruleset=ccnl_id,
            remediation="State Apprentice.ratei_hours: school, company training, work.",
        )
    return replace(contract_type, hours=contract_type.ratei_hours)
