"""Tests for INPS sick-pay band boundary helpers and edge cases."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.contract.domain.ccnl import SicknessRules, SicknessTier
from ccnl_engine.engine.payroll.domain.supplements import SickInput
from ccnl_engine.engine.payroll.service.sickness import (
    _bucket_days,
    _ccnl_tier_boundaries_in_period,
    _inps_boundaries_in_period,
    _tier_rate_segments,
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


class TestBucketDaysFractionalOffset:
    """_bucket_days preserves fractional cumulative offsets without truncation."""

    def test_fractional_offset_not_truncated(self) -> None:
        """Decimal offset 2.5 is used exactly; int() would round to 2.

        offset=2.5: ep_start=2.5, ep_end=2.5+3=5.5.
        carenza [0,3): overlap [2.5, 3) = 0.5 days.
        band1 [3,20): overlap [3, 5.5) = 2.5 days.

        With int(2.5)=2: ep_start=2, ep_end=5, carenza [2,3)=1 day, band1 [3,5)=2 days.
        """
        carenza, bands = _bucket_days(
            _D("3"),
            carenza_days=3,
            bands=[(4, 20), (21, 180)],
            cumulative_offset=_D("2.5"),
        )
        assert carenza == _D("0.5")
        assert bands[0] == _D("2.5")
        assert bands[1] == _ZERO


class TestInpsBoundaryHelpers:
    """_inps_boundaries_in_period and _ccnl_tier_boundaries_in_period."""

    def _std_bands(self) -> list[SickPayBand]:
        """Return standard INPS bands: band1 days 4-20, band2 21-180.

        Returns:
            Two-band list matching the statutory INPS structure.
        """
        return [
            SickPayBand(day_from=4, day_to=20, rate=_D("0.50")),
            SickPayBand(day_from=21, day_to=180, rate=_D("0.6667")),
        ]

    def test_inps_boundary_inside_period(self) -> None:
        """Band2 starts at episode day 20 (day_from=21 → day 20 in 0-based).

        period [17, 24): day 20 is strictly inside → returned as boundary.
        """
        result = _inps_boundaries_in_period(self._std_bands(), _D("17"), _D("24"))
        assert _D("20") in result

    def test_inps_boundary_at_period_edge_excluded(self) -> None:
        """Boundary exactly at period_start or period_end is not returned."""
        # band2 boundary at day 20: period [20, 30) → day 20 == period_start
        result = _inps_boundaries_in_period(self._std_bands(), _D("20"), _D("30"))
        assert _D("20") not in result

    def test_inps_no_boundary_inside(self) -> None:
        """Period [4, 19): both boundaries (3 and 20) are outside → empty set."""
        result = _inps_boundaries_in_period(self._std_bands(), _D("4"), _D("19"))
        assert result == set()

    def test_ccnl_tier_boundary_inside_period(self) -> None:
        """CCNL tier boundary at month 10 = day 270 is inside [265, 280)."""
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            tiers=[  # type: ignore[arg-type]
                SicknessTier(month_from=1, month_until=10, integration_rate=_D("1")),
                SicknessTier(
                    month_from=10, month_until=None, integration_rate=_D("0.9")
                ),
            ],
        )
        result = _ccnl_tier_boundaries_in_period(rules, _D("265"), _D("280"))
        assert _D("270") in result

    def test_ccnl_tier_boundary_at_edge_excluded(self) -> None:
        """Tier boundary at day 270 == period_start is not returned."""
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            tiers=[  # type: ignore[arg-type]
                SicknessTier(month_from=1, month_until=10, integration_rate=_D("1")),
                SicknessTier(
                    month_from=10, month_until=None, integration_rate=_D("0.9")
                ),
            ],
        )
        result = _ccnl_tier_boundaries_in_period(rules, _D("270"), _D("280"))
        assert _D("270") not in result


class TestTierRateSegmentsWithInpsBoundary:
    """_tier_rate_segments splits at INPS band boundaries when sick_pay_rates given."""

    def test_inps_boundary_split(self) -> None:
        """Period crossing INPS band1→band2 boundary is split at day 20.

        Tiers: month 1-99 at 100% (no tier crossing in this range).
        Period: cumulative=17, sick_days=6 → episode days [17, 23).
        INPS band1→band2 boundary at day 20 (0-based start of band2).

        Expected segments:
          - [17, 20): 3 days at rate=100%
          - [20, 23): 3 days at rate=100%
        Both segments have the same integration rate, but the split confirms
        that INPS boundary detection fires.  The segment list has length 2.
        """
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            tiers=[  # type: ignore[arg-type]
                SicknessTier(month_from=1, month_until=99, integration_rate=_D("1")),
            ],
        )
        rates = InpsSickPayRates(
            carenza_days=3,
            bands=[
                SickPayBand(day_from=4, day_to=20, rate=_D("0.50")),
                SickPayBand(day_from=21, day_to=180, rate=_D("0.6667")),
            ],
        )
        segments = _tier_rate_segments(_D("6"), _D("17"), rules, sick_pay_rates=rates)
        assert len(segments) == 2
        assert segments[0] == (_D("3"), _D("1"))
        assert segments[1] == (_D("3"), _D("1"))

    def test_no_sick_pay_rates_no_inps_split(self) -> None:
        """Without sick_pay_rates, INPS boundaries are not added.

        Same period as above: only tier boundaries considered.
        Single tier covers whole period → one segment returned.
        """
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            tiers=[  # type: ignore[arg-type]
                SicknessTier(month_from=1, month_until=99, integration_rate=_D("1")),
            ],
        )
        segments = _tier_rate_segments(_D("6"), _D("17"), rules)
        assert len(segments) == 1
        assert segments[0] == (_D("6"), _D("1"))


class TestBeyondInpsBandCoverage:
    """Company integration for days within comporto but beyond the last INPS band.

    When no tiers are present, days past the last INPS band end should still
    receive company integration at the effective rate (INPS contributes 0).
    """

    def test_no_tier_beyond_band_pays_full_eff_rate(self) -> None:
        """10 sick days at episode 181-190: INPS rate = 0, company = eff_rate.

        comporto = 360 days; cumulative = 180; sick_days = 10.
        All 10 days are beyond the last INPS band (day_to=180).

        INPS indemnity = 0 (no band covers days 181-190).
        Company integration = 10 * eff_rate * daily_rate.
        """
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            max_duration_days=360,
        )
        sick_input = SickInput(sick_days=_D("10"), cumulative_sick_days=_D("180"))
        gross_monthly = _D("3000.00")
        daily = gross_monthly / _D("30")
        _, _, inps, company = compute_sickness(
            sick_input, rules, _standard_sick_pay_rates(), gross_monthly
        )
        assert inps == _D("0.00")
        assert company == _D("0.00") + 10 * _D("1") * daily

    def test_no_tier_equivalence_single_vs_split(self) -> None:
        """One 20-day period starting at 170 equals two 10-day periods.

        Episode days 171-190 span both within (171-180) and beyond (181-190)
        the last INPS band. The same total must be produced whether the period
        is computed in one call or two sequential calls.

        comporto = 360, eff_rate = 1.0 (full pay integration).
        """
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            max_duration_days=360,
        )
        rates = _standard_sick_pay_rates()
        gross_monthly = _D("3000.00")

        _, _, inps_1, company_1 = compute_sickness(
            SickInput(sick_days=_D("20"), cumulative_sick_days=_D("170")),
            rules,
            rates,
            gross_monthly,
        )
        _, _, inps_a, company_a = compute_sickness(
            SickInput(sick_days=_D("10"), cumulative_sick_days=_D("170")),
            rules,
            rates,
            gross_monthly,
        )
        _, _, inps_b, company_b = compute_sickness(
            SickInput(sick_days=_D("10"), cumulative_sick_days=_D("180")),
            rules,
            rates,
            gross_monthly,
        )
        assert inps_1 == inps_a + inps_b
        assert company_1 == company_a + company_b


class TestInpsBandEndBoundary:
    """_inps_boundaries_in_period includes band END positions."""

    def test_band_end_inside_period_is_returned(self) -> None:
        """Band2 ends at episode day 180 (day_to=180 → boundary 180).

        Period [170, 190): day 180 is strictly inside → returned as boundary.
        """
        bands = [
            SickPayBand(day_from=4, day_to=20, rate=_D("0.50")),
            SickPayBand(day_from=21, day_to=180, rate=_D("0.6667")),
        ]
        result = _inps_boundaries_in_period(bands, _D("170"), _D("190"))
        assert _D("180") in result

    def test_band_end_at_period_edge_excluded(self) -> None:
        """Band end at period_end is excluded (open interval).

        Period [170, 180): day 180 == period_end → not returned.
        """
        bands = [
            SickPayBand(day_from=4, day_to=20, rate=_D("0.50")),
            SickPayBand(day_from=21, day_to=180, rate=_D("0.6667")),
        ]
        result = _inps_boundaries_in_period(bands, _D("170"), _D("180"))
        assert _D("180") not in result


class TestCumulativeNoneEquivalence:
    """cumulative_sick_days=None and Decimal(0) must produce identical results."""

    def _rules_with_tiers(self) -> SicknessRules:
        """SicknessRules with 100%→90% tiers starting at month 10.

        Returns:
            SicknessRules with a two-tier progression and 360-day comporto.
        """
        return SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
            max_duration_days=360,
            tiers=[  # type: ignore[arg-type]
                SicknessTier(month_from=1, month_until=10, integration_rate=_D("1")),
                SicknessTier(
                    month_from=10, month_until=None, integration_rate=_D("0.9")
                ),
            ],
        )

    def test_none_equals_zero_no_tiers(self) -> None:
        """Without tiers, None and Decimal(0) produce identical results."""
        rules = SicknessRules(
            carenza_integration_rate=_D("1"),
            full_pay_integration_rate=_D("1"),
        )
        rates = _standard_sick_pay_rates()
        gross = _D("3000")
        sick_days = _D("30")

        result_none = compute_sickness(
            SickInput(sick_days=sick_days, cumulative_sick_days=None),
            rules,
            rates,
            gross_monthly=gross,
        )
        result_zero = compute_sickness(
            SickInput(sick_days=sick_days, cumulative_sick_days=_D("0")),
            rules,
            rates,
            gross_monthly=gross,
        )
        assert result_none == result_zero

    def test_none_equals_zero_with_tiers_in_first_segment(self) -> None:
        """With tiers, None and Decimal(0) both start in tier 1 and agree."""
        rules = self._rules_with_tiers()
        rates = _standard_sick_pay_rates()
        gross = _D("3000")
        sick_days = _D("10")  # well within the first tier

        result_none = compute_sickness(
            SickInput(sick_days=sick_days, cumulative_sick_days=None),
            rules,
            rates,
            gross_monthly=gross,
        )
        result_zero = compute_sickness(
            SickInput(sick_days=sick_days, cumulative_sick_days=_D("0")),
            rules,
            rates,
            gross_monthly=gross,
        )
        assert result_none == result_zero

    def test_none_equals_zero_crossing_tier_boundary(self) -> None:
        """None and Decimal(0) agree even when the episode crosses a tier boundary.

        Tier 1 ends at month 10 = day 270.
        sick_days=100 starting at cumulative=0 crosses that boundary (days 0-100).
        """
        rules = self._rules_with_tiers()
        rates = _standard_sick_pay_rates()
        gross = _D("3000")
        sick_days = _D("100")

        result_none = compute_sickness(
            SickInput(sick_days=sick_days, cumulative_sick_days=None),
            rules,
            rates,
            gross_monthly=gross,
        )
        result_zero = compute_sickness(
            SickInput(sick_days=sick_days, cumulative_sick_days=_D("0")),
            rules,
            rates,
            gross_monthly=gross,
        )
        assert result_none == result_zero
