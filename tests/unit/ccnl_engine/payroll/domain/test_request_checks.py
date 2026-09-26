"""Construction checks of PeriodCalculationRequest: types and employment."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import EmploymentPeriod, WeeklyHours
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.request_checks import employment_gap, type_error
from ccnl_engine.payroll.domain.run import PayrollRun

_YEAR = 2026


def _request(**kwargs: Any) -> PeriodCalculationRequest:  # noqa: ANN401
    fields: dict[str, Any] = {
        "period_id": PeriodId(year=_YEAR, month=3),
        "payment_date": date(_YEAR, 3, 27),
        "ccnl_slug": "metalmeccanico-federmeccanica.json",
        "level_code": "C3",
        "employer": EmployerProfile(headcount=Headcount(50)),
    }
    fields.update(kwargs)
    return PeriodCalculationRequest(**fields)


class TestFieldTypes:
    """Values of the wrong type raise InvalidInputError at construction."""

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("weekly_hours", 40),
            ("full_time_weekly_hours", 40),
            ("contributable_hours", 120),
            ("seniority_months", 24),
            ("period_id", (2026, 3)),
            ("payment_date", "2026-03-27"),
            ("ccnl_slug", 7),
            ("contract_type", "permanent"),
            ("employer", 50),
            ("ceiling_status", "post_1995"),
            ("events", None),
            ("employment_period", date(_YEAR, 1, 1)),
            ("opening_state", None),
        ],
    )
    def test_raw_value_is_invalid_input(self, field: str, value: object) -> None:
        """A raw value where a typed one is expected is a domain error."""
        with pytest.raises(InvalidInputError, match=rf"^{field} must be"):
            _request(**{field: value})

    def test_typed_values_are_accepted(self) -> None:
        """Value objects of the declared types construct the request."""
        request = _request(
            weekly_hours=WeeklyHours(20), full_time_weekly_hours=WeeklyHours(40)
        )
        assert request.weekly_hours == WeeklyHours(20)

    def test_message_names_every_accepted_type(self) -> None:
        """A field with several accepted types lists them all."""
        message = type_error([("x", 1, (str, bytes), False)])
        assert message == "x must be str or bytes; got int 1"


class TestRegularRunInEmployment:
    """A regular run must fall in a month with a day of employment."""

    def test_run_before_hire_is_invalid_input(self) -> None:
        """A regular run of a month before the hire date is rejected."""
        employment = EmploymentPeriod(started_on=date(_YEAR, 4, 1))
        with pytest.raises(InvalidInputError, match="outside the employment"):
            _request(employment_period=employment)

    def test_run_after_termination_is_invalid_input(self) -> None:
        """A regular run of a month after the termination is rejected."""
        employment = EmploymentPeriod(date(_YEAR, 1, 1), date(_YEAR, 2, 28))
        with pytest.raises(InvalidInputError, match="outside the employment"):
            _request(employment_period=employment)

    def test_partial_month_is_accepted(self) -> None:
        """A hire in the run month leaves the run inside the employment."""
        employment = EmploymentPeriod(started_on=date(_YEAR, 3, 20))
        assert _request(employment_period=employment).employment_period == employment

    def test_extra_month_run_is_not_bound(self) -> None:
        """An extra-month run is not checked against the employment months."""
        employment = EmploymentPeriod(started_on=date(_YEAR, 4, 1))
        run = PayrollRun.thirteenth(_YEAR, 3)
        assert employment_gap(PeriodId(year=_YEAR, month=3), run, employment) is None
