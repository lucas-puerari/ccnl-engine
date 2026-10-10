"""National pay elements a provincial element replaces.

Some CCNL pay a national element only where no provincial element of the
same kind is in force: the terzo elemento nazionale of the Commercio CCNL
(Art. 215) is due "nelle provincie nelle quali non sono in atto terzi
elementi retributivi provinciali".  The allowances flagged
``replaced_by_provincial_element`` are paid only when
``EmployerProfile.provincial_pay_element`` is false; when it is true they
are not due, and when it is not known they are left out and the run names
the missing fact.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.compensation.models import Level
    from ccnl_engine.contract.identity.facade import CCNL

__all__ = ["without_replaced_elements"]


def without_replaced_elements(
    ccnl: CCNL, level_code: str, in_force: bool | None, day: date
) -> tuple[CCNL, tuple[str, ...]]:
    """Return the CCNL without the national elements a run does not pay.

    Args:
        ccnl: The CCNL of the run.
        level_code: Level of the run, whose elements in force on ``day``
            are reported when the fact is unknown.
        in_force: ``EmployerProfile.provincial_pay_element``.
        day: Competence date of the run.

    Returns:
        The CCNL, unchanged when ``in_force`` is false or no level has such
        an element, and the codes of the elements of the level left out
        because ``in_force`` is not known.
    """
    if in_force is False or not any(
        a.replaced_by_provincial_element
        for lv in ccnl.levels
        for a in lv.fixed_allowances
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
                if a.replaced_by_provincial_element and a.monthly.applies_on(day)
            )
        )
    levels = tuple(_without(level) for level in ccnl.levels)
    return ccnl.model_copy(update={"levels": levels}), unknown


def _without(level: Level) -> Level:
    kept = tuple(
        a for a in level.fixed_allowances if not a.replaced_by_provincial_element
    )
    return level.model_copy(update={"fixed_allowances": kept})
