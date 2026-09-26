"""2026 substitute-tax regimes for renewal increments and work-time supplements.

Source: L. 199/2025 art. 1:

- c. 7: 5% substitute tax on salary increments from CCNL renewals, for
  private-sector employees with 2025 employment income not above 33,000 EUR;
- c. 10-11: 15% substitute tax on night, holiday and rest-day and shift
  supplements, up to 1,500 EUR a year, for private-sector employees with
  2025 employment income not above 40,000 EUR; the excess is ordinary IRPEF.

Scenario base: Commercio L4 (private sector), March 2026, prior-year income
as stated.  The public-sector scenario uses CCNL Funzioni Centrali.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine import CalculationDecision, CalculationStatus
from ccnl_engine.events import BonusEvent, HolidayWorkEvent, NightShiftEvent
from tests.acceptance.legal_scenarios._support import (
    PA_FUNZIONI_CENTRALI,
    regular_period,
    substitute_tax,
)

if TYPE_CHECKING:
    from ccnl_engine import PayrollResult

pytestmark = pytest.mark.legal_scenario

_EVENT_DAY = date(2026, 3, 10)
_ELIGIBLE_PRIOR_INCOME = Decimal(20_000)


def _renewal(prior_income: Decimal | None, *, waived: bool = False) -> BonusEvent:
    return BonusEvent(
        event_date=_EVENT_DAY,
        amount=Decimal(2_000),
        kind="contract_renewal",
        prior_income=prior_income,
        substitute_tax_waived=waived,
    )


def _renewal_decision(result: PayrollResult) -> CalculationDecision:
    (decision,) = (
        d for d in result.decisions if d.capability == "rinnovo_substitute_tax"
    )
    return decision


def test_renewal_increment_below_income_cap_uses_substitute_tax() -> None:
    """Renewal 2,000 EUR, prior income 20,000: 2,000 * 5% = 100.00 (c. 7)."""
    result = regular_period(month=3, events=(_renewal(_ELIGIBLE_PRIOR_INCOME),))

    assert substitute_tax(result) == Decimal("100.00")
    assert _renewal_decision(result).reason_code == "requirements_met"
    assert result.status is CalculationStatus.FINAL


def test_renewal_increment_at_income_cap_uses_substitute_tax() -> None:
    """Prior income exactly 33,000 is "non superiore": 2,000 * 5% = 100.00."""
    result = regular_period(month=3, events=(_renewal(Decimal(33_000)),))

    assert substitute_tax(result) == Decimal("100.00")


def test_renewal_increment_above_income_cap_is_ordinary() -> None:
    """Renewal 2,000 EUR, prior income 100,000 > 33,000: no substitute tax."""
    result = regular_period(month=3, events=(_renewal(Decimal(100_000)),))

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "prior_income_above_ceiling"
    assert result.status is CalculationStatus.FINAL


def test_renewal_increment_in_public_sector_is_ordinary() -> None:
    """A public administration contract is not "settore privato": ordinary."""
    result = regular_period(
        ccnl_slug=PA_FUNZIONI_CENTRALI,
        level_code="ASSISTENTI",
        month=3,
        events=(_renewal(_ELIGIBLE_PRIOR_INCOME),),
    )

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "sector_not_eligible"


def test_renewal_increment_waived_in_writing_is_ordinary() -> None:
    """A written waiver ("salva espressa rinuncia scritta") keeps ordinary IRPEF."""
    events = (_renewal(_ELIGIBLE_PRIOR_INCOME, waived=True),)
    result = regular_period(month=3, events=events)

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "waived_by_worker"


def test_renewal_increment_with_unknown_income_is_ordinary_and_provisional() -> None:
    """Unknown 2025 income: ordinary IRPEF and a provisional result."""
    result = regular_period(month=3, events=(_renewal(None),))

    assert substitute_tax(result) == Decimal(0)
    assert result.status is CalculationStatus.PROVISIONAL
    assert [issue.code for issue in result.issues] == ["rinnovo_eligibility_unknown"]


@pytest.mark.xfail(
    strict=True,
    reason="night supplement substitute tax has no annual 1500 euro cap",
)
def test_night_supplement_above_annual_cap_splits_regime() -> None:
    """Night supplement 2,000 EUR: 1,500 * 15% = 225.00, 500 stays ordinary.

    Observed on 26 September 2026: substitute tax 300.00 on the whole 2,000.
    """
    event = NightShiftEvent(
        event_date=_EVENT_DAY,
        supplement_amount=Decimal(2_000),
        prior_income=_ELIGIBLE_PRIOR_INCOME,
    )
    result = regular_period(month=3, events=(event,))

    assert substitute_tax(result) == Decimal("225.00")


@pytest.mark.xfail(
    strict=True,
    reason="holiday work supplements are not eligible for the 15 percent regime",
)
def test_holiday_supplement_uses_substitute_tax() -> None:
    """Holiday supplement 500 EUR, eligible income: 500 * 15% = 75.00.

    Eligibility needs the prior-year income, as for night work, so the event
    is built with ``prior_income``.  Unknown income must stay ordinary.

    Observed on 26 September 2026: ``HolidayWorkEvent`` has no
    ``prior_income`` field; without it the run posts no substitute tax.
    """
    eligibility: dict[str, Any] = {"prior_income": _ELIGIBLE_PRIOR_INCOME}
    event = HolidayWorkEvent(
        event_date=_EVENT_DAY, supplement_amount=Decimal(500), **eligibility
    )
    result = regular_period(month=3, events=(event,))

    assert substitute_tax(result) == Decimal("75.00")
