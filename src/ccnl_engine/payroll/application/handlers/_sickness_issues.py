"""Decision and issues of a sickness episode."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.sick_days import SickDayKind

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.application.handlers._sickness_pay import EpisodePay
    from ccnl_engine.payroll.application.handlers._sickness_terms import (
        SicknessTerms,
    )
    from ccnl_engine.payroll.domain.sickness import SicknessEpisode

__all__ = [
    "BEYOND_COMPORTO",
    "COVER_UNKNOWN",
    "CUMULATION_LIMITATION",
    "INPS_DAILY_BASE_LIMITATION",
    "PAID",
    "QUOTA_MISSING",
    "RULE_MISSING",
    "episode_decision",
    "episode_issues",
    "episode_limitations",
]

CAPABILITY = "sickness"
#: Engine limitation of the INPS share computed on the CCNL daily quota.
INPS_DAILY_BASE_LIMITATION = "sickness_inps_daily_base"
#: Engine limitation of the CCNL tiers counted over one relapse chain.
CUMULATION_LIMITATION = "sickness_cumulation_window"
#: Reason of an episode paid from the CCNL and INPS rules.
PAID = "sickness_episode_paid"
#: The CCNL defines no sickness rule: nothing is posted.
RULE_MISSING = "sickness_rule_missing"
#: The CCNL defines no daily quota: nothing is posted.
QUOTA_MISSING = "sickness_daily_quota_missing"
#: Sick days past the comporto: they are left out.
BEYOND_COMPORTO = "sickness_beyond_comporto"
#: The bundle does not say whether INPS pays the worker.
COVER_UNKNOWN = "sickness_inps_cover_unknown"
_NONE = "none"
_ZERO = Decimal(0)


def _issue(
    code: str, message: str, status: CalculationStatus, fact: str | None = None
) -> CalculationIssue:
    return CalculationIssue(code=code, message=message, status=status, fact=fact)


def _missing(episode: SicknessEpisode, terms: SicknessTerms) -> CalculationIssue:
    """Return the issue of an episode the CCNL data cannot pay.

    Returns:
        An incomplete issue naming the missing rule.
    """
    if terms.rules is None:
        return _issue(
            RULE_MISSING,
            f"sickness episode '{episode.episode_id}': the CCNL data define no "
            "sickness rule (work_rules.sickness_rules); the sick days are left "
            "out of the amounts",
            CalculationStatus.INCOMPLETE,
        )
    return _issue(
        QUOTA_MISSING,
        f"sickness episode '{episode.episode_id}': the CCNL data define no daily "
        "quota (work_rules.absence_rules); the sick days are left out of the "
        "amounts",
        CalculationStatus.INCOMPLETE,
    )


def episode_issues(
    episode: SicknessEpisode, pay: EpisodePay | None, terms: SicknessTerms
) -> tuple[CalculationIssue, ...]:
    """Return the issues of ``episode`` in the run.

    Returns:
        An incomplete issue for a missing rule or days past the comporto;
        a provisional one when INPS cover is unknown for indemnified days.
    """
    if pay is None:
        return (_missing(episode, terms),)
    issues: list[CalculationIssue] = []
    kinds = {segment.kind for segment in pay.segments}
    if SickDayKind.BEYOND_COMPORTO in kinds:
        issues.append(
            _issue(
                BEYOND_COMPORTO,
                f"sickness episode '{episode.episode_id}' lasts past the "
                "comporto of the CCNL (max_duration_days): those days are left "
                "out of the amounts",
                CalculationStatus.INCOMPLETE,
            )
        )
    rules = terms.rules
    if (
        rules is not None
        and rules.inps_cover is None
        and any(rules.inps.band_rate(s.first_index) for s in pay.segments)
        and SickDayKind.INDEMNIFIED in kinds
    ):
        issues.append(
            _issue(
                COVER_UNKNOWN,
                f"sickness episode '{episode.episode_id}': the bundle does not "
                "say whether INPS pays the indemnity to this worker (state the "
                "worker category when it is not fixed by the level); the days "
                "are paid as if INPS did not, at the CCNL rate only",
                CalculationStatus.PROVISIONAL,
                terms.cover_fact,
            )
        )
    return tuple(issues)


def _segments(pay: EpisodePay) -> str:
    return ";".join(
        f"{s.first.isoformat()}..{s.last.isoformat()}:{s.kind.value}:"
        f"index={s.first_index}:units={units}:inps={s.inps_rate}:"
        f"worker={s.worker_rate}"
        for s, units in zip(pay.segments, pay.units, strict=True)
    )


def _inputs(
    episode: SicknessEpisode,
    span: tuple[date, date],
    pay: EpisodePay | None,
    terms: SicknessTerms,
) -> dict[str, Decimal | str]:
    rules, quota = terms.rules, terms.quota
    cover = None if rules is None else rules.inps_cover
    inputs: dict[str, Decimal | str] = {
        "episode_id": episode.episode_id,
        "started_on": episode.started_on.isoformat(),
        "ended_on": episode.ended_on.isoformat(),
        "relapse_of": episode.relapse_of or _NONE,
        "sick_from": span[0].isoformat(),
        "sick_until": span[1].isoformat(),
        "divisor_method": _NONE if quota is None else quota.method.value,
        "divisor": _NONE if quota is None else quota.divisor,
        "inps_cover": _NONE if cover is None else str(cover).lower(),
    }
    if pay is not None:
        inputs |= {
            "segments": _segments(pay),
            "absence": pay.absence,
            "inps_indemnity": pay.inps,
            "employer_integration": pay.integration,
            "carenza_pay": pay.carenza,
        }
    return inputs


def episode_decision(
    episode: SicknessEpisode,
    span: tuple[date, date],
    pay: EpisodePay | None,
    terms: SicknessTerms,
    issues: tuple[CalculationIssue, ...],
) -> CalculationDecision:
    """Return the ``sickness`` decision of ``episode`` in the run.

    Returns:
        A decision whose status is the worst of its issues, with the amount
        paid back for the sick days; no amount when nothing is posted.
    """
    status = CalculationStatus.worst(issue.status for issue in issues)
    return CalculationDecision(
        capability=CAPABILITY,
        status=status,
        reason_code=issues[0].code if issues else PAID,
        rule=terms.rule,
        rule_version=terms.rule_version,
        inputs=_inputs(episode, span, pay, terms),
        source=terms.source,
        amount=None if pay is None else pay.paid,
    )


def episode_limitations(
    event: SicknessEpisode, pay: EpisodePay | None, terms: SicknessTerms
) -> tuple[str, ...]:
    """Return the engine limitations whose path the episode took.

    Returns:
        The INPS daily base when INPS pays a share; the cumulation window
        when an earlier episode outside the relapse chain is recorded.
    """
    found: list[str] = []
    if pay is not None and pay.inps > _ZERO:
        found.append(INPS_DAILY_BASE_LIMITATION)
    chain = _chain_ids(event, terms)
    if any(e.episode_id not in chain for e in terms.history.earlier(event)):
        found.append(CUMULATION_LIMITATION)
    return tuple(found)


def _chain_ids(event: SicknessEpisode, terms: SicknessTerms) -> frozenset[str]:
    """Return the ids of the episodes ``event`` continues.

    Returns:
        The ids of its relapse chain, itself excluded.
    """
    ids: set[str] = set()
    current = event.relapse_of
    episodes = {e.episode_id: e for e in terms.history.episodes}
    while current is not None and current not in ids and current in episodes:
        ids.add(current)
        current = episodes[current].relapse_of
    return frozenset(ids)
