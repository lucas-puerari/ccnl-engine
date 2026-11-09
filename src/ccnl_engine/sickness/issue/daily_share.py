"""Missing facts for reference-date employer sickness supplements."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause

if TYPE_CHECKING:
    from ccnl_engine.sickness.models import SicknessEpisode
    from ccnl_engine.sickness.pay.handlers import EpisodePay
    from ccnl_engine.sickness.term.rules import SicknessTerms


def daily_share_issues(
    episode: SicknessEpisode, pay: EpisodePay, terms: SicknessTerms
) -> tuple[CalculationIssue, ...]:
    """Flag missing facts needed for an employer daily supplement.

    Returns:
        Provisional issues, or an empty tuple when the inputs are complete.
    """
    rules = terms.rules
    if rules is None or rules.ccnl.annual_daily_share is None or terms.fixed_term:
        return ()
    if episode.inps_recognized is None:
        return (
            CalculationIssue(
                "sickness_recognition_unknown",
                "Employer daily supplement requires INPS recognition; "
                "no supplement is paid without this fact",
                CalculationStatus.PROVISIONAL,
                None,
                "inps_recognized",
                "sickness",
                IssueCause.RULE,
            ),
        )
    if episode.inps_recognized and any(
        day.year not in (episode.contractual_daily_wage_by_year or {})
        for day in pay.sick_days
    ):
        return (
            CalculationIssue(
                "sickness_reference_wage_unknown",
                "Employer daily supplement requires the contractual daily wage "
                "on the reference date; no supplement is paid without it",
                CalculationStatus.PROVISIONAL,
                None,
                "contractual_daily_wage_by_year",
                "sickness",
                IssueCause.RULE,
            ),
        )
    return ()
