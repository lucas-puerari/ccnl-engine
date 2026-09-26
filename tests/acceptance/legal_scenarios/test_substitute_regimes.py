"""2026 substitute-tax regimes for renewal increments and work-time supplements.

Source: L. 199/2025 art. 1:

- c. 7: 5% substitute tax on salary increments from CCNL renewals signed
  from 1 January 2024 to 31 December 2026, for private-sector employees with
  2025 employment income not above 33,000 EUR;
- c. 10-11: 15% substitute tax on night, holiday and rest-day and shift
  supplements, up to 1,500 EUR a year, for private-sector employees with
  2025 employment income not above 40,000 EUR, excluding the activities of
  c. 18 (food and beverage service, tourism, thermal establishments); the
  excess is ordinary IRPEF.

Scenario base: Commercio L4, private sector declared on the employment,
employer activity outside c. 18, March 2026, 2025 income as stated.  The
public-sector scenarios declare a public employment: on CCNL Funzioni
Centrali and on a private CCNL applied by a public employer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ccnl_engine import (
    CalculationDecision,
    CalculationStatus,
    EmployerActivity,
    EmployerProfile,
    Employment,
    EmploymentSector,
    Headcount,
    PriorYearTaxFacts,
    SubstituteTaxRegime,
)
from ccnl_engine.events import (
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    ShiftWorkEvent,
    WorkEvent,
)
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    PA_FUNZIONI_CENTRALI,
    regular_period,
    substitute_tax,
)

if TYPE_CHECKING:
    from ccnl_engine import PayrollState, PeriodResult

pytestmark = pytest.mark.legal_scenario

_EVENT_DAY = date(2026, 3, 10)
_SIGNED_ON = date(2025, 3, 1)
_ELIGIBLE_PRIOR_INCOME = Decimal(20_000)
_PRIVATE = EmploymentSector.PRIVATE


@dataclass(frozen=True)
class _Worker:
    """Facts the regimes read, eligible unless a scenario changes one."""

    income: Decimal | None = _ELIGIBLE_PRIOR_INCOME
    waived: bool = False
    sector: EmploymentSector | None = _PRIVATE
    activity: EmployerActivity | None = EmployerActivity.OTHER
    ccnl_slug: str = COMMERCIO
    level_code: str = "4"


_ELIGIBLE = _Worker()


def _period(
    *events: WorkEvent,
    worker: _Worker = _ELIGIBLE,
    month: int = 3,
    opening: PayrollState | None = None,
) -> PeriodResult:
    waived = frozenset(SubstituteTaxRegime) if worker.waived else frozenset()
    return regular_period(
        month=month,
        events=events,
        opening_state=opening,
        employment=Employment(
            ccnl_slug=worker.ccnl_slug,
            level_code=worker.level_code,
            sector=worker.sector,
        ),
        employer=EmployerProfile(headcount=Headcount(50), activity=worker.activity),
        prior_year=PriorYearTaxFacts(
            employment_income=worker.income, waived_regimes=waived
        ),
    )


def _renewal(signed_on: date | None = _SIGNED_ON) -> BonusEvent:
    return BonusEvent(
        event_date=_EVENT_DAY,
        amount=Decimal(2_000),
        kind="contract_renewal",
        agreement_signed_on=signed_on,
    )


def _renewal_decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = (
        d for d in result.decisions if d.capability == "rinnovo_substitute_tax"
    )
    return decision


def test_renewal_increment_below_income_cap_uses_substitute_tax() -> None:
    """Renewal 2,000 EUR, prior income 20,000: 2,000 * 5% = 100.00 (c. 7)."""
    result = _period(_renewal())

    assert substitute_tax(result) == Decimal("100.00")
    assert _renewal_decision(result).reason_code == "requirements_met"
    assert result.status is CalculationStatus.FINAL


def test_renewal_increment_at_income_cap_uses_substitute_tax() -> None:
    """Prior income exactly 33,000 is "non superiore": 2,000 * 5% = 100.00."""
    result = _period(_renewal(), worker=_Worker(income=Decimal(33_000)))

    assert substitute_tax(result) == Decimal("100.00")


def test_renewal_increment_above_income_cap_is_ordinary() -> None:
    """Renewal 2,000 EUR, prior income 100,000 > 33,000: no substitute tax."""
    result = _period(_renewal(), worker=_Worker(income=Decimal(100_000)))

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "prior_income_above_ceiling"
    assert result.status is CalculationStatus.FINAL


def test_renewal_increment_in_public_sector_is_ordinary() -> None:
    """A public administration contract is not "settore privato": ordinary."""
    result = _period(_renewal(), worker=_PUBLIC_ADMINISTRATION)

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "sector_not_eligible"


def test_renewal_increment_waived_in_writing_is_ordinary() -> None:
    """A written waiver ("salva espressa rinuncia scritta") keeps ordinary IRPEF."""
    result = _period(_renewal(), worker=_Worker(waived=True))

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "waived_by_worker"


def test_renewal_increment_with_unknown_income_is_ordinary_and_provisional() -> None:
    """Unknown 2025 income: ordinary IRPEF and a provisional result."""
    result = _period(_renewal(), worker=_Worker(income=None))

    assert substitute_tax(result) == Decimal(0)
    assert result.status is CalculationStatus.PROVISIONAL
    assert [issue.code for issue in result.issues] == ["rinnovo_eligibility_unknown"]


_PUBLIC_ADMINISTRATION = _Worker(
    sector=EmploymentSector.PUBLIC,
    ccnl_slug=PA_FUNZIONI_CENTRALI,
    level_code="ASSISTENTI",
)


def test_renewal_by_public_employer_on_private_ccnl_is_ordinary() -> None:
    """The sector is the employer's: a private CCNL does not make it private."""
    result = _period(_renewal(), worker=_Worker(sector=EmploymentSector.PUBLIC))

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "sector_not_eligible"


