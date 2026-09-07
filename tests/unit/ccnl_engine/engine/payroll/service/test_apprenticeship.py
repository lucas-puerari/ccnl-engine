"""Tests for engine/compute/apprenticeship — track selection and pay chains."""

from __future__ import annotations

import copy

import pytest

from ccnl_engine.engine.contract.domain.apprenticeship import ApprenticeshipPeriod
from ccnl_engine.engine.contract.domain.ccnl import CCNL
from ccnl_engine.engine.payroll.domain.employment import Apprentice
from ccnl_engine.engine.payroll.service.apprenticeship import _find_period_index
from ccnl_engine.engine.payroll.service.orchestrator import compute
from tests.helpers import make_ccnl_dict, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _RULES,
    _allowance,
    _build_ccnl,
    _req,
    _series,
)

_DEFAULT_CCNL = _build_ccnl()
_DEFAULT_CCNL_UC = _build_ccnl("under_classification")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


class TestFindPeriodIndex:
    """Direct unit tests for _find_period_index()."""

    def test_not_found_raises(self) -> None:
        """months_elapsed before the first period raises ValueError."""
        periods = [
            ApprenticeshipPeriod(
                months_from=10, months_until=None, percentage=_D("0.8")
            )
        ]
        with pytest.raises(ValueError, match="months_elapsed"):
            _find_period_index(periods, months_elapsed=5)


# ---------------------------------------------------------------------------
# Apprentice — percentage
# ---------------------------------------------------------------------------


class TestComputeApprenticePercentage:
    """Percentage track dispatch."""

    def test_basic(self) -> None:
        """Apprentice salary = destination-level salary * pct (0.80)."""
        r = compute(
            _DEFAULT_CCNL, _RULES, _req(employment=Apprentice(months_elapsed=0))
        )

        assert r.apprenticeship_pct == _D("0.80")
        assert r.apprenticeship_under_level_code is None
        assert r.base_monthly == _D("800.00")
        assert r.gross_annual == _D("9600.00")
        assert r.employment_type == "apprentice"

    def test_apprentice_contribution_rates(self) -> None:
        """Apprentices use the reduced statutory INPS rates."""
        r = compute(
            _DEFAULT_CCNL, _RULES, _req(employment=Apprentice(months_elapsed=0))
        )
        assert r.inps_employee_annual == _D("560.64")  # 9600 * 0.0584
        assert r.inps_employer_annual == _D("1114.56")  # 9600 * 0.1161

    def test_small_firm_rates_by_months(self) -> None:
        """Small-firm employer rate steps at 12 and 24 months."""
        rules = make_year_rules(
            apprentice={
                "employee_rate": "0.0584",
                "employee_ivs_rate": "0.0584",
                "employer_rate_months_0_11": "0.0311",
                "employer_ivs_rate_months_0_11": "0.0150",
                "employer_rate_months_12_23": "0.0461",
                "employer_ivs_rate_months_12_23": "0.0300",
                "employer_rate_after": "0.1161",
                "employer_ivs_rate_after": "0.1000",
            }
        )
        rates = [
            compute(
                _DEFAULT_CCNL, rules, _req(employment=Apprentice(months_elapsed=m))
            ).inps_employer_annual
            for m in (0, 11, 12, 23, 24)
        ]
        assert rates == [
            _D("298.56"),
            _D("298.56"),
            _D("442.56"),
            _D("442.56"),
            _D("1114.56"),
        ]

    def test_seniority_not_accrued_without_apprentice_amount(self) -> None:
        """Without apprentice_amount the level increment does not apply."""
        r = compute(
            _DEFAULT_CCNL,
            _RULES,
            _req(employment=Apprentice(months_elapsed=0), seniority_count=2),
        )
        assert r.seniority_monthly == _D("0.00")

    def test_apprentice_amount(self) -> None:
        """apprentice_amount replaces the level increment for apprentices."""
        ccnl = _build_ccnl(**{
            "parameters.seniority_increments.apprentice_amount": _series("6.00")
        })
        r = compute(
            ccnl,
            _RULES,
            _req(employment=Apprentice(months_elapsed=0), seniority_count=2),
        )
        assert r.seniority_monthly == _D("9.60")  # 12 * 0.80

    def test_negotiated_ral(self) -> None:
        """RalOverride is the actual apprentice salary; no further scaling."""
        ral = _D("20000.00")
        r = compute(
            _DEFAULT_CCNL,
            _RULES,
            _req(employment=Apprentice(months_elapsed=0), negotiated_ral=ral),
        )

        assert r.gross_annual == _D("20000.00")
        assert r.gross_monthly == _D("1666.67")

    def test_negotiated_destination_ral(self) -> None:
        """DestinationRalOverride * apprenticeship_pct yields the actual pay."""
        ral = _D("20000.00")
        r = compute(
            _DEFAULT_CCNL,
            _RULES,
            _req(
                employment=Apprentice(months_elapsed=0),
                negotiated_destination_ral=ral,
            ),
        )

        assert r.gross_annual == _D("16000.00")  # 20000 * 0.80
        assert r.gross_monthly == _D("1333.33")

    def test_negotiated_destination_ral_requires_percentage_track(self) -> None:
        """DestinationRalOverride on an under-classification track raises."""
        with pytest.raises(ValueError, match="under-classification"):
            compute(
                _DEFAULT_CCNL_UC,
                _RULES,
                _req(
                    employment=Apprentice(months_elapsed=0),
                    negotiated_destination_ral=_D("20000.00"),
                ),
            )

    def test_level_without_track_raises(self) -> None:
        """A destination level not covered by any track must raise ValueError."""
        with pytest.raises(ValueError, match=r"eligible destination levels: \['4'\]"):
            compute(
                _DEFAULT_CCNL,
                _RULES,
                _req(level_code="3", employment=Apprentice(months_elapsed=0)),
            )

    def test_no_tracks_raises(self) -> None:
        """A CCNL without apprenticeship tracks reports its coverage status."""
        ccnl = _build_ccnl("none")
        with pytest.raises(ValueError, match=r"coverage\.layer_2 is partial"):
            compute(ccnl, _RULES, _req(employment=Apprentice(months_elapsed=0)))

    def test_ambiguous_tracks_require_name(self) -> None:
        """Two tracks on one level: the caller must name the track."""
        second = copy.deepcopy(_DEFAULT_CCNL.apprenticeship[0].model_dump())
        second["name"] = "gruppo_2"
        second["periods"][0]["percentage"] = "0.70"
        data = make_ccnl_dict()
        data["apprenticeship"].append(second)
        ccnl = CCNL.model_validate(data)
        with pytest.raises(ValueError, match=r"set Apprentice\.track"):
            compute(ccnl, _RULES, _req(employment=Apprentice(months_elapsed=0)))
        r = compute(
            ccnl,
            _RULES,
            _req(employment=Apprentice(months_elapsed=0, track="gruppo_2")),
        )
        assert r.apprenticeship_pct == _D("0.70")

    def test_named_track_not_covering_level_raises(self) -> None:
        """A named track must cover the requested destination level."""
        with pytest.raises(ValueError, match="does not cover destination level '3'"):
            compute(
                _DEFAULT_CCNL,
                _RULES,
                _req(
                    level_code="3",
                    employment=Apprentice(months_elapsed=0, track="standard"),
                ),
            )

    def test_unknown_track_name_raises(self) -> None:
        """An unknown track name raises ValueError."""
        with pytest.raises(ValueError, match="no apprenticeship track named 'nope'"):
            compute(
                _DEFAULT_CCNL,
                _RULES,
                _req(employment=Apprentice(months_elapsed=0, track="nope")),
            )

    def test_pct_exempt_allowance_paid_at_full_value(self) -> None:
        """Allowances with apprenticeship_pct_relevant=False are not scaled by pct.

        Level 4 base=1000, one exempt allowance=200 (pct_relevant=False).
        Track: 80%. Allowance should remain 200, not 160.
        """
        data = make_ccnl_dict()
        data["levels"][2]["fixed_allowances"] = [
            _allowance("EDR", "200.00", apprenticeship_pct_relevant=False)
        ]
        ccnl = CCNL.model_validate(data)
        r = compute(ccnl, _RULES, _req(employment=Apprentice(months_elapsed=0)))
        # base: 1000 * 0.80 = 800; allowance: 200 (exempt, not scaled by 0.80)
        assert r.base_monthly == _D("800.00")
        assert r.allowances_monthly == _D("200.00")


