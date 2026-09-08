"""Unit tests for the sickness (malattia ordinaria) service."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.contract.domain.ccnl import SicknessRules
from ccnl_engine.engine.payroll.domain.supplements import SickInput
from ccnl_engine.engine.payroll.service.sickness import _bucket_days, compute_sickness
from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates, SickPayBand

_ZERO = Decimal(0)
_D = Decimal


def _standard_sick_pay_rates() -> InpsSickPayRates:
    """Build standard INPS sick-pay rates (2001 statutory structure).

    Returns:
        An :class:`InpsSickPayRates` with carenza=3, band1 50%, band2 66.67%.
    """
    return InpsSickPayRates(
        carenza_days=3,
        bands=[
            SickPayBand(day_from=4, day_to=20, rate=_D("0.50")),
            SickPayBand(day_from=21, day_to=180, rate=_D("0.6667")),
        ],
    )


def _full_integration_rules() -> SicknessRules:
    """Build CCNL sickness rules with 100% integration (e.g. Federmeccanica).

    Returns:
        A :class:`SicknessRules` with full carenza and pay integration.
    """
    return SicknessRules(
        carenza_integration_rate=_D("1"),
        full_pay_integration_rate=_D("1"),
    )


class TestBucketDays:
    """_bucket_days correctly splits sick days across carenza and rate bands."""

    def test_all_in_carenza(self) -> None:
        """2 sick days: fully within carenza (3-day wait)."""
        carenza, bands = _bucket_days(
            _D("2"), carenza_days=3, bands=[(4, 20), (21, 180)]
        )
        assert carenza == _D("2")
        assert bands[0] == _ZERO
        assert bands[1] == _ZERO

    def test_exactly_carenza(self) -> None:
        """3 sick days: fills carenza exactly, no band days."""
        carenza, bands = _bucket_days(
            _D("3"), carenza_days=3, bands=[(4, 20), (21, 180)]
        )
        assert carenza == _D("3")
        assert bands[0] == _ZERO
        assert bands[1] == _ZERO

    def test_one_band1_day(self) -> None:
        """4 sick days: 3 carenza + 1 band1 day."""
        carenza, bands = _bucket_days(
            _D("4"), carenza_days=3, bands=[(4, 20), (21, 180)]
        )
        assert carenza == _D("3")
        assert bands[0] == _D("1")
        assert bands[1] == _ZERO

    def test_full_band1(self) -> None:
        """20 sick days: 3 carenza + 17 band1 days (days 4-20)."""
        carenza, bands = _bucket_days(
            _D("20"), carenza_days=3, bands=[(4, 20), (21, 180)]
        )
        assert carenza == _D("3")
        assert bands[0] == _D("17")
        assert bands[1] == _ZERO

    def test_partial_band2(self) -> None:
        """25 sick days: 3 carenza + 17 band1 + 5 band2."""
        carenza, bands = _bucket_days(
            _D("25"), carenza_days=3, bands=[(4, 20), (21, 180)]
        )
        assert carenza == _D("3")
        assert bands[0] == _D("17")
        assert bands[1] == _D("5")

    def test_zero_days(self) -> None:
        """Zero sick days: all buckets are zero."""
        carenza, bands = _bucket_days(_ZERO, carenza_days=3, bands=[(4, 20), (21, 180)])
        assert carenza == _ZERO
        assert all(b == _ZERO for b in bands)


class TestComputeSickness:
    """compute_sickness output values for the standard INPS rate structure."""

    def test_zero_sick_days_returns_all_zero(self) -> None:
        """Zero sick days: all outputs are zero."""
        sick_days, carenza, inps, company = compute_sickness(
            SickInput(sick_days=_ZERO),
            _full_integration_rules(),
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert sick_days == _ZERO
        assert carenza == _ZERO
        assert inps == _ZERO
        assert company == _ZERO

    def test_only_carenza_days(self) -> None:
        """3 days sick: only carenza, no INPS indemnity; company pays 100%."""
        # daily_rate = money(2064.88 / 30) = 68.83
        # carenza_pay = 3 * 1.0 * 68.83 = 206.49
        sick_days, carenza, inps, company = compute_sickness(
            SickInput(sick_days=_D("3")),
            _full_integration_rules(),
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert sick_days == _D("3")
        assert carenza == _D("3")
        assert inps == _ZERO
        assert company == _D("206.49")

    def test_5_days_sick_carenza_plus_band1(self) -> None:
        """5 days: 3 carenza + 2 band1 (50%), integration at 100%.

        daily_rate = money(2064.88/30) = 68.83
        inps = 2 * 0.50 * 68.83 = 68.83
        company = 3 * 1.0 * 68.83 + 2 * 0.50 * 68.83 = 206.49 + 68.83 = 275.32
        """
        sick_days, carenza, inps, company = compute_sickness(
            SickInput(sick_days=_D("5")),
            _full_integration_rules(),
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert sick_days == _D("5")
        assert carenza == _D("3")
        assert inps == _D("68.83")
        assert company == _D("275.32")

    def test_25_days_both_bands(self) -> None:
        """25 days: 3 carenza + 17 band1 + 5 band2.

        daily_rate = 68.83
        inps = 17*0.50*68.83 + 5*0.6667*68.83 = 814.50 (rounded)
        company = 206.49 + 17*0.50*68.83 + 5*0.3333*68.83 = 906.25
        """
        sick_days, carenza, inps, company = compute_sickness(
            SickInput(sick_days=_D("25")),
            _full_integration_rules(),
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert sick_days == _D("25")
        assert carenza == _D("3")
        assert inps == _D("814.50")
        assert company == _D("906.25")

    def test_partial_carenza_integration(self) -> None:
        """CCNL with 0% carenza integration: company pays 0 during carenza."""
        rules = SicknessRules(
            carenza_integration_rate=_D("0"),
            full_pay_integration_rate=_D("1"),
        )
        _sick_days, carenza, inps, company = compute_sickness(
            SickInput(sick_days=_D("3")),
            rules,
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert carenza == _D("3")
        assert inps == _ZERO
        assert company == _ZERO

    def test_ccnl_below_inps_rate_clamps_to_zero(self) -> None:
        """CCNL integration rate below INPS rate: company supplement is zero.

        full_pay_integration_rate=0.40 < band1 INPS rate 0.50.
        Company gap = max(0, 0.40 - 0.50) = 0, so integration = 0 for band1.
        """
        rules = SicknessRules(
            carenza_integration_rate=_D("0"),
            full_pay_integration_rate=_D("0.40"),
        )
        _sick_days, _carenza, inps, company = compute_sickness(
            SickInput(sick_days=_D("5")),
            rules,
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert inps == _D("68.83")  # INPS still pays 50% of band1 days
        assert company == _ZERO  # CCNL rate < INPS rate → no integration
