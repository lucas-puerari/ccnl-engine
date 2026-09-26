"""2026 substitute-tax regimes for renewal increments and work-time supplements.

Source: L. 199/2025 art. 1:

- c. 7: 5% substitute tax on salary increments from CCNL renewals, for
  private-sector employees with 2025 employment income not above 33,000 EUR;
- c. 10-11: 15% substitute tax on night, holiday and rest-day and shift
  supplements, up to 1,500 EUR a year, for private-sector employees with
  2025 employment income not above 40,000 EUR; the excess is ordinary IRPEF.

Scenario base: Commercio L4, March 2026, prior-year income as stated.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.events import BonusEvent, HolidayWorkEvent, NightShiftEvent
from tests.acceptance.legal_scenarios._support import regular_period, substitute_tax

pytestmark = pytest.mark.legal_scenario

_EVENT_DAY = date(2026, 3, 10)
_ELIGIBLE_PRIOR_INCOME = Decimal(20_000)


def _renewal(prior_income: Decimal) -> BonusEvent:
    return BonusEvent(
        event_date=_EVENT_DAY,
        amount=Decimal(2_000),
        kind="contract_renewal",
        prior_income=prior_income,
    )


def test_renewal_increment_below_income_cap_uses_substitute_tax() -> None:
    """Renewal 2,000 EUR, prior income 20,000: 2,000 * 5% = 100.00 (c. 7)."""
    result = regular_period(month=3, events=(_renewal(_ELIGIBLE_PRIOR_INCOME),))

    assert substitute_tax(result) == Decimal("100.00")


@pytest.mark.xfail(
    strict=True,
    reason="renewal substitute tax ignores the prior-year income cap",
)
def test_renewal_increment_above_income_cap_is_ordinary() -> None:
    """Renewal 2,000 EUR, prior income 100,000 > 33,000: no substitute tax.

    Observed on 26 September 2026: substitute tax 100.00.
    """
    result = regular_period(month=3, events=(_renewal(Decimal(100_000)),))

    assert substitute_tax(result) == Decimal(0)


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
