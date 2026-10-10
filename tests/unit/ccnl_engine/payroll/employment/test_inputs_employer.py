"""Unit tests for the employer model and its headcount value object."""

from __future__ import annotations

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.employment.inputs_employer import (
    AgriculturalZone,
    EmployerActivity,
    EmployerProfile,
    Headcount,
)


class TestHeadcount:
    """Headcount counts at least the worker being paid."""

    def test_accepts_one(self) -> None:
        """A single employee is a valid headcount."""
        assert Headcount(1).value == 1

    @pytest.mark.parametrize("value", [0, -1])
    def test_rejects_below_one(self, value: int) -> None:
        """Zero or negative headcount is impossible."""
        with pytest.raises(
            InvalidInputError, match=r"Headcount\.value must be an int >= 1"
        ):
            Headcount(value)

    @pytest.mark.parametrize("value", [True, 1.5, "3"])
    def test_rejects_non_int(self, value: object) -> None:
        """Bools, floats and strings are not silently coerced."""
        with pytest.raises(InvalidInputError, match="must be an int"):
            Headcount(value)  # type: ignore[arg-type]


class TestEmployerProfile:
    """The employer carries a validated headcount and an optional activity."""

    def test_keeps_declared_headcount(self) -> None:
        """The declared headcount is kept as given."""
        assert EmployerProfile(headcount=Headcount(12)).headcount == Headcount(12)

    def test_requires_headcount(self) -> None:
        """No headcount is assumed: the employer must declare it."""
        with pytest.raises(TypeError, match="headcount"):
            EmployerProfile()  # type: ignore[call-arg]

    def test_activity_defaults_to_unknown(self) -> None:
        """An undeclared activity is unknown."""
        assert EmployerProfile(headcount=Headcount(3)).activity is None

    def test_normalizes_activity_value(self) -> None:
        """The string value of an activity is accepted and normalized."""
        employer = EmployerProfile(headcount=Headcount(3), activity="tourism")  # type: ignore[arg-type]
        assert employer.activity is EmployerActivity.TOURISM

    def test_rejects_unknown_activity(self) -> None:
        """An activity that names no known value is invalid input."""
        with pytest.raises(InvalidInputError, match="activity must be one of"):
            EmployerProfile(headcount=Headcount(3), activity="mining")  # type: ignore[arg-type]

    @pytest.mark.parametrize("value", [12, None])
    def test_rejects_raw_headcount(self, value: object) -> None:
        """A raw value is not accepted in place of a Headcount."""
        with pytest.raises(InvalidInputError, match="must be a Headcount"):
            EmployerProfile(headcount=value)  # type: ignore[arg-type]


def test_agricultural_zone_is_parsed_and_checked() -> None:
    """A zone given by value is the enum; anything else is rejected."""
    profile = EmployerProfile(
        headcount=Headcount(5),
        agricultural_zone="mountain",  # type: ignore[arg-type]
    )
    assert profile.agricultural_zone is AgriculturalZone.MOUNTAIN
    with pytest.raises(InvalidInputError, match="agricultural_zone"):
        EmployerProfile(
            headcount=Headcount(5),
            agricultural_zone="hilly",  # type: ignore[arg-type]
        )
