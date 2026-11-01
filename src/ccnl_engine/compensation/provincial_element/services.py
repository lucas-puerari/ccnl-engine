"""National pay elements a provincial element or a company premium replaces.

Some CCNL pay a national element only where no element of the same kind is
in force: the terzo elemento nazionale of the Commercio CCNL (Art. 215) is
due "nelle provincie nelle quali non sono in atto terzi elementi
retributivi provinciali"; the elemento di garanzia retributiva of the
Unionalimentari CCNL is paid by the firms that pay no premio per obiettivi.
An allowance whose ``replaced_by`` names the kind is paid only when the
employer fact of the kind (``EmployerProfile.provincial_pay_element``,
``EmployerProfile.second_level_premium``) is false; when it is true it is
not due, and when it is not known it is left out and the run names the
missing fact.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.models import Level

__all__ = ["without_replaced_elements"]


def without_replaced_elements(
    ccnl: CCNL, level_code: str, kind: str, in_force: bool | None, day: date
) -> tuple[CCNL, tuple[str, ...]]:
    """Return the CCNL without the national elements of ``kind`` a run does not pay.

    Args:
        ccnl: The CCNL of the run.
        level_code: Level of the run, whose elements in force on ``day``
            are reported when the fact is unknown.
        kind: What replaces the elements, as ``Allowance.replaced_by``.
        in_force: The employer fact of ``kind``.
        day: Competence date of the run.

    Returns:
        The CCNL, unchanged when ``in_force`` is false or no level has such
        an element, and the codes of the elements of the level left out
        because ``in_force`` is not known.
    """
    if in_force is False or not any(
        a.replaced_by == kind for lv in ccnl.levels for a in lv.fixed_allowances
    ):
        return ccnl, ()
    unknown: tuple[str, ...] = ()
    if in_force is None:
        unknown = tuple(
            sorted(
                a.code
                for lv in ccnl.levels
                if lv.code == level_code
                for a in lv.fixed_allowances
                if a.replaced_by == kind and a.monthly.applies_on(day)
            )
        )
    levels = tuple(_without(level, kind) for level in ccnl.levels)
    return ccnl.model_copy(update={"levels": levels}), unknown


def _without(level: Level, kind: str) -> Level:
    kept = tuple(a for a in level.fixed_allowances if a.replaced_by != kind)
    return level.model_copy(update={"fixed_allowances": kept})
