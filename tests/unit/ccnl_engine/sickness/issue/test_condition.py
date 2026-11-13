"""Issues of the unstated facts a CCNL sickness treatment depends on."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.sickness.cumulation.worker import SicknessWorker
from ccnl_engine.sickness.day.rules import SickDayKind, SickDaySegment
from ccnl_engine.sickness.integration.models import SicknessRules
from ccnl_engine.sickness.issue.condition import condition_issues
from ccnl_engine.sickness.models import SicknessEpisode

if TYPE_CHECKING:
    from ccnl_engine.sickness.term.rules import SicknessTerms

_START, _END = date(2026, 3, 2), date(2026, 3, 13)
_EPISODE = SicknessEpisode("e", _START, _END)
_ZERO = Decimal(0)
_RULES = SicknessRules(
    carenza_integration_rate=Decimal("0.6"),
    full_pay_integration_rate=_ZERO,
    hospital_employer_share=Decimal("0.6"),
    after_probation=True,
)


def _segment(kind: SickDayKind, worker: str = "0.6") -> SickDaySegment:
    return SickDaySegment(_START, _START, 1, kind, _ZERO, Decimal(worker))


def _terms(probation_until: date | None = None) -> SicknessTerms:
    worker = SicknessWorker(probation_until=probation_until)
    rules = SimpleNamespace(ccnl=_RULES, worker=worker)
    return cast("SicknessTerms", SimpleNamespace(rules=rules))


def _codes(
    episode: SicknessEpisode, terms: SicknessTerms, *segments: SickDaySegment
) -> set[str]:
    return {issue.code for issue in condition_issues(episode, terms, segments)}


def test_without_rules_no_fact_is_named() -> None:
    """A CCNL without a sickness rule pays nothing a fact could change."""
    terms = cast("SicknessTerms", SimpleNamespace(rules=None))
    assert condition_issues(_EPISODE, terms, (_segment(SickDayKind.CARENZA),)) == ()


@pytest.mark.parametrize(
    "kind", [SickDayKind.BEYOND_COMPORTO, SickDayKind.FIXED_TERM_LIMIT]
)
def test_days_without_a_ccnl_treatment_name_no_fact(kind: SickDayKind) -> None:
    """Past the comporto or the fixed-term limit the CCNL pays nothing."""
    assert _codes(_EPISODE, _terms(), _segment(kind)) == set()


def test_unstated_stays_and_probation_are_named() -> None:
    """A paid carenza with neither fact stated names both."""
    assert _codes(_EPISODE, _terms(), _segment(SickDayKind.CARENZA)) == {
        "sickness_hospital_stays_unknown",
        "sickness_probation_unknown",
    }


def test_an_episode_within_the_stated_probation_needs_no_stays() -> None:
    """Art. 54 pays nothing in the probation: the stays cannot change it."""
    terms = _terms(probation_until=_END)
    carenza = _segment(SickDayKind.CARENZA, "0")
    assert _codes(_EPISODE, terms, carenza) == set()
    later = _terms(probation_until=date(2026, 3, 12))
    assert _codes(_EPISODE, later, carenza) == {"sickness_hospital_stays_unknown"}


def test_an_unpaid_episode_with_stated_stays_needs_no_probation() -> None:
    """A seventh event without a stay: no amount the probation could cancel."""
    episode = SicknessEpisode("e", _START, _END, hospital_stays=())
    unpaid = _segment(SickDayKind.CARENZA, "0")
    assert _codes(episode, _terms(), unpaid) == set()
    paid = _segment(SickDayKind.CARENZA)
    assert _codes(episode, _terms(), paid) == {"sickness_probation_unknown"}
