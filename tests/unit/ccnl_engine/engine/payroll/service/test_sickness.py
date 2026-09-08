"""Unit tests for the sickness (malattia ordinaria) service."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.ccnl import SicknessRules, SicknessTier
from ccnl_engine.engine.payroll.domain.supplements import SickInput
from ccnl_engine.engine.payroll.service.sickness import (
    _bucket_days,
    _effective_integration_rate,
    compute_sickness,
)
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

    def test_negative_cumulative_sick_days_raises(self) -> None:
        """Negative cumulative_sick_days raises ValueError."""
        with pytest.raises(ValueError, match="cumulative_sick_days must be >= 0"):
            SickInput(sick_days=_D("5"), cumulative_sick_days=_D("-1"))


class TestEffectiveIntegrationRate:
    """_effective_integration_rate tier selection logic."""

    def _rules_with_tiers(self) -> SicknessRules:
        """SicknessRules with 100%→90%→50% tiers (9/3/6 months).

        Returns:
            SicknessRules with three progression tiers.
        """
        return SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            tiers=[
                SicknessTier(month_from=1, month_until=10, integration_rate=_D("1")),
                SicknessTier(month_from=10, month_until=13, integration_rate=_D("0.9")),
                SicknessTier(
                    month_from=13, month_until=None, integration_rate=_D("0.5")
                ),
            ],
        )

    def test_no_tiers_returns_flat_rate(self) -> None:
        """No tiers → always returns full_pay_integration_rate."""
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("0.75"),
        )
        assert _effective_integration_rate(rules, _D("60")) == _D("0.75")

    def test_no_cumulative_returns_flat_rate(self) -> None:
        """Tiers present but cumulative=None → falls back to flat rate."""
        rules = self._rules_with_tiers()
        assert _effective_integration_rate(rules, None) == _D("1")

    def test_first_tier_month_1(self) -> None:
        """Day 0 cumulative → month 1 → tier 100%."""
        rules = self._rules_with_tiers()
        assert _effective_integration_rate(rules, _D("0")) == _D("1")

    def test_first_tier_month_9(self) -> None:
        """Day 240 cumulative (month 9) → still tier 100%."""
        rules = self._rules_with_tiers()
        assert _effective_integration_rate(rules, _D("240")) == _D("1")

    def test_second_tier_month_10(self) -> None:
        """Day 270 cumulative (month 10) → tier 90%."""
        rules = self._rules_with_tiers()
        assert _effective_integration_rate(rules, _D("270")) == _D("0.9")

    def test_third_tier_month_13(self) -> None:
        """Day 360 cumulative (month 13) → open-ended tier 50%."""
        rules = self._rules_with_tiers()
        assert _effective_integration_rate(rules, _D("360")) == _D("0.5")

    def test_lower_month_from_tier_not_preferred(self) -> None:
        """A matching tier with lower month_from is not chosen over a better one.

        Tiers are [month_from=5, month_from=10]; both match month 12.
        The engine should pick the one with higher month_from (10), not 5.
        """
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            tiers=[
                SicknessTier(
                    month_from=10, month_until=None, integration_rate=_D("0.5")
                ),
                SicknessTier(
                    month_from=5, month_until=None, integration_rate=_D("0.8")
                ),
            ],
        )
        # month 12: both tiers match; month_from=10 wins over month_from=5
        assert _effective_integration_rate(rules, _D("330")) == _D("0.5")

    def test_no_matching_tier_falls_back(self) -> None:
        """Tier list that doesn't cover month 1 → flat fallback rate."""
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("0.80"),
            tiers=[
                SicknessTier(month_from=5, month_until=10, integration_rate=_D("0.6")),
            ],
        )
        # Day 0 = month 1 → no tier covers it → fallback
        assert _effective_integration_rate(rules, _D("0")) == _D("0.80")

    def test_compute_sickness_uses_tier(self) -> None:
        """Tier 90% is applied when cumulative puts episode at month 10."""
        rules = self._rules_with_tiers()
        # cumulative=270 days → month 10 → 90% integration
        # 5 sick days: 3 carenza (100%) + 2 band1 (50% INPS)
        # daily_rate = money(2064.88 / 30) = 68.83
        # carenza_pay = 3 * 1.0 * 68.83 = 206.49
        # eff_rate = 0.90; gap = max(0, 0.90 - 0.50) = 0.40
        # post_carenza = 2 * 0.40 * 68.83 = 55.06
        # company = 206.49 + 55.06 = 261.55
        _sd, _cd, inps, company = compute_sickness(
            SickInput(sick_days=_D("5"), cumulative_sick_days=_D("270")),
            rules,
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert inps == _D("68.83")
        assert company == _D("261.55")
