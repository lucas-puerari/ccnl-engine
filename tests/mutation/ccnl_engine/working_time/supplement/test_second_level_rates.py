"""Supplement rates of the employer's agreement, stated once.

Università ARAN art. 26 c. 6 leaves the night supplement to the integrative
agreement: an employer that states 3.00 an hour has 8 night hours priced at
24.00 without the event stating the amount.  A rate of the employer for a
work the CCNL prices replaces the CCNL band (Commercio night at 30%).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.compensation.second_level.inputs import SecondLevelAgreement
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.event.facade import NightShiftEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.supplement.employer.inputs import (
    RateUnit,
    SecondLevelRate,
    check_second_level_rates,
)
from ccnl_engine.working_time.supplement.models import SupplementWork

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationDecision

_DAY = date(2026, 3, 11)
_NIGHT = NightShiftEvent(_DAY, hours=Decimal(8))


def _rate(**changes: object) -> SecondLevelRate:
    fields: dict[str, object] = {
        "work": SupplementWork.NIGHT,
        "rate": Decimal(3),
        "unit": RateUnit.PER_HOUR,
        "agreement": SecondLevelAgreement.COMPANY,
        "valid_from": date(2026, 1, 1),
        **changes,
    }
    return SecondLevelRate(**fields)  # type: ignore[arg-type]


def _night(ccnl: str, level: str, *rates: SecondLevelRate) -> CalculationDecision:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50), second_level_rates=rates),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=ccnl,
            level_code=level,
            opening_state=PeriodState.zero(),
            events=(_NIGHT,),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "night_work" and d.reason_code == "ccnl_supplement_applied"
    )
    return decision


def test_the_employer_rate_prices_a_delegated_supplement() -> None:
    """8 night hours at the 3.00 of the agreement: 24.00."""
    decision = _night("universita-aran", "COLLABORATORE", _rate())
    assert decision.amount == Decimal("24.00")
    assert decision.inputs["band_code"] == "EMPLOYER_NIGHT"


def test_without_the_rate_the_delegated_supplement_is_not_priced() -> None:
    """No CCNL band and no employer rate: the event must state the amount."""
    with pytest.raises((MissingRuleError, InvalidInputError)):
        _night("universita-aran", "COLLABORATORE")


def test_the_employer_rate_replaces_the_ccnl_band() -> None:
    """A company 30% in place of the CCNL night band of Commercio."""
    ccnl = _night("commercio-confcommercio", "4")
    company = _night(
        "commercio-confcommercio",
        "4",
        _rate(rate=Decimal("0.30"), unit=RateUnit.PERCENTAGE),
    )
    assert company.inputs["band_code"] == "EMPLOYER_NIGHT"
    assert company.inputs["band_supplement"] == Decimal("0.30")
    assert ccnl.inputs["band_code"] != "EMPLOYER_NIGHT"
    assert company.amount != ccnl.amount


def test_a_rate_out_of_force_or_of_another_level_leaves_the_ccnl_band() -> None:
    """Expired, future or reserved to another level: the CCNL band stays."""
    for rate in (
        _rate(valid_until=date(2026, 2, 28)),
        _rate(valid_from=date(2026, 4, 1)),
        _rate(levels=("1",)),
    ):
        decision = _night("commercio-confcommercio", "4", rate)
        assert decision.inputs["band_code"] != "EMPLOYER_NIGHT"


def test_a_shift_rate_is_paid_by_the_turn() -> None:
    """The unit names how the band is paid."""
    rate = _rate(unit=RateUnit.PER_SHIFT, work=SupplementWork.NIGHT_SHIFT)
    assert rate.unit is RateUnit.PER_SHIFT
    assert rate.applies_to("4", _DAY)


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"rate": Decimal(0)}, "rate"),
        ({"valid_until": date(2025, 12, 31)}, "valid_until"),
        ({"levels": "4"}, "levels"),
        ({"levels": ("",)}, "levels"),
        ({"work": "lunch"}, "work"),
        ({"hours_paid_apart": "no"}, "hours_paid_apart"),
    ],
)
def test_invalid_rates_are_rejected(changes: dict[str, object], field: str) -> None:
    """Each field is checked."""
    with pytest.raises(InvalidInputError, match=field):
        _rate(**changes)


def test_two_rates_of_the_same_work_are_rejected() -> None:
    """One rate for a work, its levels and its start."""
    with pytest.raises(InvalidInputError, match="same work"):
        check_second_level_rates((_rate(), _rate()), "rates")
    with pytest.raises(InvalidInputError, match="SecondLevelRate"):
        check_second_level_rates("rate", "rates")
    with pytest.raises(InvalidInputError):
        check_second_level_rates(("rate",), "rates")
    assert check_second_level_rates([_rate()], "rates") == (_rate(),)