def test_renewal_with_unknown_sector_is_ordinary_and_provisional() -> None:
    """The sector is not derived from the CCNL: unknown makes it provisional."""
    result = _period(_renewal(), worker=_Worker(sector=None))

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "sector_unknown"
    assert result.status is CalculationStatus.PROVISIONAL


@pytest.mark.parametrize("signed_on", [date(2023, 12, 31), date(2027, 1, 1)])
def test_renewal_signed_outside_the_window_is_ordinary(signed_on: date) -> None:
    """Only renewals "sottoscritti dal 1 gennaio 2024 al 31 dicembre 2026"."""
    result = _period(_renewal(signed_on))

    assert substitute_tax(result) == Decimal(0)
    decision = _renewal_decision(result)
    assert decision.reason_code == "agreement_signed_outside_window"
    assert decision.inputs["agreement_signed_on"] == signed_on.isoformat()
    assert result.status is CalculationStatus.FINAL


def test_renewal_signed_on_window_bounds_uses_substitute_tax() -> None:
    """Both bounds of the window qualify: 2,000 * 5% = 100.00 each."""
    first = _period(_renewal(date(2024, 1, 1)))
    last = _period(_renewal(date(2026, 12, 31)))

    assert substitute_tax(first) == substitute_tax(last) == Decimal("100.00")


def test_renewal_with_unknown_signing_date_is_ordinary_and_provisional() -> None:
    """Without the signing date the window cannot be checked: provisional."""
    result = _period(_renewal(None))

    assert substitute_tax(result) == Decimal(0)
    assert _renewal_decision(result).reason_code == "agreement_signing_date_unknown"
    assert result.status is CalculationStatus.PROVISIONAL


_WORK_TIME = "notte_festivi_turni_substitute_tax"
_CAP = Decimal(1_500)
_RATE = Decimal("0.15")


def _night(amount: Decimal, *, day: date = _EVENT_DAY) -> NightShiftEvent:
    return NightShiftEvent(event_date=day, supplement_amount=amount)


def _work_time_decisions(result: PeriodResult) -> list[CalculationDecision]:
    return [d for d in result.decisions if d.capability == _WORK_TIME]


def _taxable(result: PeriodResult) -> Decimal:
    return result.closing_state.ytd.earnings.taxable


def test_night_supplement_above_annual_cap_splits_regime() -> None:
    """Night supplement 2,000 EUR: 1,500 * 15% = 225.00, 500 stays ordinary."""
    result = _period(_night(Decimal(2_000)))

    assert substitute_tax(result) == Decimal("225.00")
    (decision,) = _work_time_decisions(result)
    assert decision.reason_code == "requirements_met"
    assert decision.inputs["eligible_amount"] == _CAP
    assert decision.inputs["ordinary_amount"] == Decimal(500)
    assert result.closing_state.ytd.work_time_regime.used == _CAP
    assert result.status is CalculationStatus.FINAL


