"""Scalar validators of the public inputs."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validation import (
    MAX_DECIMAL_MAGNITUDE,
    parse_enum,
    reject,
    require_bool,
    require_choice,
    require_date,
    require_decimal,
    require_instance,
    require_instances,
    require_int,
    require_str,
    type_names,
)

_FEATURE = "test_feature"


class _Colour(StrEnum):
    RED = "red"
    BLUE = "blue"


def test_reject_names_the_field_the_feature_and_the_fix() -> None:
    """Every rejection carries the path, the feature and a remediation."""
    with pytest.raises(InvalidInputError) as raised:
        reject("Input.amount", "a finite Decimal", "x" * 200, feature=_FEATURE)

    error = raised.value
    assert error.field == "Input.amount"
    assert error.feature == _FEATURE
    assert error.code == "invalid_input"
    assert error.remediation == "Supply Input.amount as a finite Decimal."
    assert str(error).startswith("Input.amount must be a finite Decimal; got 'xxx")
    assert len(str(error)) < 120


def test_type_names_lists_every_accepted_type() -> None:
    """One type or several are named for the message."""
    assert type_names(int) == "an int"
    assert type_names((str, bytes)) == "a str or a bytes"


class TestRequireInstance:
    """Instances, optional ``None`` and several fields at once."""

    def test_accepts_an_instance_and_optional_none(self) -> None:
        """An instance passes; ``None`` passes only when optional."""
        require_instance(date(2026, 1, 1), date, "x", feature=_FEATURE)
        require_instance(None, date, "x", feature=_FEATURE, optional=True)
        with pytest.raises(InvalidInputError, match="x must be a date"):
            require_instance(None, date, "x", feature=_FEATURE)

    def test_reports_the_first_field_of_the_wrong_type(self) -> None:
        """The path is the owner and the field name."""
        with pytest.raises(InvalidInputError) as raised:
            require_instances(
                "Owner",
                (("a", 1, int, False), ("b", "x", int, True), ("c", 1.5, int, False)),
                feature=_FEATURE,
            )
        assert raised.value.field == "Owner.b"


class TestRequireInt:
    """Ints within bounds; a bool is not an int."""

    @pytest.mark.parametrize("value", [True, 1.0, "1", None, Decimal(1)], ids=repr)
    def test_rejects_what_is_not_an_int(self, value: object) -> None:
        """A bool, a float, a string, ``None`` or a Decimal is rejected."""
        with pytest.raises(InvalidInputError, match="an int"):
            require_int(value, "n", feature=_FEATURE)

    @pytest.mark.parametrize("value", [0, 13])
    def test_rejects_out_of_bounds(self, value: int) -> None:
        """Both bounds are inclusive."""
        with pytest.raises(InvalidInputError, match=">= 1 and <= 12"):
            require_int(value, "n", feature=_FEATURE, minimum=1, maximum=12)

    def test_accepts_bounds_and_optional_none(self) -> None:
        """The bounds themselves and an optional ``None`` pass."""
        require_int(1, "n", feature=_FEATURE, minimum=1, maximum=12)
        require_int(12, "n", feature=_FEATURE, minimum=1, maximum=12)
        require_int(None, "n", feature=_FEATURE, optional=True)


class TestRequireDecimal:
    """Finite Decimals within bounds."""

    @pytest.mark.parametrize(
        "value",
        [
            Decimal("NaN"),
            Decimal("sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            1,
            1.5,
            "1",
            True,
            None,
        ],
        ids=repr,
    )
    def test_rejects_what_is_not_a_finite_decimal(self, value: object) -> None:
        """Non-finite decimals and other types are rejected, never compared."""
        with pytest.raises(InvalidInputError, match="a finite Decimal"):
            require_decimal(value, "d", feature=_FEATURE, minimum=Decimal(0))

    @pytest.mark.parametrize("value", [MAX_DECIMAL_MAGNITUDE, -MAX_DECIMAL_MAGNITUDE])
    def test_rejects_a_magnitude_no_payroll_reaches(self, value: Decimal) -> None:
        """A billion or more, either sign, is rejected."""
        with pytest.raises(InvalidInputError, match="below 1E\\+9 in magnitude"):
            require_decimal(value, "d", feature=_FEATURE)

    @pytest.mark.parametrize(
        ("value", "message"),
        [
            (Decimal(0), "> 0"),
            (Decimal(-1), "> 0"),
        ],
    )
    def test_positive_rejects_zero_and_below(
        self, value: Decimal, message: str
    ) -> None:
        """``positive`` excludes zero."""
        with pytest.raises(InvalidInputError, match=message):
            require_decimal(value, "d", feature=_FEATURE, positive=True)

    @pytest.mark.parametrize("value", [Decimal("-0.01"), Decimal("1.01")])
    def test_rejects_out_of_bounds(self, value: Decimal) -> None:
        """Both bounds are inclusive."""
        with pytest.raises(InvalidInputError, match=">= 0 and <= 1"):
            require_decimal(
                value, "d", feature=_FEATURE, minimum=Decimal(0), maximum=Decimal(1)
            )

    def test_accepts_bounds_and_optional_none(self) -> None:
        """The bounds and an optional ``None`` pass."""
        require_decimal(
            Decimal(1), "d", feature=_FEATURE, minimum=Decimal(0), maximum=Decimal(1)
        )
        require_decimal(None, "d", feature=_FEATURE, optional=True)


class TestOtherScalars:
    """Dates, bools, strings, choices and enums."""

    def test_date_rejects_a_datetime_and_a_string(self) -> None:
        """A datetime does not compare with a date; a string is not one."""
        require_date(date(2026, 1, 1), "d", feature=_FEATURE)
        require_date(None, "d", feature=_FEATURE, optional=True)
        for value in (datetime(2026, 1, 1, 9), "2026-01-01", None):  # noqa: DTZ001
            with pytest.raises(InvalidInputError, match="a date"):
                require_date(value, "d", feature=_FEATURE)

    def test_bool_rejects_an_int(self) -> None:
        """1 and 0 are not bools."""
        require_bool(False, "b", feature=_FEATURE)
        with pytest.raises(InvalidInputError, match="a bool"):
            require_bool(1, "b", feature=_FEATURE)

    def test_str_rejects_blank_when_required(self) -> None:
        """A blank string passes only when blank is allowed."""
        require_str("", "s", feature=_FEATURE)
        require_str(None, "s", feature=_FEATURE, optional=True)
        with pytest.raises(InvalidInputError, match="a non-blank str"):
            require_str("  ", "s", feature=_FEATURE, non_blank=True)
        with pytest.raises(InvalidInputError, match="a str"):
            require_str(3, "s", feature=_FEATURE)

    def test_choice_accepts_only_its_strings(self) -> None:
        """A string outside the choices or a non-string is rejected."""
        require_choice("a", ("a", "b"), "c", feature=_FEATURE)
        for value in ("z", 1):
            with pytest.raises(InvalidInputError, match=r"one of \['a', 'b'\]"):
                require_choice(value, ("a", "b"), "c", feature=_FEATURE)

    def test_enum_accepts_a_member_or_its_value(self) -> None:
        """A member or its value is normalized; anything else is rejected."""
        assert parse_enum(_Colour.RED, _Colour, "e", feature=_FEATURE) is _Colour.RED
        assert parse_enum("blue", _Colour, "e", feature=_FEATURE) is _Colour.BLUE
        for value in ("green", 1, None):
            with pytest.raises(InvalidInputError, match=r"one of \['red', 'blue'\]"):
                parse_enum(value, _Colour, "e", feature=_FEATURE)
