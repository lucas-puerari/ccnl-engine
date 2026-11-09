"""Hand oracles for the two distinct Confapi former-worker clauses.

For level 5 in May 2026, EUR 2,195.87 / 173 x 80/60 = EUR 16.92
for the single Friday holiday (1 May), or EUR 11.92 after a EUR 5 company
holiday payment. December 2026 has two weekday holidays (8 and 25
December), so the same formula applies twice using the June 2026 pay.
January 2029 has Monday New Year and Saturday Epiphany: EUR 2,345.87
/ 173 x (80/60) x 2 = EUR 36.16. The former Part One worker receives
11h10 only in December 2026: EUR 2,245.87 / 173 x 670/60 = EUR 144.96,
not twelve monthly instalments.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

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
from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.compensation.legacy_holiday.services import (
    _annual,
    _holiday,
    _holiday_count,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import EmploymentPeriod, NoPensionFund, Permanent
from ccnl_engine.pay_item.facade import FixedAllowanceEarning
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.run.types import RunKind

if TYPE_CHECKING:
    from ccnl_engine.compensation.legacy_holiday.models import LegacyHolidayPayment
    from ccnl_engine.period.context.services import RunContext


def _result(
    year: int,
    month: int,
    roles: frozenset[str] | None,
    offset: Decimal | None = Decimal(0),
    hired: date = date(2025, 1, 1),
    ended: date | None = None,
    patron: str | None = None,
    termination: bool = False,
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=(
                PayrollRun(RunKind.TERMINATION, month, year)
                if termination
                else PayrollRun.regular(year, month)
            ),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-confapi",
                level_code="5",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(hired, ended),
                roles=roles,
                holiday_company_offset=offset,
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20), patron_saint_day=patron),
            facts=PeriodFacts(),
        )
    )


def _payment(result: PeriodResult, code: str) -> Decimal:
    return sum(
        (
            i.amount
            for i in result.pay_items
            if isinstance(i, FixedAllowanceEarning) and i.item_id.startswith(code)
        ),
        Decimal(0),
    )


def test_weekday_holiday_and_company_absorption() -> None:
    """May 2026: one Friday, EUR 16.92 gross; EUR 5 offset leaves 11.92."""
    roles = frozenset({"former_legal_operaio"})
    assert _payment(_result(2026, 5, roles), "former_operaio_holidays") == Decimal(
        "16.92"
    )
    assert _payment(
        _result(2026, 5, roles, Decimal(5)), "former_operaio_holidays"
    ) == Decimal("11.92")
    assert (
        _payment(_result(2026, 5, roles, Decimal(20)), "former_operaio_holidays") == 0
    )
    assert _payment(_result(2026, 3, roles), "former_operaio_holidays") == 0
    assert _payment(_result(2026, 5, frozenset()), "former_operaio_holidays") == 0
    assert _payment(_result(2026, 12, roles), "former_operaio_holidays") == Decimal(
        "34.62"
    )


def _count(
    year: int,
    month: int,
    period: EmploymentPeriod | None = None,
    patron: str | None = None,
) -> int:
    context = cast(
        "RunContext",
        SimpleNamespace(
            request=SimpleNamespace(
                period_id=SimpleNamespace(year=year, month=month),
                employment_period=period,
                employer=SimpleNamespace(patron_saint_day=patron),
            ),
            repo=SimpleNamespace(load_national_holidays=load_national_holidays),
        ),
    )
    return _holiday_count(context)


def test_weekend_epiphany_counts_in_january() -> None:
    """January 2029: Monday New Year plus Saturday Epiphany, two 80m quotas."""
    assert _count(2029, 1) == 2


def test_new_holiday_and_service_boundaries() -> None:
    """4 October starts in 2026; December 25 falls after service ends on 24."""
    assert _count(2025, 10) == 0
    assert (
        _count(2026, 12, EmploymentPeriod(date(2026, 12, 1), date(2026, 12, 24))) == 1
    )
    assert _count(2026, 5, EmploymentPeriod(date(2026, 5, 2), None)) == 0


def test_november_fourth_is_not_a_weekday_holiday_supplement() -> None:
    """The separate first-Sunday-of-November quota has no 80-minute supplement."""
    context = cast(
        "RunContext",
        SimpleNamespace(
            request=SimpleNamespace(
                period_id=SimpleNamespace(year=2026, month=11),
                employment_period=None,
                employer=SimpleNamespace(patron_saint_day=None),
            ),
            repo=SimpleNamespace(
                load_national_holidays=lambda: SimpleNamespace(
                    holidays=(SimpleNamespace(day="11-04"),)
                )
            ),
        ),
    )
    assert _holiday_count(context) == 0


def test_annual_december_only() -> None:
    """December 2026: EUR 2,245.87 / 173 x 670/60 = EUR 144.96."""
    roles = frozenset({"former_part_one_2008"})
    old = date(2008, 12, 1)
    december = _result(2026, 12, roles, hired=old)
    assert _payment(december, "former_part_one_annual") == Decimal("144.96")
    assert _payment(_result(2026, 11, roles, hired=old), "former_part_one_annual") == 0
    assert _payment(_result(2026, 12, roles), "former_part_one_annual") == 0
    assert (
        _payment(
            _result(2026, 12, frozenset({"former_legal_operaio"}), hired=old),
            "former_part_one_annual",
        )
        == 0
    )
    assert any(i.fact == "roles" for i in _result(2026, 12, None, hired=old).issues)


def test_annual_before_start_and_without_a_stated_service_period() -> None:
    """No annual before 2009, and an explicit noncohort role excludes pay."""
    clause = cast("LegacyHolidayPayment", object())
    for year in (2008, 2026):
        context = cast(
            "RunContext",
            SimpleNamespace(
                request=SimpleNamespace(
                    period_id=SimpleNamespace(year=year, month=12),
                    employment_period=None,
                    roles=frozenset(),
                ),
            ),
        )
        assert not _annual(context, clause, Decimal(1)).items


def test_missing_offset_only_on_a_qualifying_holiday() -> None:
    """An unknown company arrangement blocks May, not holiday-free March."""
    roles = frozenset({"former_legal_operaio"})
    may = _result(2026, 5, roles, None)
    march = _result(2026, 3, roles, None)
    assert any(i.fact == "holiday_company_offset" for i in may.issues)
    assert not any(i.fact == "holiday_company_offset" for i in march.issues)


def test_direct_request_rejects_negative_company_offset() -> None:
    """A negative EUR 5 cannot turn a EUR 16.92 holiday into EUR 21.92."""
    base = PeriodInput(
        run=PayrollRun.regular(2026, 5),
        payment_date=date(2026, 5, 27),
        employment=Employment(
            ccnl_id="metalmeccanico-confapi",
            level_code="5",
            contract_type=Permanent(),
            holiday_company_offset=Decimal(0),
        ),
        employer=EmployerProfile(headcount=Headcount(20)),
        facts=PeriodFacts(),
    ).calculation_request()
    assert isinstance(base, PeriodCalculationRequest)
    with pytest.raises(InvalidInputError, match="holiday_company_offset"):
        replace(base, holiday_company_offset=Decimal(-5))


def test_pre_2009_holiday_has_no_extra_hours() -> None:
    """December 2008 holiday hours are EUR 0 even at EUR 12 per hour."""
    context = cast(
        "RunContext",
        SimpleNamespace(
            request=SimpleNamespace(period_id=SimpleNamespace(year=2008, month=12))
        ),
    )
    assert not _holiday(
        context, cast("LegacyHolidayPayment", object()), Decimal(12)
    ).items


def test_patron_holiday_within_service_and_not_double_counted() -> None:
    """June 2026 patron adds EUR 17.31 to the national EUR 17.31: EUR 34.62."""
    roles = frozenset({"former_legal_operaio"})
    assert _count(2026, 6, patron="06-24") == 2
    assert _count(2026, 6, patron="06-28") == 1
    assert _count(2026, 5, patron="05-01") == 1
    assert _count(2025, 2, patron="02-29") == 0
    assert _count(2026, 6, EmploymentPeriod(date(2026, 6, 25), None), "06-24") == 0
    assert _payment(
        _result(2026, 6, roles, patron="06-24"), "former_operaio_holidays"
    ) == Decimal("34.62")
    assert _payment(_result(2026, 6, roles), "former_operaio_holidays") == Decimal(
        "17.31"
    )


def test_standalone_termination_holiday_and_december_payment() -> None:
    """May 15 exit pays EUR 16.92; Dec 24 exit pays EUR 17.31 plus EUR 144.96."""
    worker = frozenset({"former_legal_operaio", "former_part_one_2008"})
    may = _result(
        2026,
        5,
        worker,
        hired=date(2008, 1, 1),
        ended=date(2026, 5, 15),
        termination=True,
    )
    assert _payment(may, "former_operaio_holidays") == Decimal("16.92")
    assert _payment(may, "former_part_one_annual") == 0
    december = _result(
        2026,
        12,
        worker,
        hired=date(2008, 1, 1),
        ended=date(2026, 12, 24),
        termination=True,
    )
    assert _payment(december, "former_operaio_holidays") == Decimal("17.31")
    assert _payment(december, "former_part_one_annual") == Decimal("144.96")
    before = _result(
        2026,
        11,
        worker,
        hired=date(2008, 1, 1),
        ended=date(2026, 11, 30),
        termination=True,
    )
    assert _payment(before, "former_part_one_annual") == 0
