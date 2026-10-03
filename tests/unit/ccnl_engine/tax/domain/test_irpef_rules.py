"""IRPEF bracket and deduction breakpoint models validate their bounds."""

from decimal import Decimal

import pytest

from ccnl_engine.shared.domain.primitives import Bracket
from ccnl_engine.tax.domain.irpef_rules import IrpefBracket


class TestBracketRateConstraint:
    """Bracket.__post_init__ rejects rates outside [0, 1]."""

    def test_valid_rate_accepted(self) -> None:
        """Rate in [0, 1] is accepted."""
        b = Bracket(up_to=Decimal(28000), rate=Decimal("0.23"))
        assert b.rate == Decimal("0.23")

    def test_zero_rate_accepted(self) -> None:
        """rate=0 is on the boundary and must be accepted."""
        b = Bracket(up_to=None, rate=Decimal(0))
        assert b.rate == Decimal(0)

    def test_one_rate_accepted(self) -> None:
        """rate=1 is on the boundary and must be accepted."""
        b = Bracket(up_to=None, rate=Decimal(1))
        assert b.rate == Decimal(1)

    def test_negative_rate_raises(self) -> None:
        """Rate < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="\\[0, 1\\]"):
            Bracket(up_to=None, rate=Decimal("-0.23"))

    def test_rate_above_one_raises(self) -> None:
        """Rate > 1 must raise ValueError."""
        with pytest.raises(ValueError, match="\\[0, 1\\]"):
            Bracket(up_to=None, rate=Decimal("1.01"))


class TestIrpefBracket:
    """Unit tests for IrpefBracket construction."""

    def test_bounded_bracket(self) -> None:
        """A bracket with a finite up_to is accepted."""
        b = IrpefBracket(up_to=Decimal(28000), rate=Decimal("0.23"))
        assert b.up_to == Decimal(28000)

    def test_unbounded_bracket(self) -> None:
        """A bracket with up_to=None (unbounded) is accepted."""
        b = IrpefBracket(up_to=None, rate=Decimal("0.43"))
        assert b.up_to is None
