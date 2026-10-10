"""INPS sick pay bands must be contiguous, ordered and bounded."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.tax.domain.sick_pay import (
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)

_COVERAGE = (SickPayCoverage(covered=True, source="test: every worker"),)


def _rates(bands: list[SickPayBand], **changes: object) -> InpsSickPayRates:
    fields: dict[str, object] = {
        "carenza_days": 3,
        "bands": bands,
        "annual_max_days": 180,
        "coverage": _COVERAGE,
    }
    fields.update(changes)
    return InpsSickPayRates.model_validate(fields)


class TestSickPayBandInvariants:
    """SickPayBand and InpsSickPayRates construction-time validators."""

    def test_sick_pay_band_valid(self) -> None:
        """SickPayBand with day_to >= day_from is accepted."""
        band = SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50"))
        assert band.day_to >= band.day_from

    def test_sick_pay_band_day_to_lt_day_from_raises(self) -> None:
        """SickPayBand rejects day_to < day_from."""
        with pytest.raises(ValidationError, match=r"day_to.*day_from"):
            SickPayBand(day_from=10, day_to=5, rate=Decimal("0.50"))

    def test_inps_sick_pay_rates_valid(self) -> None:
        """InpsSickPayRates with carenza=3 and ordered non-overlapping bands."""
        rates = _rates(
            [
                SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50")),
                SickPayBand(day_from=21, day_to=180, rate=Decimal("0.6667")),
            ],
        )
        assert len(rates.bands) == 2

    def test_inps_sick_pay_rates_without_bands_is_rejected(self) -> None:
        """A table with no indemnity band is incomplete."""
        with pytest.raises(ValidationError, match="bands"):
            _rates([])

    @pytest.mark.parametrize(
        "field", ["carenza_days", "bands", "annual_max_days", "coverage"]
    )
    def test_every_statutory_field_is_required(self, field: str) -> None:
        """No legal value is taken by default."""
        fields: dict[str, object] = {
            "carenza_days": 3,
            "bands": [SickPayBand(day_from=4, day_to=180, rate=Decimal("0.50"))],
            "annual_max_days": 180,
            "coverage": _COVERAGE,
        }
        del fields[field]
        with pytest.raises(ValidationError, match=field):
            InpsSickPayRates.model_validate(fields)

    def test_inps_sick_pay_rates_without_coverage_is_rejected(self) -> None:
        """A table that says nobody is or is not covered is incomplete."""
        band = SickPayBand(day_from=4, day_to=180, rate=Decimal("0.50"))
        with pytest.raises(ValidationError, match="coverage"):
            _rates([band], coverage=())

    def test_inps_sick_pay_rates_first_band_wrong_start_raises(self) -> None:
        """First band must start at carenza_days + 1."""
        with pytest.raises(ValidationError, match="first band day_from"):
            _rates(
                [SickPayBand(day_from=5, day_to=20, rate=Decimal("0.50"))],
            )

    def test_inps_sick_pay_rates_overlapping_bands_raise(self) -> None:
        """Overlapping bands are rejected."""
        with pytest.raises(ValidationError, match="overlaps"):
            _rates(
                [
                    SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50")),
                    SickPayBand(day_from=15, day_to=30, rate=Decimal("0.6667")),
                ],
            )

    def test_inps_sick_pay_rates_gap_between_bands_raises(self) -> None:
        """A gap between consecutive bands is rejected."""
        with pytest.raises(ValidationError, match="gap"):
            _rates(
                [
                    SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50")),
                    SickPayBand(day_from=25, day_to=180, rate=Decimal("0.6667")),
                ],
            )
