"""Somma esente bands and rules validate ordering and rates."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.tax.domain.credit_rules import SommaEsenteBand, SommaEsenteRules

_VALID_BAND_LIST: list[SommaEsenteBand] = [
    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071")),
    SommaEsenteBand(up_to=Decimal(15000), rate=Decimal("0.053")),
    SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.048")),
]


class TestSommaEsenteBand:
    """SommaEsenteBand rejects negative and >1 rates."""

    def test_negative_rate_raises(self) -> None:
        """Rate < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("-0.05"))

    def test_rate_above_one_raises(self) -> None:
        """Rate > 1 must raise ValidationError."""
        with pytest.raises(ValidationError):
            SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("1.5"))

    def test_valid_band_accepted(self) -> None:
        """Valid rate in [0, 1] is accepted."""
        b = SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071"))
        assert b.rate == Decimal("0.071")


class TestSommaEsenteRules:
    """SommaEsenteRules: empty, duplicate, non-ascending bands are rejected."""

    def test_empty_bands_raises(self) -> None:
        """Empty bands list must raise ValidationError."""
        with pytest.raises(ValidationError):
            SommaEsenteRules(bands=[])

    def test_non_ascending_bands_raises(self) -> None:
        """Bands with non-ascending up_to must raise ValidationError."""
        with pytest.raises(ValidationError, match="strictly ascending"):
            SommaEsenteRules(
                bands=[
                    SommaEsenteBand(up_to=Decimal(15000), rate=Decimal("0.053")),
                    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071")),
                ]
            )

    def test_duplicate_up_to_raises(self) -> None:
        """Bands with equal up_to must raise ValidationError."""
        with pytest.raises(ValidationError, match="strictly ascending"):
            SommaEsenteRules(
                bands=[
                    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071")),
                    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.053")),
                ]
            )

    def test_single_band_accepted(self) -> None:
        """A single band (no ordering to check) is accepted."""
        r = SommaEsenteRules(
            bands=[SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.05"))]
        )
        assert len(r.bands) == 1

    def test_valid_bands_accepted(self) -> None:
        """Three strictly-ascending bands are accepted."""
        r = SommaEsenteRules(bands=_VALID_BAND_LIST)
        assert len(r.bands) == 3
