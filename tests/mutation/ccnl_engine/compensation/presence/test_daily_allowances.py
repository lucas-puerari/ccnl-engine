"""Daily presence pay, checked against the source rates in G24-G26.

The 2025 Parte Specifica PDF pp. 41-42 (SHA256
 a9ea5e4a0d7c90bd3566c2858e2bdec2561f31824fa1710aadb996dd219465de)
states G24 2.73/3.97 + 3.00 from July 2025, G25 0.26 and G26 0.21/0.26.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from ccnl_engine.period.results import PeriodResult
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _run(
    roles: frozenset[str],
    days: int | None,
    site_days: int | None = None,
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_id="trasporto-aereo-assaeroporti",
                level_code="9",
                category=WorkerCategory.OPERAIO,
                seniority=new_hire(),
                roles=roles,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(
                presence_days=days,
                site_presence_days=site_days,
                regione="IT-25",
                comune_belfiore="A005",
            ),
        )
    )


def _daily(result: PeriodResult, code: str) -> list[Decimal]:
    return [item.amount for item in result.pay_items if code in item.item_id]


@pytest.mark.parametrize("days", [20, 0])
def test_nonscheduled_and_airport_near(days: int) -> None:
    """At 20 days: 20 x 6.97 = 139.40 and 20 x 0.21 = 4.20; at 0 both 0."""
    result = _run(frozenset({"airport_within_20km"}), days, days)
    assert _daily(result, "G24_NONSHIFT_DAILY") == (
        [Decimal("6.97") * days] if days else []
    )
    assert _daily(result, "G26_NEAR_DAILY") == (
        [Decimal("0.21") * days] if days else []
    )
    assert not _daily(result, "G25_SHIFT_DAILY")
    assert not [b for b in result.blockers if "presence_days" in b.detail]


def test_rotating_shift_and_far_airport() -> None:
    """20 days: G24 114.60 + G25 5.20 + G26 5.20 = 125.00; before 0."""
    result = _run(frozenset({"rotating_shift_h16_h24", "airport_over_20km"}), 20, 20)
    assert _daily(result, "G24_SHIFT_DAILY") == [Decimal("114.60")]
    assert _daily(result, "G25_SHIFT_DAILY") == [Decimal("5.20")]
    assert _daily(result, "G26_FAR_DAILY") == [Decimal("5.20")]
    assert not _daily(result, "G24_NONSHIFT_DAILY")
    assert sum(
        (
            _daily(result, code)[0]
            for code in ("G24_SHIFT_DAILY", "G25_SHIFT_DAILY", "G26_FAR_DAILY")
        ),
        Decimal(0),
    ) == Decimal("125.00")


def test_absorbed_shift_and_missing_days() -> None:
    """Absorbed G25 pays 0; 20 x 5.73 = 114.60, missing days blocks only G24."""
    roles = frozenset({"rotating_shift_h16_h24", "shift_allowance_absorbed"})
    paid = _run(roles, 20)
    assert _daily(paid, "G24_SHIFT_DAILY") == [Decimal("114.60")]
    assert not _daily(paid, "G25_SHIFT_DAILY")
    missing = _run(roles, None)
    assert not _daily(missing, "G24_SHIFT_DAILY")
    assert any("presence_days" in b.detail for b in missing.blockers)
    assert not any("site_presence_days" in b.detail for b in missing.blockers)


def test_airport_days_need_separate_count() -> None:
    """20 workdays pay G24 139.40; without airport count G26 stays 0 and blocks."""
    result = _run(frozenset({"airport_over_20km"}), 20)
    assert _daily(result, "G24_NONSHIFT_DAILY") == [Decimal("139.40")]
    assert not _daily(result, "G26_FAR_DAILY")
    assert any("site_presence_days" in b.detail for b in result.blockers)


def test_g24_excludes_tfr_but_g25_g26_have_no_contractual_exclusion() -> None:
    """G24 20 x 5.73 = 114.60 excluded; G25/G26 5.20 each not excluded."""
    rules = {
        rule.code: rule
        for rule in load_ccnl(
            "trasporto-aereo-assaeroporti"
        ).parameters.daily_presence_allowances
    }
    assert not rules["G24_SHIFT_DAILY"].tfr_relevant
    assert not rules["G24_NONSHIFT_DAILY"].tfr_relevant
    assert rules["G25_SHIFT_DAILY"].tfr_relevant
    assert rules["G26_NEAR_DAILY"].tfr_relevant
    assert rules["G26_FAR_DAILY"].tfr_relevant


def test_conflicting_airport_distance_roles_are_invalid() -> None:
    """20 x 0.21 and 20 x 0.26 cannot both pay for the same airport."""
    with pytest.raises(InvalidInputError, match="incompatible daily presence roles"):
        _run(frozenset({"airport_within_20km", "airport_over_20km"}), 20, 20)


def test_site_days_cannot_exceed_work_days() -> None:
    """A site count of 21 cannot be paid as 21 x 0.21 for 20 workdays."""
    with pytest.raises(InvalidInputError, match="site_presence_days"):
        PeriodFacts(presence_days=20, site_presence_days=21)


def test_negative_days_are_invalid() -> None:
    """A negative count cannot be converted into negative daily earnings."""
    with pytest.raises(InvalidInputError, match="presence_days"):
        PeriodFacts(presence_days=-1)
