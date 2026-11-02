"""The fact a fixed-term sickness episode lacks to be paid on its own days."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.sickness.day.models import SickPayRules
    from ccnl_engine.sickness.models import SicknessEpisode

__all__ = ["AGRICULTURAL_DAYS_UNKNOWN", "PRIOR_WORK_UNKNOWN", "fixed_term_fact"]

#: A fixed-term episode does not state the days of work before it.
PRIOR_WORK_UNKNOWN = "sickness_fixed_term_prior_work_unknown"
#: An operaio agricolo a tempo determinato does not state the elenchi days.
AGRICULTURAL_DAYS_UNKNOWN = "sickness_agricultural_days_unknown"


def fixed_term_fact(
    episode: SicknessEpisode, rules: SickPayRules | None
) -> tuple[str, str, str] | None:
    """Return the code, message and fact of the days a fixed-term episode lacks.

    Returns:
        For a regime INPS pays directly (operai agricoli) without the days
        in the elenchi, or for another fixed-term contract without the days
        of work of the 12 months before, the provisional issue's code,
        message and fact; ``None`` otherwise.
    """
    if rules is None or not rules.fixed_term:
        return None
    name = f"sickness episode '{episode.episode_id}'"
    if rules.paid_directly:
        if episode.agricultural_days is not None:
            return None
        return (
            AGRICULTURAL_DAYS_UNKNOWN,
            (
                f"{name}: INPS pays an operaio agricolo a tempo determinato for "
                "the days of registration in the elenchi of the year before (at "
                "most 180), with 51 of them or 51 of the current year (then 30); "
                "state agricultural_days, the days are paid up to 180 a year"
            ),
            "agricultural_days",
        )
    if episode.prior_worked_days is not None:
        return None
    return (
        PRIOR_WORK_UNKNOWN,
        (
            f"{name}: a fixed-term contract pays sickness for no more days than "
            "those of work in the 12 months before (D.L. 463/1983 art. 5); state "
            "prior_worked_days, the days are paid without that limit"
        ),
        "prior_worked_days",
    )
