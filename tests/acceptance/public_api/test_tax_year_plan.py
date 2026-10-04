"""A tax year holds the payments actually made in it; the last one settles it.

Art. 51 c. 1 TUIR: employment income belongs to the tax year it is paid in,
and pay of a period of the year before paid by 12 January belongs to that
year (cassa allargata).  Commercio L4 pays twelve months, the
quattordicesima in June and the tredicesima in December, on the 28th of
the month by default.  With the December salary paid on 13 January 2027,
tax year 2026 holds thirteen payments and its conguaglio (art. 23 c. 3 DPR
600/1973) falls on the tredicesima; with the December salary paid on 12
January 2027 it holds fourteen and the conguaglio falls on that December
payment.  2027 rules are the 2026 ones relabelled
(:class:`~tests.fixtures.next_year_repository.NextYearRepository`): only
the structure and differential amounts are asserted on 2027 runs.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    TaxYearPlan,
    TaxYearResult,
)
from tests.fixtures.next_year_repository import NextYearRepository

if TYPE_CHECKING:
    from ccnl_engine.inputs import PaymentId

_ENGINE = PayrollEngine(repository=NextYearRepository())
_COMMERCIO_L4 = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _plan(year: int, **dates: date) -> CompetenceYearPlan:
    """Return the Commercio L4 plan of ``year``, with payment dates by run id.

    Returns:
        The plan; ``dates`` maps a month name (``december``) to its date.
    """
    months = {"december": 12}
    return CompetenceYearPlan(
        year=year,
        employment=_COMMERCIO_L4,
        employer=_EMPLOYER,
        payment_dates={months[k]: v for k, v in dates.items()},
    )


def _ids(payments: tuple[PaymentId, ...]) -> list[str]:
    return [str(p) for p in payments]


@cache
def _tax_year_2026(december: date) -> TaxYearResult:
    """Compute tax year 2026 with the December salary paid on ``december``.

    Returns:
        The payments of 2026 and its closing state.
    """
    plan = TaxYearPlan(
        tax_year=2026, competence_years=(_plan(2026, december=december),)
    )
    return _ENGINE.calculate_tax_year(plan)


class TestDecemberPaidInJanuary:
    """12 January is the last day of the cassa allargata; 13 January is not."""

    def test_december_paid_on_13_january_leaves_2026_with_thirteen_payments(
        self,
    ) -> None:
        """The tredicesima, last payment of 2026, settles its conguaglio."""
        year = _tax_year_2026(date(2027, 1, 13))

        assert len(year.payments) == 13
        assert str(year.conguaglio) == "2026-12-thirteenth@2026-12-28"
        assert year.closing_state.cash.is_complete
        assert year.next_opening_state.tax_year == 2027

    def test_december_paid_on_12_january_belongs_to_2026(self) -> None:
        """Paid in 2027 but attributed to 2026: it is the conguaglio of 2026."""
        year = _tax_year_2026(date(2027, 1, 12))

        assert year.conguaglio is not None
        assert year.conguaglio.tax_year == 2026
        assert len(year.payments) == 14
        assert str(year.conguaglio) == "2026-12-regular@2027-01-12"
        assert _ids(year.payments)[-2:] == [
            "2026-12-thirteenth@2026-12-28",
            "2026-12-regular@2027-01-12",
        ]

    def test_the_two_dates_differ_by_the_december_gross_in_2026(self) -> None:
        """Differential: 2026 income differs by exactly the December salary."""
        inside = _tax_year_2026(date(2027, 1, 12))
        outside = _tax_year_2026(date(2027, 1, 13))
        december = inside.period_results[-1]

        assert inside.annual_gross - outside.annual_gross == december.period_gross
        assert (
            inside.closing_state.cash.earnings.gross
            - outside.closing_state.cash.earnings.gross
            == december.period_gross
        )

    def test_2027_opens_with_the_late_december_and_closes(self) -> None:
        """2027 holds fifteen payments, the late December first."""
        late = date(2027, 1, 13)
        plan = TaxYearPlan(
            tax_year=2027,
            competence_years=(_plan(2026, december=late), _plan(2027)),
            opening_state=_tax_year_2026(late).next_opening_state,
        )

        year = _ENGINE.calculate_tax_year(plan)

        assert len(year.payments) == 15
        assert _ids(year.payments)[0] == "2026-12-regular@2027-01-13"
        assert str(year.conguaglio) == "2027-12-thirteenth@2027-12-28"
        assert year.next_opening_state.tax_year == 2028
        slots = {
            d.inputs["withholding_slots"]
            for r in year.period_results
            for d in r.decisions
            if d.capability == "irpef"
        }
        assert slots == {"15"}

    @pytest.mark.parametrize("day", [12, 13])
    def test_competence_years_give_the_same_states_as_tax_years(self, day: int) -> None:
        """Both public paths compute the same payments on the same schedule."""
        paid_on = date(2027, 1, day)
        first = _ENGINE.calculate_competence_year(_plan(2026, december=paid_on))
        second = _ENGINE.calculate_competence_year(
            CompetenceYearPlan(
                year=2027,
                employment=_COMMERCIO_L4,
                employer=_EMPLOYER,
                opening_state=first.next_opening_state,
            )
        )
        by_tax_year = _ENGINE.calculate_tax_year(
            TaxYearPlan(
                tax_year=2027,
                competence_years=(_plan(2026, december=paid_on), _plan(2027)),
                opening_state=_tax_year_2026(paid_on).next_opening_state,
            )
        )

        assert first.conguagli[0] == _tax_year_2026(paid_on).conguaglio
        assert second.closing_state == by_tax_year.closing_state


@pytest.mark.parametrize(
    ("paid_on", "position"),
    [
        (date(2027, 1, 13), 0),
        (date(2027, 6, 15), 5),
        (date(2027, 12, 30), 14),
    ],
    ids=["before", "during", "after"],
)
def test_conguaglio_falls_on_the_last_payment_with_a_late_payment(
    paid_on: date, position: int
) -> None:
    """December 2026 paid before, among or after the 2027 runs.

    Every case has fifteen payments in date order; the conguaglio is the
    last of them, the late December itself when it comes after the
    tredicesima of 28 December 2027.
    """
    plan = TaxYearPlan(
        tax_year=2027,
        competence_years=(_plan(2026, december=paid_on), _plan(2027)),
        opening_state=_tax_year_2026(paid_on).next_opening_state,
    )

    year = _ENGINE.calculate_tax_year(plan)

    late = f"2026-12-regular@{paid_on.isoformat()}"
    assert _ids(year.payments).index(late) == position
    assert [p.payment_date for p in year.payments] == sorted(
        p.payment_date for p in year.payments
    )
    assert year.conguaglio == year.payments[-1]
    assert year.conguagli == (year.payments[-1],)
    assert year.closing_state.accrual.regular_months(2026) == 12


class TestPayInArrears:
    """An employer paying the salary of a month on the 10th of the next one."""

    @staticmethod
    def _arrears() -> CompetenceYearPlan:
        dates: dict[int | str, date] = {
            month: date(2026 + month // 12, month % 12 + 1, 10)
            for month in range(1, 13)
        }
        dates["2026-06-fourteenth"] = date(2026, 6, 15)
        dates["2026-12-thirteenth"] = date(2026, 12, 15)
        return CompetenceYearPlan(
            year=2026,
            employment=_COMMERCIO_L4,
            employer=_EMPLOYER,
            payment_dates=dates,
        )

    def test_extra_months_paid_before_their_month_salary_are_accepted(
        self,
    ) -> None:
        """The quattordicesima precedes the June salary, the tredicesima December's.

        The December salary paid on 10 January 2027 is still 2026 income
        and the last payment of 2026: it settles the conguaglio.
        """
        year = _ENGINE.calculate_competence_year(self._arrears())

        ids = [str(r.run.run_id) for r in year.period_results if r.run is not None]
        assert ids.index("2026-06-fourteenth") < ids.index("2026-06-regular")
        assert ids.index("2026-12-thirteenth") < ids.index("2026-12-regular")
        assert len(ids) == 14
        assert {r.closing_state.tax_year for r in year.period_results} == {2026}
        assert str(year.conguagli[0]) == "2026-12-regular@2027-01-10"
        assert year.next_opening_state.tax_year == 2027

    def test_a_payment_dated_before_the_last_one_is_rejected(self) -> None:
        """Payments close in date order, whatever their competence."""
        year = _ENGINE.calculate_competence_year(self._arrears())
        march = year.period_results[2]
        assert str(march.run.run_id if march.run else None) == "2026-03-regular"

        with pytest.raises(InvalidInputError, match="dated before") as info:
            _ENGINE.calculate_period(
                PeriodInput(
                    run=PayrollRun.regular(2026, 4),
                    payment_date=date(2026, 4, 1),
                    employment=_COMMERCIO_L4,
                    employer=_EMPLOYER,
                    opening_state=march.closing_state,
                )
            )

        assert info.value.field == "TaxCashState.payments"
