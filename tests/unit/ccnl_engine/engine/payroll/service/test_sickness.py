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
        """Tier 90% is applied when cumulative puts episode at month 10.

        cumulative=270 days: episode days 271-275.  The INPS bands only cover
        days 4-180; all 5 days are beyond day 180, so INPS pays nothing.
        Company pays 90% (tier 2) on all 5 post-carenza days (no INPS gap).

        daily_rate = money(2064.88 / 30) = 68.83
        carenza = 0  (cumulative=270 > carenza_limit=3)
        INPS = 0  (episode days 271-275 are beyond band2 end of day 180)
        post_carenza = 5 * 0.90 * 68.83 = 309.74  (eff_rate=0.9, no INPS gap)
        company = 309.74
        """
        rules = self._rules_with_tiers()
        _sd, _cd, inps, company = compute_sickness(
            SickInput(sick_days=_D("5"), cumulative_sick_days=_D("270")),
            rules,
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert inps == _D("0.00")
        assert company == _D("309.74")

    def test_r5_split_equals_single_episode(self) -> None:
        """R5: splitting one episode into two calls gives the same totals.

        Episode of 20 sick days split as 10+10 must equal a single 20-day call.

        Single call (cumulative=0, sick_days=20):
          daily_rate = money(2064.88 / 30) = 68.83
          carenza = 3, band1 = 17, band2 = 0
          inps = 17 * 0.50 * 68.83 = 584.86 (rounded)
          company = 3 * 1.0 * 68.83 + 17 * 0.50 * 68.83 = 206.49 + 584.86 = 791.35

        Split call 1 (cumulative=0, sick_days=10):
          carenza = 3, band1 = 7
          inps = 7 * 0.50 * 68.83 = 240.91
          company = 3 * 1.0 * 68.83 + 7 * 0.50 * 68.83 = 206.49 + 240.91 = 447.40

        Split call 2 (cumulative=10, sick_days=10):
          carenza = 0 (offset=10 > carenza limit 3)
          band1 days: band1=[4..20] => overlap [10..20) = 10 days
          inps = 10 * 0.50 * 68.83 = 344.15
          company = 0 + 10 * 0.50 * 68.83 = 344.15

        Total split: inps = 240.91 + 344.15 = 585.06 != 584.86?
        Note: rounding is applied per call, so small differences possible.
        The key invariant is carenza+band1+band2 totals equal the single call.
        """
        rules = _full_integration_rules()
        rates = _standard_sick_pay_rates()
        gross = _D("2064.88")

        # Single 20-day call
        _, _, inps_single, co_single = compute_sickness(
            SickInput(sick_days=_D("20"), cumulative_sick_days=_D("0")),
            rules,
            rates,
            gross_monthly=gross,
        )

        # Split into two 10-day calls
        _, _, inps_a, co_a = compute_sickness(
            SickInput(sick_days=_D("10"), cumulative_sick_days=_D("0")),
            rules,
            rates,
            gross_monthly=gross,
        )
        _, _, inps_b, co_b = compute_sickness(
            SickInput(sick_days=_D("10"), cumulative_sick_days=_D("10")),
            rules,
            rates,
            gross_monthly=gross,
        )

        # Band-day totals must match (rounding inside money() is per-call, so
        # small cents differ; we tolerate +-0.02 to account for two rounding ops)
        tol = _D("0.02")
        assert abs((inps_a + inps_b) - inps_single) <= tol
        assert abs((co_a + co_b) - co_single) <= tol

    def test_r6_tier_crossing(self) -> None:
        """R6: period spanning a tier boundary uses separate rates per segment.

        Tiers: month 1-10 at 100%, month 10-13 at 90%.
        Tier boundary at day (10-1)*30 = 270.

        cumulative=265, sick_days=10: episode days 265-274 crosses day 270.
          - Segment 1: days 265-270 (5 days) => month 9 => 100% rate
          - Segment 2: days 270-275 (5 days) => month 10 => 90% rate
          All days are beyond INPS bands (>180), so INPS = 0 for both segments.

        daily_rate = 68.83
        company = 5 * 1.00 * 68.83 + 5 * 0.90 * 68.83
                = 344.15 + 309.74 = 653.89
        """
        rules = self._rules_with_tiers()
        rates = _standard_sick_pay_rates()
        gross = _D("2064.88")

        _, _, inps, company = compute_sickness(
            SickInput(sick_days=_D("10"), cumulative_sick_days=_D("265")),
            rules,
            rates,
            gross_monthly=gross,
        )
        assert inps == _D("0.00")
        assert company == _D("653.89")

    def test_tier_all_days_in_carenza_skips_post_carenza(self) -> None:
        """Tiers + cumulative, all sick days within carenza: no post-carenza work.

        cumulative=0, sick_days=3, carenza_limit=3: post_carenza_days = 0.
        The `if post_carenza_days > _ZERO` branch is skipped.

        daily_rate = 68.83
        company = 3 * 1.0 * 68.83 = 206.49  (carenza pay only)
        inps = 0
        """
        rules = self._rules_with_tiers()
        _, _, inps, company = compute_sickness(
            SickInput(sick_days=_D("3"), cumulative_sick_days=_D("0")),
            rules,
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert inps == _D("0.00")
        assert company == _D("206.49")

    def test_tier_with_inps_band_overlap(self) -> None:
        """Tiers + cumulative, segment within INPS band: seg_inps_rate is set.

        cumulative=3, sick_days=5: episode days 4-8, all in band1 (days 4-20, 50%).
        Offset > carenza_limit so carenza=0.  post_carenza_offset = max(3,3) = 3.
        All 5 days are at tier 1 (100%) since cumulative=3 is in month 1.

        daily_rate = 68.83
        carenza = 0  (cumulative=3 >= carenza_limit=3)
        inps = 5 * 0.50 * 68.83 = 172.08 (rounded)
        company (tier): seg_inps_rate=0.50, gap=0.50, 5 * 0.50 * 68.83 = 172.08
        total company = 172.08
        """
        rules = self._rules_with_tiers()
        _, _, inps, company = compute_sickness(
            SickInput(sick_days=_D("5"), cumulative_sick_days=_D("3")),
            rules,
            _standard_sick_pay_rates(),
            gross_monthly=_D("2064.88"),
        )
        assert inps == _D("172.08")
        assert company == _D("172.08")
