"""Issues of a cumulated sick-pay treatment: one per fact or rule that matters."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.decision.models import CalculationStatus, IssueCause
from ccnl_engine.sickness.cumulation.handlers import (
    BAND_CHANGES,
    EXEMPTION_UNKNOWN,
    FIXED_TERM,
    HISTORY_UNKNOWN,
    HOSPITAL_STAY,
    HOSPITAL_STAY_UNKNOWN,
    SENIORITY_UNKNOWN,
    SERIOUS_ILLNESS_UNKNOWN,
    cumulation_inputs,
    cumulation_issues,
    year_issues,
)
from ccnl_engine.sickness.cumulation.results import CumulationReport
from ccnl_engine.sickness.integration.models import SicknessSeniorityBand
from ccnl_engine.sickness.models import SicknessEpisode
from ccnl_engine.sickness.term.rules import SicknessTerms

if TYPE_CHECKING:
    from ccnl_engine.sickness.cumulation.year.rules import YearTreatment

_EPISODE = SicknessEpisode("a", date(2026, 3, 2), date(2026, 3, 13))
_QUIET = CumulationReport(
    band=SicknessSeniorityBand(
        seniority_months_from=0, full_pay_days=122, comporto_days=183
    ),
    chain_days=12,
    window_days=40,
    reduced=False,
    seniority_reach=False,
    band_changes=False,
    history_reach=False,
    exemption_reach=False,
)


def test_a_report_without_doubt_raises_nothing() -> None:
    """Known facts and a permanent contract: no issue."""
    assert cumulation_issues(_EPISODE, _QUIET, SicknessTerms()) == ()


@pytest.mark.parametrize(
    ("flag", "code", "fact"),
    [
        ("history_reach", HISTORY_UNKNOWN, "sickness_known_from"),
        ("seniority_reach", SENIORITY_UNKNOWN, "seniority"),
        ("exemption_reach", EXEMPTION_UNKNOWN, "short_absence_exempt"),
        ("band_changes", BAND_CHANGES, None),
        ("reduced", HOSPITAL_STAY, None),
    ],
)
def test_each_doubt_is_a_provisional_issue(
    flag: str, code: str, fact: str | None
) -> None:
    """A fact names the public field that settles it."""
    report = replace(_QUIET, **{flag: True})  # type: ignore[arg-type]
    (issue,) = cumulation_issues(_EPISODE, report, SicknessTerms())
    assert (issue.code, issue.fact, issue.status, issue.capability) == (
        code,
        fact,
        CalculationStatus.PROVISIONAL,
        "sickness",
    )
    assert issue.message.startswith("sickness episode 'a': ")


def test_a_fixed_term_contract_is_not_scaled() -> None:
    """The CCNL scales the periods of a fixed-term contract."""
    (issue,) = cumulation_issues(_EPISODE, _QUIET, SicknessTerms(fixed_term=True))
    assert issue.code == FIXED_TERM


def test_the_decision_records_the_band_and_the_counts() -> None:
    """Band, chain and window counts on the last day paid."""
    assert cumulation_inputs(_QUIET) == {
        "band_seniority_months_from": Decimal(0),
        "band_full_pay_days": Decimal(122),
        "band_comporto_days": Decimal(183),
        "chain_days": Decimal(12),
        "window_days": Decimal(40),
    }


@pytest.mark.parametrize(
    ("flag", "code", "fact"),
    [
        ("history_reach", HISTORY_UNKNOWN, "sickness_known_from"),
        ("seniority_reach", SENIORITY_UNKNOWN, "seniority"),
        ("exemption_reach", EXEMPTION_UNKNOWN, "short_absence_exempt"),
    ],
)
def test_each_doubt_of_a_year_count_is_a_missing_fact(
    flag: str, code: str, fact: str
) -> None:
    """A count over the year or a window names the field that settles it."""
    flags = dict.fromkeys(
        ("history_reach", "seniority_reach", "exemption_reach"), False
    )
    year = cast("YearTreatment", SimpleNamespace(**{**flags, flag: True}))

    (issue,) = year_issues(_EPISODE, year)
    assert (issue.code, issue.fact, issue.status, issue.capability) == (
        code,
        fact,
        CalculationStatus.PROVISIONAL,
        "sickness",
    )
    assert issue.message.startswith("sickness episode 'a': ")


def _ccnl_terms(*, serious: bool, hospital: bool) -> SicknessTerms:
    cumulation = SimpleNamespace(
        serious_illness=object() if serious else None,
        hospital_stay=object() if hospital else None,
    )
    rules = SimpleNamespace(ccnl=SimpleNamespace(cumulation=cumulation))
    return SicknessTerms(rules=rules)  # type: ignore[arg-type]


_REDUCED = replace(_QUIET, reduced=True)


@pytest.mark.parametrize(
    ("serious", "hospital", "stated", "codes"),
    [
        (True, True, False, [SERIOUS_ILLNESS_UNKNOWN, HOSPITAL_STAY_UNKNOWN]),
        (True, True, True, []),
        (False, False, False, [HOSPITAL_STAY]),
    ],
)
def test_reduced_days_ask_for_what_the_ccnl_pays_in_full(
    serious: bool, hospital: bool, stated: bool, codes: list[str]
) -> None:
    """A serious illness and the hospital stays, when the CCNL pays them."""
    episode = (
        replace(_EPISODE, serious_illness=False, hospital_stays=())
        if stated
        else _EPISODE
    )
    issues = cumulation_issues(
        episode, _REDUCED, _ccnl_terms(serious=serious, hospital=hospital)
    )

    assert [i.code for i in issues] == codes
    assert {i.capability for i in issues} <= {"sickness"}
    facts = {i.code: i.fact for i in issues}
    assert facts.get(SERIOUS_ILLNESS_UNKNOWN, "serious_illness") == "serious_illness"
    assert facts.get(HOSPITAL_STAY_UNKNOWN, "hospital_stays") == "hospital_stays"
    assert all(i.cause is IssueCause.RULE for i in issues if i.fact is None)


def test_reduced_days_of_a_ccnl_without_those_rules_ask_nothing() -> None:
    """No serious-illness rule: no question about it, even if not stated."""
    issues = cumulation_issues(
        _EPISODE, _REDUCED, _ccnl_terms(serious=False, hospital=True)
    )

    assert [i.code for i in issues] == [HOSPITAL_STAY_UNKNOWN]
