"""Unit tests for the dataclass_codec serialisation primitives.

Tests _dump, _load_by_hint, _load_dataclass, _load_union, _try_union_member,
and the _NO_MATCH sentinel, extracted from test_calculation.py.
"""

from __future__ import annotations

import dataclasses
import typing
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.employee import RalOverride, SeniorityByCount
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours
from ccnl_engine.engine.serialization.dataclass_codec import (
    _NO_MATCH,
    _dump,
    _load_by_hint,
    _load_dataclass,
    _load_union,
    _try_union_member,
)


@dataclasses.dataclass(frozen=True)
class _SimplePoint:
    x: int
    y: int = 0


class TestDumpLoadPrimitives:
    """Low-level serialisation helpers used by InputSnapshot."""

    def test_dump_rejects_unsupported_type(self) -> None:
        """_dump raises TypeError for a non-JSON-native object."""

        class NotMappable:
            pass

        with pytest.raises(TypeError, match="Cannot serialise"):
            _dump(NotMappable())

    def test_load_dataclass_missing_field_raises(self) -> None:
        """_load_dataclass raises ValueError on a missing required field."""
        with pytest.raises(ValueError, match="Missing field"):
            _load_dataclass(SeniorityByCount, {})

    def test_load_union_no_match_raises(self) -> None:
        """_load_union raises ValueError when no dataclass member matches."""
        with pytest.raises(ValueError, match="No union member matched"):
            _load_union([SeniorityByCount], {"unrelated": 1})

    def test_load_union_pydantic_member_failure(self) -> None:
        """_load_union tries pydantic members and raises when none accept."""
        with pytest.raises(ValueError, match="No union member matched"):
            _load_union([Permanent], {"type": "not-a-contract"})

    def test_load_union_tag_mismatch_falls_through(self) -> None:
        """A non-matching $type tag falls back to trial-loading."""
        loaded = _load_union(
            [SeniorityByCount],
            {"$type": "SomeOtherType", "value": 3},
        )
        assert isinstance(loaded, SeniorityByCount)
        assert loaded.value == 3

    def test_load_union_non_string_tag_falls_through(self) -> None:
        """A non-string $type tag is ignored and trial-loading applies."""
        loaded = _load_union(
            [SeniorityByCount],
            {"$type": 5, "value": 4},
        )
        assert isinstance(loaded, SeniorityByCount)
        assert loaded.value == 4

    def test_load_dataclass_non_dict_raises(self) -> None:
        """_load_dataclass raises TypeError when raw is not a mapping."""
        with pytest.raises(TypeError, match="Expected a mapping"):
            _load_dataclass(SeniorityByCount, "not-a-dict")

    def test_load_dataclass_unknown_field_raises(self) -> None:
        """_load_dataclass raises ValueError on an unrecognised field key."""
        with pytest.raises(ValueError, match="Unknown fields"):
            _load_dataclass(SeniorityByCount, {"value": 3, "bogus_field": 1})

    def test_load_dataclass_dtype_tag_is_exempt(self) -> None:
        """The $type discriminator key is not treated as an unknown field."""
        loaded = _load_dataclass(
            SeniorityByCount, {"$type": "SeniorityByCount", "value": 7}
        )
        assert isinstance(loaded, SeniorityByCount)
        assert loaded.value == 7

    def test_load_dataclass_migrates_mortgage_pre_1993_true(self) -> None:
        """mortgage_pre_1993=True is migrated to mortgage_pre_2022=True."""
        result = _load_dataclass(Art15Deductions, {"mortgage_pre_1993": True})
        assert isinstance(result, Art15Deductions)
        assert result.mortgage_pre_2022 is True

    def test_load_dataclass_migrates_mortgage_pre_1993_false_raises(self) -> None:
        """mortgage_pre_1993=False raises ValueError — the mapping is ambiguous."""
        with pytest.raises(ValueError, match="ambiguous"):
            _load_dataclass(Art15Deductions, {"mortgage_pre_1993": False})

    def test_load_dataclass_both_old_and_new_key_drops_old(self) -> None:
        """Both old and new key present: old is dropped, new wins."""
        result = _load_dataclass(
            Art15Deductions,
            {"mortgage_pre_1993": True, "mortgage_pre_2022": False},
        )
        assert isinstance(result, Art15Deductions)
        assert result.mortgage_pre_2022 is False  # new key wins

    def test_load_dataclass_art15_no_old_key_skips_rename(self) -> None:
        """Art15Deductions without the old key loads normally, using default."""
        result = _load_dataclass(Art15Deductions, {"mortgage_interest": "500"})
        assert isinstance(result, Art15Deductions)
        assert result.mortgage_pre_2022 is False