def test_holiday_supplement_uses_substitute_tax() -> None:
    """Holiday supplement 500 EUR, eligible income: 500 * 15% = 75.00."""
    event = HolidayWorkEvent(event_date=_EVENT_DAY, supplement_amount=Decimal(500))
    result = _period(event)

    assert substitute_tax(result) == Decimal("75.00")
    assert result.closing_state.ytd.work_time_regime.used == Decimal(500)


def test_shift_allowance_uses_substitute_tax() -> None:
    """Shift allowance 300 EUR (indennita di turno, c. 10 lett. c): 45.00."""
    event = ShiftWorkEvent(event_date=_EVENT_DAY, supplement_amount=Decimal(300))
    result = _period(event)

    assert substitute_tax(result) == Decimal("45.00")


def test_work_time_supplement_at_income_ceiling_uses_substitute_tax() -> None:
    """Prior income exactly 40,000 is "non superiore": 500 * 15% = 75.00."""
    result = _period(_night(Decimal(500)), worker=_Worker(income=Decimal(40_000)))

    assert substitute_tax(result) == Decimal("75.00")


def test_work_time_supplement_above_income_ceiling_is_ordinary() -> None:
    """Prior income 40,000.01 > 40,000: ordinary, and no cap is consumed."""
    worker = _Worker(income=Decimal("40000.01"))
    result = _period(_night(Decimal(500)), worker=worker)

    assert substitute_tax(result) == Decimal(0)
    (decision,) = _work_time_decisions(result)
    assert decision.reason_code == "prior_income_above_ceiling"
    assert result.closing_state.ytd.work_time_regime.used == Decimal(0)


def test_work_time_supplement_waived_in_writing_is_ordinary() -> None:
    """A written waiver keeps the supplement ordinary."""
    result = _period(_night(Decimal(500)), worker=_Worker(waived=True))

    assert substitute_tax(result) == Decimal(0)
    (decision,) = _work_time_decisions(result)
    assert decision.reason_code == "waived_by_worker"


def test_work_time_supplement_in_public_sector_is_ordinary() -> None:
    """Only "sostituti d'imposta del settore privato" apply the regime (c. 11)."""
    result = _period(_night(Decimal(500)), worker=_PUBLIC_ADMINISTRATION)

    assert substitute_tax(result) == Decimal(0)
    (decision,) = _work_time_decisions(result)
    assert decision.reason_code == "sector_not_eligible"


def test_work_time_supplement_by_public_employer_on_private_ccnl_is_ordinary() -> None:
    """A public employer applying a private CCNL is not a private withholder."""
    worker = _Worker(sector=EmploymentSector.PUBLIC)
    result = _period(_night(Decimal(500)), worker=worker)

    (decision,) = _work_time_decisions(result)
    assert decision.reason_code == "sector_not_eligible"
    assert substitute_tax(result) == Decimal(0)


@pytest.mark.parametrize(
    "activity",
    [
        EmployerActivity.FOOD_AND_BEVERAGE_SERVICE,
        EmployerActivity.TOURISM,
        EmployerActivity.THERMAL_ESTABLISHMENT,
    ],
)
def test_work_time_supplement_in_comma_18_activity_is_ordinary(
    activity: EmployerActivity,
) -> None:
    """C. 11 excludes the activities of c. 18: ordinary IRPEF, final."""
    result = _period(_night(Decimal(500)), worker=_Worker(activity=activity))

    (decision,) = _work_time_decisions(result)
    assert decision.reason_code == "employer_activity_excluded"
    assert decision.inputs["employer_activity"] == activity.value
    assert substitute_tax(result) == Decimal(0)
    assert result.status is CalculationStatus.FINAL
    assert result.closing_state.ytd.work_time_regime.used == Decimal(0)


def test_work_time_supplement_with_unknown_activity_is_provisional() -> None:
    """The exclusion needs the employer activity: unknown is provisional."""
    result = _period(_night(Decimal(500)), worker=_Worker(activity=None))

    (decision,) = _work_time_decisions(result)
    assert decision.reason_code == "activity_unknown"
    assert substitute_tax(result) == Decimal(0)
    assert result.status is CalculationStatus.PROVISIONAL


