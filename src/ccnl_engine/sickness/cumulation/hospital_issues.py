"""Issues raised when a sickness rule depends on hospital stay facts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause

if TYPE_CHECKING:
    from ccnl_engine.sickness.cumulation.results import CumulationReport
    from ccnl_engine.sickness.models import SicknessEpisode
    from ccnl_engine.sickness.term.rules import SicknessTerms

#: A day is paid at the reduced rate and hospital stays are not modelled.
HOSPITAL_STAY = "sickness_hospital_stay_not_modelled"
#: A day is paid at the reduced rate and the hospital stays are not stated.
HOSPITAL_STAY_UNKNOWN = "sickness_hospital_stays_unknown"


def hospital_issue(
    episode: SicknessEpisode, report: CumulationReport, terms: SicknessTerms
) -> CalculationIssue | None:
    """Return the issue of a hospital stay that could change pay or comporto.

    Returns:
        For a CCNL that pays long stays in full, a missing-fact issue when
        the stays are not stated; for one without that rule, an issue that
        stays are not modelled; ``None`` without reduced days.
    """
    name = f"sickness episode '{episode.episode_id}'"
    rules = terms.rules
    cumulation = None if rules is None else rules.ccnl.cumulation
    if cumulation is not None and cumulation.hospital_excluded_from_counts:
        if episode.hospital_stays is None:
            return CalculationIssue(
                code=HOSPITAL_STAY_UNKNOWN,
                capability="sickness",
                message=(
                    f"{name}: state hospital_stays to determine the sick-pay "
                    "and comporto counts"
                ),
                status=CalculationStatus.PROVISIONAL,
                fact="hospital_stays",
            )
        return None
    if not report.reduced:
        return None
    if cumulation is not None and cumulation.hospital_stay is not None:
        if episode.hospital_stays is not None:
            return None
        return CalculationIssue(
            code=HOSPITAL_STAY_UNKNOWN,
            capability="sickness",
            message=(
                f"{name}: days are paid at the reduced rate; a hospital stay "
                "the CCNL pays in full could change them: state the stays of "
                "the episode (SicknessEpisode.hospital_stays)"
            ),
            status=CalculationStatus.PROVISIONAL,
            fact="hospital_stays",
        )
    return CalculationIssue(
        code=HOSPITAL_STAY,
        capability="sickness",
        message=(
            f"{name}: days are paid at the reduced rate; a hospital stay the "
            "CCNL could pay in full is not modelled for it"
        ),
        status=CalculationStatus.PROVISIONAL,
        cause=IssueCause.RULE,
    )