class TestLoadDataclassCompat:
    """_load_dataclass skips fields with defaults when absent from the dict."""

    def test_missing_defaulted_field_is_skipped(self) -> None:
        """A dict missing a field with a default does not raise."""
        # OvertimeHours has all fields defaulted to zero; an empty dict should
        # reconstruct the instance using the defaults.
        result = _load_dataclass(OvertimeHours, {})
        assert result == OvertimeHours()

    def test_partial_dict_uses_defaults_for_absent_fields(self) -> None:
        """Only provided fields are set; absent defaulted fields use defaults."""
        result = _load_dataclass(OvertimeHours, {"weekday_hours": "5"})
        assert isinstance(result, OvertimeHours)
        assert result.weekday_hours == Decimal(5)
        assert result.night_hours == Decimal(0)


class TestR2R19R20Fixes:
    """Tests for Literal replay (R2), snapshot alias (R19), deepcopy (R20)."""

    def test_literal_valid_value_returned(self) -> None:
        """_load_by_hint returns a valid Literal value unchanged."""
        hint: type = typing.Literal["impiegato", "operaio"]  # type: ignore[assignment]
        assert _load_by_hint(hint, "impiegato") == "impiegato"

    def test_literal_invalid_value_raises(self) -> None:
        """_load_by_hint rejects a value not in the Literal union."""
        hint: type = typing.Literal["impiegato", "operaio"]  # type: ignore[assignment]
        with pytest.raises(ValueError, match="expected one of"):
            _load_by_hint(hint, "supervisore")


class TestCoerceScalarStrictPrimitives:
    """_load_by_hint rejects wrong primitive types for bool/int/str."""

    def test_bool_string_false_rejected(self) -> None:
        """String 'false' for a bool hint raises TypeError."""
        with pytest.raises(TypeError, match="expected bool"):
            _load_by_hint(bool, "false")

    def test_bool_string_true_rejected(self) -> None:
        """String 'true' for a bool hint raises TypeError."""
        with pytest.raises(TypeError, match="expected bool"):
            _load_by_hint(bool, "true")

    def test_bool_int_zero_rejected(self) -> None:
        """Integer 0 for a bool hint raises TypeError."""
        with pytest.raises(TypeError, match="expected bool"):
            _load_by_hint(bool, 0)

    def test_bool_valid_passes(self) -> None:
        """True/False pass through unchanged for a bool hint."""
        assert _load_by_hint(bool, True) is True
        assert _load_by_hint(bool, False) is False

    def test_int_string_rejected(self) -> None:
        """String '42' for an int hint raises TypeError."""
        with pytest.raises(TypeError, match="expected int"):
            _load_by_hint(int, "42")

    def test_int_bool_rejected(self) -> None:
        """Bool True for an int hint raises TypeError (bool subclass guard)."""
        with pytest.raises(TypeError, match="expected int"):
            _load_by_hint(int, True)

    def test_int_valid_passes(self) -> None:
        """A plain int passes through unchanged."""
        assert _load_by_hint(int, 2026) == 2026

    def test_str_int_rejected(self) -> None:
        """Integer 42 for a str hint raises TypeError."""
        with pytest.raises(TypeError, match="expected str"):
            _load_by_hint(str, 42)

    def test_str_valid_passes(self) -> None:
        """A plain str passes through unchanged."""
        assert _load_by_hint(str, "hello") == "hello"


