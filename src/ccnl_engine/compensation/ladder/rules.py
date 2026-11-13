"""The ladders of the levels of a CCNL, ordinary and by sub-sector.

A level with ``Level.subsectors`` exists only for an employer of one of
them (Tessile PMI art. 46: the 4s of the pelli e cuoio, occhiali and
giocattoli tables).  A run keeps the levels of every sub-sector and those
of the stated one (:func:`levels_for`), and counts the levels below one on
that ladder by rank (:func:`level_below`): an under-classification never
reaches a level of another sub-sector.

A level with ``Level.ladder`` sits on a career ladder of its own (the
operatori di vendita of the Terziario contracts, I and II categoria, beside
the ordinary levels): it is ranked, and its pay must rise, only among the
levels of the same ladder.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.compensation.models import Level

__all__ = ["level_below", "levels_for", "pay_ladders"]


def levels_for(levels: Iterable[Level], subsector: str | None) -> tuple[Level, ...]:
    """Return the levels a run of an employer of ``subsector`` can use.

    Returns:
        The levels of every sub-sector and, when ``subsector`` is stated,
        those that exist only for it, in their original order.
    """
    return tuple(lv for lv in levels if not lv.subsectors or subsector in lv.subsectors)


def level_below(
    levels: Iterable[Level], level: Level, count: int, *, clamp: bool = False
) -> Level:
    """Return the level ``count`` ranks below ``level`` among ``levels``.

    Args:
        levels: The ladder, the levels of the run (:func:`levels_for`).
        level: The level to count from, one of ``levels``.
        count: The ranks below, by ``Level.order``, among the levels of the
            ladder of ``level`` (``Level.ladder``).
        clamp: Return the lowest level instead of raising past it.

    Returns:
        The level ``count`` ranks below ``level``.

    Raises:
        ValueError: When ``level`` is not on the ladder, or ``count`` reaches
            below its lowest level and ``clamp`` is false.
    """
    ladder = sorted(
        (lv for lv in levels if lv.ladder == level.ladder), key=lambda lv: lv.order
    )
    codes = [lv.code for lv in ladder]
    if level.code not in codes:
        msg = f"level {level.code!r} is not on the ladder {codes}"
        raise ValueError(msg)
    rank = codes.index(level.code) - count
    if rank < 0 and not clamp:
        msg = f"no level {count} below {level.code!r} on the ladder {codes}"
        raise ValueError(msg)
    return ladder[max(rank, 0)]


def pay_ladders(levels: Iterable[Level]) -> dict[str | None, list[Level]]:
    """Return the pay ladders the salaries must rise along, by sub-sector.

    The ordinary ladder (``None``) holds the levels of every sub-sector on
    their own table; the ladder of a sub-sector the levels that carry it,
    in ``Level.subsectors`` or ``Level.base_salary_by_subsector``, on its
    table; a career ladder of its own (``Level.ladder``, keyed
    ``ladder:<name>``) its levels, apart from all the others.

    Returns:
        Each ladder sorted by ``Level.order``.
    """
    every = list(levels)
    ordinary = [lv for lv in every if lv.ladder is None]
    ladders: dict[str | None, list[Level]] = {
        None: [lv for lv in ordinary if not lv.subsectors],
        **_subsector_ladders(ordinary),
    }
    for lv in every:
        if lv.ladder is not None:
            ladders.setdefault(f"ladder:{lv.ladder}", []).append(lv)
    return {code: sorted(ls, key=lambda lv: lv.order) for code, ls in ladders.items()}


def _subsector_ladders(levels: list[Level]) -> dict[str | None, list[Level]]:
    """Return the ladder of each sub-sector, on its table.

    Returns:
        The levels of each sub-sector named by a level, keyed by its code.
    """
    named = {
        code for lv in levels for code in (*lv.subsectors, *lv.base_salary_by_subsector)
    }
    return {
        code: [
            lv.model_copy(update={"base_salary": lv.base_salary_by_subsector[code]})
            if code in lv.base_salary_by_subsector
            else lv
            for lv in levels
            if code in lv.subsectors or code in lv.base_salary_by_subsector
        ]
        for code in sorted(named)
    }
