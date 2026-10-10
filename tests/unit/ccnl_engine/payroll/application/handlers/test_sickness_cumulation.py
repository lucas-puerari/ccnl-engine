"""Issues of a cumulated sick-pay treatment: one per fact or rule that matters."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.sickness.models import SicknessSeniorityBand
from ccnl_engine.payroll.application.handlers._sickness_cumulation import (
    BAND_CHANGES,
    EXEMPTION_UNKNOWN,
    FIXED_TERM,
    HISTORY_UNKNOWN,
    HOSPITAL_STAY,
    SENIORITY_UNKNOWN,
    cumulation_inputs,
    cumulation_issues,
)
from ccnl_engine.payroll.application.handlers._sickness_terms import SicknessTerms
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.sick_cumulation_report import CumulationReport
from ccnl_engine.payroll.domain.sickness import SicknessEpisode

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
    assert (issue.code, issue.fact, issue.status) == (
        code,
        fact,
        CalculationStatus.PROVISIONAL,
    )


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