# ---------------------------------------------------------------------------
# Apprentice — under-classification
# ---------------------------------------------------------------------------


class TestComputeApprenticeUnderClassification:
    """Under-classification track dispatch."""

    def test_basic(self) -> None:
        """Apprentice paid one level below (level '3': 800/month * 12 = 9600)."""
        r = compute(
            _DEFAULT_CCNL_UC, _RULES, _req(employment=Apprentice(months_elapsed=0))
        )

        assert r.apprenticeship_under_level_code == "3"
        assert r.apprenticeship_pct is None
        assert r.gross_annual == _D("9600.00")

    def test_levels_below_progression(self) -> None:
        """Each period resolves the pay level by order offset."""
        track = copy.deepcopy(_DEFAULT_CCNL_UC.apprenticeship[0].model_dump())
        track["periods"] = [
            {"months_from": 0, "months_until": 12, "levels_below": 2},
            {"months_from": 12, "months_until": 24, "levels_below": 1},
            {"months_from": 24, "months_until": None, "levels_below": 0},
        ]
        ccnl = _build_ccnl("under_classification", **{"apprenticeship.0": track})
        codes = [
            compute(
                ccnl, _RULES, _req(employment=Apprentice(months_elapsed=m))
            ).apprenticeship_under_level_code
            for m in (0, 12, 24)
        ]
        assert codes == ["2", "3", "4"]

    def test_midpoint_to_destination(self) -> None:
        """Midpoint period pays the mean of pay-level and destination base."""
        track = copy.deepcopy(_DEFAULT_CCNL_UC.apprenticeship[0].model_dump())
        track["periods"][0]["midpoint_to_destination"] = True
        ccnl = _build_ccnl("under_classification", **{"apprenticeship.0": track})
        r = compute(ccnl, _RULES, _req(employment=Apprentice(months_elapsed=0)))
        assert r.base_monthly == _D("900.00")
        assert r.apprenticeship_under_level_code == "3"

    def test_negotiated_ral(self) -> None:
        """RalOverride overrides the under-classification pay computation."""
        ral = _D("20000.00")
        r = compute(
            _DEFAULT_CCNL_UC,
            _RULES,
            _req(employment=Apprentice(months_elapsed=0), negotiated_ral=ral),
        )

        assert r.gross_annual == ral
        assert r.gross_monthly == _D("1666.67")
