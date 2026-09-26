"""Unit tests for the employer model and its headcount value object."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.employer import Employer, Headcount


class TestHeadcount:
    """Headcount counts at least the worker being paid."""

    def test_accepts_one(self) -> None:
        """A single employee is a valid headcount."""
        assert Headcount(1).value == 1

    @pytest.mark.parametrize("value", [0, -1])
    def test_rejects_below_one(self, value: int) -> None:
        """Zero or negative headcount is impossible."""
        with pytest.raises(InvalidInputError, match="headcount must be >= 1"):
            Headcount(value)

    @pytest.mark.parametrize("value", [True, 1.5, "3"])
    def test_rejects_non_int(self, value: object) -> None:
        """Bools, floats and strings are not silently coerced."""
        with pytest.raises(InvalidInputError, match="must be an int"):
            Headcount(value)  # type: ignore[arg-type]


class TestEmployer:
    """The employer carries a validated headcount."""

    def test_keeps_declared_headcount(self) -> None:
        """The declared headcount is kept as given."""
        assert Employer(headcount=Headcount(12)).headcount == Headcount(12)

    def test_defaults_to_fifty_employees(self) -> None:
        """An undeclared headcount defaults to 50 employees."""
        assert Employer().headcount == Headcount(50)

    @pytest.mark.parametrize("value", [12, None])
    def test_rejects_raw_headcount(self, value: object) -> None:
        """A raw value is not accepted in place of a Headcount."""
        with pytest.raises(InvalidInputError, match="must be a Headcount"):
            Employer(headcount=value)  # type: ignore[arg-type]
