"""The permits of a year not taken: paid at its end or at the deadline (art. 158).

Commercio art. 158 (testo unico 2019, p. 156): "I permessi non fruiti entro
l'anno di maturazione decadranno e saranno pagati con la retribuzione di
fatto [...] in atto al momento della scadenza, oppure potranno essere fruiti
in epoca successiva e comunque non oltre il 30 giugno dell'anno successivo".
A hire of 1 January 2026 accrues no ROL for two years (the new-hire ramp)
and 32 hours of ex festività in 2026, 352 twelfths by the end of November.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.leave.balance.models import LeaveAccount, LeaveBalance
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_EX = LeaveBucket.EX_FESTIVITA


def _run(
    carryover: bool | None,
    period: PeriodId,
    *balances: LeaveBalance,
    slug: str = "commercio-confcommercio",
    level: str = "4",
) -> PeriodResult:
    opening = PeriodState.zero()
    opening = replace(
        opening, accrual=replace(opening.accrual, leave=LeaveAccount(balances))
    )
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(10), permit_carryover=carryover
            ),
            period_id=period,
            payment_date=date(period.year, period.month, 27),
            ccnl_id=slug,
            level_code=level,
            opening_state=opening,
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2026, 1, 1)),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


def _paid(result: PeriodResult) -> dict[str, Decimal]:
    return {
        i.item_id.split("_")[1]: i.quantity
        for i in result.pay_items
        if i.item_id.startswith("leave_")
    }


def _balance(result: PeriodResult, year: int) -> LeaveBalance:
    (balance,) = [
        b
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is _EX and b.year == year
    ]
    return balance


_NOVEMBER = LeaveBalance(_EX, 2026, Decimal(352), Decimal(0))


def test_paid_with_the_december_pay() -> None:
    """December accrues the last twelfth and pays the 32 hours of 2026."""
    december = _run(False, PeriodId(2026, 12), _NOVEMBER)

    assert _paid(december) == {"ex": Decimal(32)}
    assert _balance(december, 2026).settled
    (decision,) = [d for d in december.decisions if d.capability == "leave"]
    assert decision.rule.endswith("work_rules.leave_rules.permit_deadline")
    assert decision.source is not None
    assert decision.source.page == "156"
    assert decision.amount == sum(
        (i.amount for i in december.pay_items if i.item_id.startswith("leave_")),
        Decimal(0),
    )
    (item,) = [i for i in december.pay_items if i.item_id.startswith("leave_")]
    assert "at the deadline" in str(item.source)


@pytest.mark.parametrize("carryover", [True, None])
def test_december_pays_nothing_unless_the_year_ends_the_permits(
    carryover: bool | None,
) -> None:
    """Carried, or with the choice unknown, the December pay holds no permit."""
    december = _run(carryover, PeriodId(2026, 12), _NOVEMBER)

    assert not _paid(december)
    assert not _balance(december, 2026).settled


def test_carried_and_paid_with_the_june_pay() -> None:
    """Carried: the 2026 hours left after those taken by June are paid in June."""
    june = _run(
        True, PeriodId(2027, 6), LeaveBalance(_EX, 2026, Decimal(384), Decimal(120))
    )

    assert _paid(june) == {"ex": Decimal(22)}
    assert _balance(june, 2026).settled
    assert not _balance(june, 2027).settled


def test_an_unknown_choice_names_the_fact() -> None:
    """The run of December asks for EmployerProfile.permit_carryover."""
    december = _run(None, PeriodId(2026, 12), _NOVEMBER)

    assert "permit_carryover" in {b.detail for b in december.blockers}
    assert "permit_carryover" not in {
        b.detail for b in _run(None, PeriodId(2026, 11)).blockers
    }


_PULIZIA = "pulizia-artigianato-confartigianato"


@pytest.mark.parametrize(
    ("period", "paid"),
    [(PeriodId(2026, 12), {}), (PeriodId(2027, 9), {"ex": Decimal(32)})],
)
def test_pulizia_carries_the_ex_festivita_to_september(
    period: PeriodId, paid: dict[str, Decimal]
) -> None:
    """Art. 23: used by 30 September of the next year, else paid; no choice.

    Without the employer's choice the 2026 hours are kept in December and
    paid with the September 2027 pay.
    """
    hours = Decimal(352) if period.year == 2026 else Decimal(384)
    result = _run(
        None,
        period,
        LeaveBalance(_EX, 2026, hours, Decimal(0)),
        slug=_PULIZIA,
        level="3",
    )

    assert _paid(result) == paid
    assert "permit_carryover" not in {b.detail for b in result.blockers}


def _metalmeccanico(
    slug: str, level: str, year: int, hourly_elements: Decimal | None = Decimal(0)
) -> PeriodResult:
    opening = PeriodState.zero()
    balance = LeaveBalance(LeaveBucket.ROL, 2025, Decimal(120), Decimal(0))
    opening = replace(
        opening, accrual=replace(opening.accrual, leave=LeaveAccount((balance,)))
    )
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10)),
            period_id=PeriodId(year, 12),
            payment_date=date(year, 12, 27),
            ccnl_id=slug,
            level_code=level,
            hourly_pay_elements=hourly_elements,
            opening_state=opening,
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2020, 1, 1)),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


@pytest.mark.parametrize(
    ("slug", "level", "amount"),
    [
        ("metalmeccanico-federmeccanica", "C3", Decimal("131.27")),
        ("metalmeccanico-confapi", "5", Decimal("132.42")),
    ],
    ids=["federmeccanica", "confapi"],
)
def test_the_par_conto_ore_is_paid_two_years_after(
    slug: str, level: str, amount: Decimal
) -> None:
    """Art. 5 / art. 22: 24 more months, then paid at the hourly pay (/173).

    The 10 hours left of 2025 are carried through 2026 and paid with the
    December pay of 2027, at the monthly pay over 173, though the CCNL gives
    no basis for the leave left at the end of the employment.
    """
    assert _paid(_metalmeccanico(slug, level, 2026)) == {}
    december = _metalmeccanico(slug, level, 2027)
    assert _paid(december) == {"rol": Decimal(10)}
    (item,) = (i for i in december.pay_items if i.item_id.startswith("leave_"))
    assert item.amount == amount


def test_federmeccanica_par_hourly_elements_at_expiry() -> None:
    """Art. 3: 10 * (2271.01 / 173 + 2.50) = 156.27 euros.

    With zero hourly elements the same ten hours pay 131.27 euros;
    an unstated hourly element blocks payment instead of assuming zero.
    """
    slug = "metalmeccanico-federmeccanica"
    without = _metalmeccanico(slug, "C3", 2027)
    with_elements = _metalmeccanico(slug, "C3", 2027, Decimal("2.50"))
    missing = _metalmeccanico(slug, "C3", 2027, None)
    assert next(
        i.amount for i in without.pay_items if i.item_id.startswith("leave_")
    ) == Decimal("131.27")
    assert next(
        i.amount for i in with_elements.pay_items if i.item_id.startswith("leave_")
    ) == Decimal("156.27")
    assert not _paid(missing)
    assert "hourly_pay_elements" in {b.detail for b in missing.blockers}
    assert not missing.closing_state.accrual.leave.balances[0].settled


def test_hourly_elements_are_added_only_when_stated_at_expiry() -> None:
    """Confapi art. 38: 10 * (2290.87 / 173 + 2.50) = 157.42 euros.

    The same ten hours without hourly elements pay 132.42 euros; omitting
    the fact instead blocks the payout and leaves the balance unsettled.
    """
    slug = "metalmeccanico-confapi"
    without = _metalmeccanico(slug, "5", 2027)
    with_elements = _metalmeccanico(slug, "5", 2027, Decimal("2.50"))
    missing = _metalmeccanico(slug, "5", 2027, None)
    assert next(
        i.amount for i in without.pay_items if i.item_id.startswith("leave_")
    ) == Decimal("132.42")
    assert next(
        i.amount for i in with_elements.pay_items if i.item_id.startswith("leave_")
    ) == Decimal("157.42")
    assert not _paid(missing)
    assert "hourly_pay_elements" in {b.detail for b in missing.blockers}
    assert not missing.closing_state.accrual.leave.balances[0].settled
