"""Issues and decision inputs of a sickness episode counted over several.

A CCNL that counts the sickness of several episodes
(:mod:`~ccnl_engine.sickness.cumulation.rules`) pays a sick day from
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

from ccnl_engine.decision.models import (
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)

if TYPE_CHECKING:
    from ccnl_engine.sickness.cumulation.results import CumulationReport
    from ccnl_engine.sickness.cumulation.year.rules import YearTreatment
    from ccnl_engine.sickness.models import SicknessEpisode
    from ccnl_engine.sickness.term.rules import (
        SicknessTerms,
    )

__all__ = [
    "BAND_CHANGES",
    "EXEMPTION_UNKNOWN",
    "FIXED_TERM",
    "HISTORY_UNKNOWN",
    "HOSPITAL_STAY",
    "HOSPITAL_STAY_UNKNOWN",
    "SENIORITY_UNKNOWN",
    "SERIOUS_ILLNESS_UNKNOWN",
    "cumulation_inputs",
    "cumulation_issues",
    "year_issues",
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
#: A day is paid at the reduced rate and a serious illness is not stated.
SERIOUS_ILLNESS_UNKNOWN = "sickness_serious_illness_unknown"
#: A day is paid at the reduced rate and the hospital stays are not stated.
HOSPITAL_STAY_UNKNOWN = "sickness_hospital_stays_unknown"
#: The full-pay and comporto days of a fixed-term contract are not scaled.
FIXED_TERM = "sickness_fixed_term_proportion"

_PROVISIONAL, _RULE = CalculationStatus.PROVISIONAL, IssueCause.RULE


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
    )


def _serious_issue(
    episode: SicknessEpisode, report: CumulationReport, terms: SicknessTerms
) -> CalculationIssue | None:
    """Return the issue of reduced days a serious illness could change.

    Returns:
        For a CCNL with a serious-illness treatment, a missing-fact issue
        when the episode does not say whether it is one and its days are
        reduced; else ``None``.
    """
    rules = terms.rules
    cumulation = None if rules is None else rules.ccnl.cumulation
    if (
        not report.reduced
        or episode.serious_illness is not None
        or cumulation is None
        or cumulation.serious_illness is None
    ):
        return None
    return CalculationIssue(
        code=SERIOUS_ILLNESS_UNKNOWN,
        capability="sickness",
        message=(
            f"sickness episode '{episode.episode_id}': days are paid at the "
            "reduced rate; the CCNL treats a particularly serious illness "
            "apart (its pay or its comporto): state "
            "SicknessEpisode.serious_illness"
        ),
        status=_PROVISIONAL,
        fact="serious_illness",
    )


def _hospital_issue(
    episode: SicknessEpisode, report: CumulationReport, terms: SicknessTerms
) -> CalculationIssue | None:
    """Return the issue of reduced days a hospital stay could change.

    Returns:
        For a CCNL that pays long stays in full, a missing-fact issue when
        the stays are not stated; for one without that rule, an issue that
        stays are not modelled; ``None`` without reduced days.
    """
    if not report.reduced:
        return None
    name = f"sickness episode '{episode.episode_id}'"
    rules = terms.rules
    cumulation = None if rules is None else rules.ccnl.cumulation
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
            status=_PROVISIONAL,
            fact="hospital_stays",
        )
    return CalculationIssue(
        code=HOSPITAL_STAY,
        capability="sickness",
        message=(
            f"{name}: days are paid at the reduced rate; a hospital stay the "
            "CCNL could pay in full is not modelled for it"
        ),
        status=_PROVISIONAL,
        cause=IssueCause.RULE,
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
        CalculationIssue(code, message, _PROVISIONAL, None, fact, "sickness", _RULE)
        for holds, code, message, fact in _messages(episode, report)
        if holds
    ]
    serious = _serious_issue(episode, report, terms)
    if serious is not None:
        issues.append(serious)
    hospital = _hospital_issue(episode, report, terms)
    if hospital is not None:
        issues.append(hospital)
    if terms.fixed_term:
        issues.append(
            CalculationIssue(
                code=FIXED_TERM,
                capability="sickness",
                message=(
                    f"sickness episode '{episode.episode_id}': the CCNL scales "
                    "the full-pay and comporto days to the length of a "
                    "fixed-term contract, which is not modelled"
                ),
                status=_PROVISIONAL,
                cause=IssueCause.RULE,
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


def year_issues(
    episode: SicknessEpisode, year: YearTreatment
) -> tuple[CalculationIssue, ...]:
    """Return the issues of a treatment counted over the year or a window.

    Returns:
        A provisional issue when sick days before the known history, an
        unknown seniority or an unstated exemption could change the comporto
        or the carenza.
    """
    name = f"sickness episode '{episode.episode_id}'"
    conditions = (
        (
            year.history_reach,
            HISTORY_UNKNOWN,
            (
                f"{name}: sick days of the year or window before the history "
                "the state records could change the comporto or the carenza "
                "counted; state from which day the imported episodes are complete "
                "(OpeningBalances.sickness_known_from)"
            ),
            "sickness_known_from",
        ),
        (
            year.seniority_reach,
            SENIORITY_UNKNOWN,
            (
                f"{name}: the days pass the comporto of the first seniority band, "
                "and the seniority is not known; the first band is applied"
            ),
            "seniority",
        ),
        (
            year.exemption_reach,
            EXEMPTION_UNKNOWN,
            (
                f"{name}: its carenza is paid less from the n-th event of the year "
                "unless the CCNL exempts an event; an exemption is not stated, so "
                "the higher carenza is paid"
            ),
            "short_absence_exempt",
        ),
    )
    return tuple(
        CalculationIssue(code, message, _PROVISIONAL, None, fact, "sickness", _RULE)
        for holds, code, message, fact in conditions
        if holds
    )
