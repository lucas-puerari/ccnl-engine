"""Issues of the unstated facts a CCNL sickness treatment depends on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.sickness.cumulation.hospital_issues import HOSPITAL_STAY_UNKNOWN
from ccnl_engine.sickness.day.rules import SickDayKind

if TYPE_CHECKING:
    from ccnl_engine.sickness.day.rules import SickDaySegment
    from ccnl_engine.sickness.models import SicknessEpisode
    from ccnl_engine.sickness.term.rules import SicknessTerms

__all__ = ["PROBATION_UNKNOWN", "condition_issues"]

CAPABILITY = "sickness"
#: The CCNL pays after the probation and its end is not stated.
PROBATION_UNKNOWN = "sickness_probation_unknown"
#: Days on which the CCNL pays nothing, whatever the facts.
_NO_CCNL_PAY = frozenset({SickDayKind.BEYOND_COMPORTO, SickDayKind.FIXED_TERM_LIMIT})


def condition_issues(
    episode: SicknessEpisode, terms: SicknessTerms, segments: tuple[SickDaySegment, ...]
) -> tuple[CalculationIssue, ...]:
    """Return the issues of the unstated facts a CCNL treatment depends on.

    Returns:
        A provisional missing-fact issue for each fact that could change the
        pay of a day within the comporto: the hospital stays of a CCNL that
        pays them apart, unless the probation covers the episode; the end of
        the probation of a CCNL that pays after it, when the CCNL pays the
        episode something.
    """
    rules = terms.rules
    open_days = [s for s in segments if s.kind not in _NO_CCNL_PAY]
    if rules is None or not open_days:
        return ()
    name = f"sickness episode '{episode.episode_id}'"
    issues: list[CalculationIssue] = []
    until = rules.worker.probation_until if rules.ccnl.after_probation else None
    stays_unknown = (
        rules.ccnl.hospital_employer_share is not None
        and episode.hospital_stays is None
    )
    if stays_unknown and (until is None or episode.ended_on > until):
        issues.append(
            CalculationIssue(
                HOSPITAL_STAY_UNKNOWN,
                f"{name}: the CCNL pays a share of the pay on the days of a "
                "hospital stay; state the stays of the episode "
                "(SicknessEpisode.hospital_stays), none is paid meanwhile",
                CalculationStatus.PROVISIONAL,
                fact="hospital_stays",
                capability=CAPABILITY,
            )
        )
    paid = any(s.worker_rate > s.inps_rate for s in open_days)
    if (
        rules.ccnl.after_probation
        and rules.worker.probation_until is None
        and (paid or stays_unknown)
    ):
        issues.append(
            CalculationIssue(
                PROBATION_UNKNOWN,
                f"{name}: the CCNL pays its treatment after the periodo di "
                "prova; state its end (EmploymentPeriod.probation_until), the "
                "treatment is paid meanwhile",
                CalculationStatus.PROVISIONAL,
                fact="probation_until",
                capability=CAPABILITY,
            )
        )
    return tuple(issues)
