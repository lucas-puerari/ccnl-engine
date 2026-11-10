"""Art. 61(c), cached PDF p. 91: daily rotation rates on actual service days."""

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


def _run(roles: frozenset[str], days: int | None = 20) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_id="sanita-privata-aiop-aris",
                level_code="D",
                category=WorkerCategory.OPERAIO,
                seniority=new_hire(),
                roles=roles,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(
                presence_days=days, regione="IT-25", comune_belfiore="A005"
            ),
        )
    )


def _rotation(result: PeriodResult) -> dict[str, Decimal]:
    return {
        code: sum(
            (item.amount for item in result.pay_items if code in item.item_id),
            Decimal(0),
        )
        for code in (
            "ROTATION_THREE_AUX_DAILY",
            "ROTATION_THREE_HEALTH_TECH_DAILY",
            "ROTATION_TWO_DAILY",
        )
    }


@pytest.mark.parametrize(
    ("roles", "expected"),
    [
        (
            frozenset({"three_shift_diagnosis_care_rehab_specialized_auxiliary"}),
            (Decimal("90.00"), Decimal(0), Decimal(0)),
        ),
        (
            frozenset({"three_shift_diagnosis_care_rehab_health_technical_b_c_d_ds"}),
            (Decimal(0), Decimal("90.00"), Decimal(0)),
        ),
        (
            frozenset({"two_shift_scheduled_operator_a_ds"}),
            (Decimal(0), Decimal(0), Decimal("41.20")),
        ),
        (frozenset(), (Decimal(0), Decimal(0), Decimal(0))),
    ],
)
def test_twenty_service_days(
    roles: frozenset[str], expected: tuple[Decimal, ...]
) -> None:
    """Before: 0; after: 20 x 4.50 = 90.00 or 20 x 2.06 = 41.20; neither = 0."""
    assert tuple(_rotation(_run(roles)).values()) == expected


def test_art_four_effective_date() -> None:
    """The 8 October 2020 signing gives no daily rate before 9 October 2020."""
    rules = load_ccnl("sanita-privata-aiop-aris").parameters.daily_presence_allowances
    assert len(rules) == 3
    for rule in rules:
        assert not rule.rate.applies_on(date(2020, 10, 8))
        assert rule.rate.applies_on(date(2020, 10, 9))


def test_both_rotation_brackets_rejected() -> None:
    """20 x 4.50 and 20 x 2.06 cannot both be paid (not 131.20)."""
    with pytest.raises(InvalidInputError, match="incompatible daily presence roles"):
        _run(
            frozenset({
                "three_shift_diagnosis_care_rehab_specialized_auxiliary",
                "two_shift_scheduled_operator_a_ds",
            })
        )


def test_no_days_does_not_infer_days_from_rotation_role() -> None:
    """Without a count, even a three-shift role pays 0, not 20 x 4.50 = 90.00."""
    result = _run(
        frozenset({"three_shift_diagnosis_care_rehab_specialized_auxiliary"}), None
    )
    assert all(amount == 0 for amount in _rotation(result).values())
    assert any("presence_days" in blocker.detail for blocker in result.blockers)