def test_work_time_supplement_with_unknown_income_is_provisional() -> None:
    """Unknown 2025 income: ordinary IRPEF and a provisional result."""
    result = _period(_night(Decimal(500)), worker=_Worker(income=None))

    assert substitute_tax(result) == Decimal(0)
    assert result.status is CalculationStatus.PROVISIONAL
    assert [issue.code for issue in result.issues] == [
        "notte_festivi_turni_eligibility_unknown"
    ]
    assert result.closing_state.ytd.work_time_regime.used == Decimal(0)


def test_annual_cap_is_shared_by_supplements_of_one_run() -> None:
    """Night 1,000 and holiday 1,000 in one run share one 1,500 EUR cap."""
    holiday = HolidayWorkEvent(event_date=_EVENT_DAY, supplement_amount=Decimal(1_000))
    result = _period(_night(Decimal(1_000)), holiday)

    assert substitute_tax(result) == Decimal("225.00")
    first, second = _work_time_decisions(result)
    assert first.inputs["eligible_amount"] == Decimal(1_000)
    assert second.inputs["cap_available"] == Decimal(500)
    assert second.inputs["eligible_amount"] == Decimal(500)
    assert second.inputs["ordinary_amount"] == Decimal(500)


def _month(month: int, amount: Decimal, opening: PayrollState | None) -> PeriodResult:
    event = _night(amount, day=date(2026, month, 10))
    return _period(event, month=month, opening=opening)


def test_annual_cap_is_consumed_across_runs() -> None:
    """March 1,000 (150.00), April 1,000 (500 at 15% = 75.00), May 1,000 (0)."""
    march = _month(3, Decimal(1_000), None)
    april = _month(4, Decimal(1_000), march.closing_state)
    may = _month(5, Decimal(1_000), april.closing_state)

    assert substitute_tax(march) == Decimal("150.00")
    assert substitute_tax(april) == Decimal("75.00")
    assert substitute_tax(may) == Decimal(0)
    assert march.closing_state.ytd.work_time_regime.used == Decimal(1_000)
    assert april.closing_state.ytd.work_time_regime.used == _CAP
    assert may.closing_state.ytd.work_time_regime.used == _CAP
    (april_decision,) = _work_time_decisions(april)
    assert april_decision.inputs["ordinary_amount"] == Decimal(500)
    (may_decision,) = _work_time_decisions(may)
    assert may_decision.reason_code == "requirements_met"
    assert may_decision.inputs["ordinary_amount"] == Decimal(1_000)


_AMOUNTS = st.decimals(
    min_value=Decimal(1), max_value=Decimal(3_000), places=2, allow_nan=False
)


def _split(result: PeriodResult) -> tuple[Decimal, Decimal]:
    (decision,) = _work_time_decisions(result)
    return (
        Decimal(decision.inputs["eligible_amount"]),
        Decimal(decision.inputs["ordinary_amount"]),
    )


def _capped_tax(amount: Decimal) -> Decimal:
    return (min(amount, _CAP) * _RATE).quantize(Decimal("0.01"), ROUND_HALF_UP)


@given(amount=_AMOUNTS, extra=_AMOUNTS)
@settings(max_examples=15)
def test_beyond_the_cap_only_the_excess_changes_regime(
    amount: Decimal, extra: Decimal
) -> None:
    """Raising a supplement moves only the part above 1,500 EUR to ordinary.

    The substitute tax is 15% of ``min(amount, 1,500)``.  Raising the amount
    by ``extra`` adds to the ordinary part exactly what lies above the cap,
    and leaves the substitute tax unchanged once the cap is reached.
    """
    low = _period(_night(amount))
    high = _period(_night(amount + extra))
    low_eligible, low_ordinary = _split(low)
    high_eligible, high_ordinary = _split(high)

    assert substitute_tax(low) == _capped_tax(amount)
    assert substitute_tax(high) == _capped_tax(amount + extra)
    assert low_eligible + low_ordinary == amount
    assert high_eligible + high_ordinary == amount + extra
    zero = Decimal(0)
    excess_increase = max(amount + extra - _CAP, zero) - max(amount - _CAP, zero)
    assert high_ordinary - low_ordinary == excess_increase
    if amount >= _CAP:
        assert substitute_tax(high) == substitute_tax(low)
        assert _taxable(high) > _taxable(low)
