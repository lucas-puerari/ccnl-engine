"""Issues and decision inputs of a sickness episode counted over several.

A CCNL that counts the sickness of several episodes
(:mod:`~ccnl_engine.payroll.domain.sick_cumulation`) pays a sick day from
facts the engine may not know.  The episode raises a provisional issue
whenever one of them could change the days the run pays:

- the sickness before the known history, the seniority or the exemption of
  a short absence, each naming the public fact that settles it;
- a seniority band that changes within the days paid (the band of the
  first day of the episode is applied);
- a day paid at the reduced rate: a hospital stay longer than ten days is
  paid in full on top of the chain (Federmeccanica, Sez. IV Tit. VI
  Art. 2), and the engine does not know the stays;
- a fixed-term contract: the CCNL scales the full-pay and comporto days of
  the first band to the length of the contract, which is not modelled.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.handlers._sickness_terms import (
        SicknessTerms,
    )
    from ccnl_engine.payroll.domain.sick_cumulation_report import CumulationReport
    from ccnl_engine.payroll.domain.sickness import SicknessEpisode

__all__ = [
    "BAND_CHANGES",
    "EXEMPTION_UNKNOWN",
    "FIXED_TERM",
    "HISTORY_UNKNOWN",
    "HOSPITAL_STAY",
    "SENIORITY_UNKNOWN",
    "cumulation_inputs",
    "cumulation_issues",
]

#: Sick days before the known history could change the treatment.
HISTORY_UNKNOWN = "sickness_history_unknown"
#: The seniority is unknown and a longer band could change the treatment.
SENIORITY_UNKNOWN = "sickness_seniority_unknown"
#: A short absence could be reduced and its exemption is not stated.
EXEMPTION_UNKNOWN = "sickness_short_absence_exemption_unknown"
#: The seniority band changes within the days paid.
BAND_CHANGES = "sickness_seniority_band_changes"
#: A day is paid at the reduced rate and hospital stays are not modelled.
HOSPITAL_STAY = "sickness_hospital_stay_not_modelled"
#: The full-pay and comporto days of a fixed-term contract are not scaled.
FIXED_TERM = "sickness_fixed_term_proportion"

_PROVISIONAL = CalculationStatus.PROVISIONAL


def _messages(
    episode: SicknessEpisode, report: CumulationReport
) -> tuple[tuple[bool, str, str, str | None], ...]:
    """Return each condition with its issue code, message and fact.

    Returns:
        ``(holds, code, message, fact)`` per condition.
    """
    name = f"sickness episode '{episode.episode_id}'"
    return (
        (
            report.history_reach,
            HISTORY_UNKNOWN,
            (
                f"{name}: sick days before the history the state records could "
                "change the comporto, the full-pay days or the short absences "
                "counted; state from which day the imported episodes are complete "
                "(OpeningBalances.sickness_known_from)"
            ),
            "sickness_known_from",
        ),
        (
            report.seniority_reach,
            SENIORITY_UNKNOWN,
            (
                f"{name}: the days counted pass the full-pay or comporto days of the "
                "first seniority band, and the seniority is not known; the first "
                "band is applied"
            ),
            "seniority",
        ),
        (
            report.exemption_reach,
            EXEMPTION_UNKNOWN,
            (
                f"{name}: a short absence of its rank in the year is paid less "
                "unless the CCNL exempts it; the exemption is not stated, so it is "
                "paid unreduced"
            ),
            "short_absence_exempt",
        ),
        (
            report.band_changes,
            BAND_CHANGES,
            (
                f"{name}: the seniority band changes within the days paid; the "
                "band of the first day of the episode is applied"
            ),
            None,
        ),
        (
            report.reduced,
            HOSPITAL_STAY,
            (
                f"{name}: days are paid at the reduced rate; a hospital stay of "
                "more than ten days would be paid in full and is not modelled"
            ),
            None,
        ),
    )


def cumulation_issues(
    episode: SicknessEpisode, report: CumulationReport, terms: SicknessTerms
) -> tuple[CalculationIssue, ...]:
    """Return the issues of a cumulated treatment.

    Returns:
        A provisional issue per fact or rule that could change the days the
        run pays.
    """
    issues = [
        CalculationIssue(code=code, message=message, status=_PROVISIONAL, fact=fact)
        for holds, code, message, fact in _messages(episode, report)
        if holds
    ]
    if terms.fixed_term:
        issues.append(
            CalculationIssue(
                code=FIXED_TERM,
                message=(
                    f"sickness episode '{episode.episode_id}': the CCNL scales "
                    "the full-pay and comporto days to the length of a "
                    "fixed-term contract, which is not modelled"
                ),
                status=_PROVISIONAL,
            )
        )
    return tuple(issues)


def cumulation_inputs(report: CumulationReport) -> dict[str, Decimal]:
    """Return the counts of a cumulated treatment, for the decision.

    Returns:
        The band, chain and window counts on the last day paid.
    """
    band = report.band
    counts = {
        "band_seniority_months_from": band.seniority_months_from,
        "band_full_pay_days": band.full_pay_days,
        "band_comporto_days": band.comporto_days,
        "chain_days": report.chain_days,
        "window_days": report.window_days,
    }
    return {name: Decimal(count) for name, count in counts.items()}