class TestDataclassCompatPaths:
    """Legacy dataclass paths in _dump/_load_* remain functional."""

    def test_dump_dataclass_value(self) -> None:
        """_dump serialises a plain dataclass to a $type-tagged dict."""
        result = _dump(_SimplePoint(x=3, y=7))
        assert result == {"$type": "_SimplePoint", "x": 3, "y": 7}

    def test_load_dataclass_plain(self) -> None:
        """_load_dataclass reconstructs a plain dataclass from a dict."""
        result = _load_dataclass(_SimplePoint, {"x": 5})
        assert isinstance(result, _SimplePoint)
        assert result.x == 5
        assert result.y == 0

    def test_load_dataclass_with_all_fields(self) -> None:
        """_load_dataclass sets all provided fields on a plain dataclass."""
        result = _load_dataclass(_SimplePoint, {"x": 1, "y": 2})
        assert isinstance(result, _SimplePoint)
        assert result.x == 1
        assert result.y == 2

    def test_load_dataclass_unknown_field_raises(self) -> None:
        """_load_dataclass raises ValueError for unknown keys on dataclass."""
        with pytest.raises(ValueError, match="Unknown fields"):
            _load_dataclass(_SimplePoint, {"x": 1, "bogus": 99})

    def test_load_dataclass_missing_required_raises(self) -> None:
        """_load_dataclass raises ValueError when required field is absent."""
        with pytest.raises(ValueError, match="Missing field"):
            _load_dataclass(_SimplePoint, {})

    def test_load_by_hint_plain_dataclass(self) -> None:
        """_load_by_hint routes plain dataclasses through _load_dataclass."""
        result = _load_by_hint(_SimplePoint, {"x": 4, "y": 2})
        assert isinstance(result, _SimplePoint)
        assert result.x == 4

    def test_try_union_member_dataclass_match(self) -> None:
        """_try_union_member returns a loaded dataclass when valid."""
        result = _try_union_member(_SimplePoint, {"x": 9})
        assert isinstance(result, _SimplePoint)
        assert result.x == 9

    def test_try_union_member_dataclass_no_match(self) -> None:
        """_try_union_member returns _NO_MATCH when dataclass rejects input."""
        result = _try_union_member(_SimplePoint, {"bogus": 1})
        assert result is _NO_MATCH

    def test_load_union_dataclass_tag_match(self) -> None:
        """_load_union resolves by $type tag for plain dataclass members."""
        result = _load_union([_SimplePoint], {"$type": "_SimplePoint", "x": 6})
        assert isinstance(result, _SimplePoint)
        assert result.x == 6


class TestCoerceScalarTypes:
    """_load_by_hint coerces Decimal and date from string representations."""

    def test_load_by_hint_decimal(self) -> None:
        """_load_by_hint converts a string to Decimal for a Decimal hint."""
        result = _load_by_hint(Decimal, "123.45")
        assert result == Decimal("123.45")
        assert isinstance(result, Decimal)

    def test_load_by_hint_date(self) -> None:
        """_load_by_hint parses an ISO string to date for a date hint."""
        result = _load_by_hint(date, "2026-06-01")
        assert result == date(2026, 6, 1)
        assert isinstance(result, date)


class TestLoadUnionHintOptional:
    """_load_by_hint handles Optional (Union with None) types."""

    def test_optional_int_none_returns_none(self) -> None:
        """Optional[int] with None input returns None."""
        hint: type = int | None  # type: ignore[assignment]
        assert _load_by_hint(hint, None) is None

    def test_optional_int_value_returns_int(self) -> None:
        """Optional[int] with int input returns the int."""
        hint: type = int | None  # type: ignore[assignment]
        assert _load_by_hint(hint, 42) == 42

    def test_frozenset_hint_iterable_builds_frozenset(self) -> None:
        """A list of strings with a frozenset[str] hint returns a frozenset."""
        result = _load_by_hint(frozenset[str], ["a", "b", "c"])
        assert result == frozenset({"a", "b", "c"})
        assert isinstance(result, frozenset)

    def test_multi_member_union_dispatches_to_load_union(self) -> None:
        """A Union with multiple non-None members delegates to _load_union."""
        hint: type = _SimplePoint | SeniorityByCount  # type: ignore[assignment]
        result = _load_by_hint(hint, {"x": 5})
        assert isinstance(result, _SimplePoint)
        assert result.x == 5


class TestStrictDecimalFloat:
    """StrictDecimal rejects float inputs via _reject_float validator."""

    def test_ral_override_float_value_rejected(self) -> None:
        """Passing float to a StrictDecimal field raises TypeError."""
        with pytest.raises(TypeError, match="float is not accepted"):
            RalOverride(value=1.5)  # type: ignore[arg-type]
