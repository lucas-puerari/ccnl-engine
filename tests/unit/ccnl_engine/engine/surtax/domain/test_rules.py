"""Unit tests for surtax domain validation."""

from decimal import Decimal

import pytest

from ccnl_engine.engine.primitives import Bracket
from ccnl_engine.engine.surtax.domain.rules import (
    ComunaleEntry,
    RegionaleEntry,
    _validate_surtax_brackets,
)


def _b(up_to: float | None, rate: float) -> Bracket:
    return Bracket(
        up_to=Decimal(str(up_to)) if up_to is not None else None,
        rate=Decimal(str(rate)),
    )


class TestValidateSurtaxBrackets:
    """Tests for _validate_surtax_brackets."""

    def test_empty_raises(self) -> None:
        """Empty list is rejected."""
        with pytest.raises(ValueError, match="must not be empty"):
            _validate_surtax_brackets([], "TestLabel")

    def test_non_last_none_raises(self) -> None:
        """Non-final bracket with up_to=None is rejected."""
        brackets = [_b(None, 0.01), _b(None, 0.02)]
        with pytest.raises(ValueError, match="only the last bracket"):
            _validate_surtax_brackets(brackets, "TestLabel")

    def test_non_ascending_raises(self) -> None:
        """Non-ascending up_to values are rejected."""
        brackets = [_b(28000, 0.01), _b(15000, 0.02), _b(None, 0.03)]
        with pytest.raises(ValueError, match="strictly ascending"):
            _validate_surtax_brackets(brackets, "TestLabel")

    def test_last_bounded_raises(self) -> None:
        """Last bracket with a finite up_to is rejected."""
        brackets = [_b(15000, 0.01), _b(28000, 0.02)]
        with pytest.raises(ValueError, match="last bracket must be unbounded"):
            _validate_surtax_brackets(brackets, "TestLabel")

    def test_valid_single_bracket(self) -> None:
        """Single unbounded bracket is accepted."""
        _validate_surtax_brackets([_b(None, 0.008)], "TestLabel")

    def test_valid_multi_bracket(self) -> None:
        """Well-formed 4-bracket schedule is accepted."""
        brackets = [
            _b(15000, 0.004),
            _b(28000, 0.006),
            _b(50000, 0.007),
            _b(None, 0.008),
        ]
        _validate_surtax_brackets(brackets, "TestLabel")


class TestComunaleEntryValidation:
    """Model-level bracket validation for ComunaleEntry."""

    def test_multi_none_brackets_rejected(self) -> None:
        """Multiple up_to=None brackets are rejected at model level."""
        with pytest.raises(ValueError, match="only the last bracket"):
            ComunaleEntry(
                nome="Test",
                brackets=[_b(None, 0.006), _b(None, 0.008)],
            )

    def test_duplicate_limit_rejected(self) -> None:
        """Duplicate up_to values are rejected at model level."""
        with pytest.raises(ValueError, match="strictly ascending"):
            ComunaleEntry(
                nome="Test",
                brackets=[
                    _b(15000, 0.004),
                    _b(15000, 0.006),
                    _b(None, 0.008),
                ],
            )

    def test_valid_entry_accepted(self) -> None:
        """Well-formed entry with 4 brackets is accepted."""
        entry = ComunaleEntry(
            nome="Roma",
            brackets=[
                _b(15000, 0.004),
                _b(28000, 0.006),
                _b(50000, 0.007),
                _b(None, 0.008),
            ],
        )
        assert len(entry.brackets) == 4


class TestRegionaleEntryValidation:
    """Model-level bracket validation for RegionaleEntry."""

    def test_multi_none_rejected(self) -> None:
        """Multiple up_to=None brackets are rejected."""
        with pytest.raises(ValueError, match="only the last bracket"):
            RegionaleEntry(brackets=[_b(None, 0.011), _b(None, 0.014)])

    def test_last_bounded_rejected(self) -> None:
        """Last bracket with finite up_to is rejected."""
        with pytest.raises(ValueError, match="last bracket must be unbounded"):
            RegionaleEntry(brackets=[_b(15000, 0.011), _b(28000, 0.014)])

    def test_valid_flat_rate(self) -> None:
        """Single flat-rate bracket is accepted."""
        entry = RegionaleEntry(brackets=[_b(None, 0.014)])
        assert len(entry.brackets) == 1
