"""Tests for engine.compute — compute() and private helper functions.

100% branch coverage:
* all validation error paths
* permanent / fixed-term / apprentice employment dispatches
* percentage and under-classification tracks, track selection by level
* seniority resolution from count or months, first cadence, per-level maximum
* role-scoped allowances, months_per_year, TFR/contribution relevance flags
* employer funds by category, ad personam element, hourly rate
* negotiated_ral override paths
* IRPEF net floored at zero
"""

from __future__ import annotations

import copy
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.engine.compute import _find_period_index, compute
from ccnl_engine.models.apprenticeship import ApprenticeshipPeriod
from ccnl_engine.models.ccnl import CCNL
from ccnl_engine.models.employment import Apprentice, FixedTerm, Permanent
from tests.conftest import make_ccnl_dict, make_year_rules

_DATE = date(2026, 6, 1)
_D = Decimal
_RULES = make_year_rules()
_PERMANENT = Permanent()
_FIXED_TERM = FixedTerm()


def _ccnl(app_type: str = "percentage", /, **mutations: object) -> CCNL:
    """Build a CCNL from the shared dict, applying dotted-path mutations.

    Returns:
        A validated CCNL instance with the requested mutations applied.
    """
    data = make_ccnl_dict(app_type=app_type)
    for path, value in mutations.items():
        node: Any = data
        keys = path.split(".")
        for key in keys[:-1]:
            node = node[int(key)] if key.isdigit() else node[key]
        last = keys[-1]
        if last.isdigit():
            node[int(last)] = value
        else:
            node[last] = value
    return CCNL.model_validate(data)


def _series(value: str) -> dict[str, Any]:
    return {
        "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": value}]
    }


def _allowance(code: str, monthly: str, **extra: object) -> dict[str, Any]:
    return {"code": code, "description": code, "monthly": _series(monthly), **extra}


_CCNL = _ccnl()
_CCNL_UC = _ccnl("under_classification")


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


class TestComputeValidation:
    """Guard-clause branches at the top of compute()."""

    @pytest.mark.parametrize("pct", ["0", "-0.1", "1.01"])
    def test_part_time_pct_out_of_range_raises(self, pct: str) -> None:
        """part_time_pct outside (0, 1] must raise ValueError."""
        with pytest.raises(ValueError, match="part_time_pct"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, part_time_pct=_D(pct))

    def test_ad_personam_negative_raises(self) -> None:
        """Negative ad_personam_monthly must raise ValueError."""
        with pytest.raises(ValueError, match="ad_personam_monthly"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, ad_personam_monthly=_D(-1))

    def test_unknown_level_code_raises(self) -> None:
        """Unknown level_code must raise KeyError."""
        with pytest.raises(KeyError, match="NOPE"):
            compute(_CCNL, "NOPE", _DATE, _RULES, _PERMANENT)

    def test_seniority_count_negative_raises(self) -> None:
        """Negative seniority_count must raise ValueError."""
        with pytest.raises(ValueError, match="seniority_count must be >= 0"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, seniority_count=-1)

    def test_seniority_months_negative_raises(self) -> None:
        """Negative seniority_months must raise ValueError."""
        with pytest.raises(ValueError, match="seniority_months must be >= 0"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, seniority_months=-1)

    def test_seniority_count_and_months_raises(self) -> None:
        """Passing both seniority inputs must raise ValueError."""
        with pytest.raises(ValueError, match="mutually exclusive"):
            compute(
                _CCNL,
                "4",
                _DATE,
                _RULES,
                _PERMANENT,
                seniority_count=1,
                seniority_months=40,
            )

    def test_seniority_count_above_maximum_raises(self) -> None:
        """seniority_count above the level maximum must raise ValueError."""
        with pytest.raises(ValueError, match="exceeds the maximum of 10"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, seniority_count=11)


# ---------------------------------------------------------------------------
# Permanent employment
# ---------------------------------------------------------------------------


class TestComputePermanent:
    """Permanent contract paths in compute()."""

    def test_full_time_no_seniority(self) -> None:
        """Permanent, full-time, no seniority: standard salary chain."""
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT)

        assert r.ccnl_id == "test"
        assert r.level_code == "4"
        assert r.employment_type == "permanent"
        assert r.part_time_pct == _D(1)
        assert r.as_of == _DATE
        assert r.year == 2026
        assert r.seniority_count == 0

        assert r.base_monthly == _D("1000.00")
        assert r.seniority_monthly == _D("0.00")
        assert r.allowances_monthly == _D("0.00")
        assert r.ad_personam_monthly == _D("0.00")
        assert r.gross_monthly == _D("1000.00")
        assert r.gross_annual == _D("12000.00")
        assert r.hourly_rate == _D("5.95")  # 1000 / 168
        assert r.employer_funds_annual == _D("0.00")

        assert r.apprenticeship_pct is None
        assert r.apprenticeship_under_level_code is None

        # Relational invariants
        assert r.taxable_income == r.gross_annual - r.inps_employee_annual
        assert r.irpef_net == max(_D(0), r.irpef_gross - r.work_income_deduction)
        assert r.net_annual == r.gross_annual - r.inps_employee_annual - r.irpef_net
        assert r.employer_cost_annual == (
            r.gross_annual + r.inps_employer_annual + r.tfr_annual
        )

    def test_with_seniority_count(self) -> None:
        """seniority_count=2 adds 2 * 20 = 40 to monthly gross."""
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, seniority_count=2)

        assert r.seniority_count == 2
        assert r.seniority_monthly == _D("40.00")
        assert r.gross_monthly == _D("1040.00")
        assert r.gross_annual == _D("12480.00")

    @pytest.mark.parametrize(
        ("months", "expected"),
        [(0, 0), (35, 0), (36, 1), (71, 1), (72, 2), (1000, 10)],
    )
    def test_seniority_months_derivation(self, months: int, expected: int) -> None:
        """Count = 1 + (months - cadence) // cadence, clamped to the maximum."""
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, seniority_months=months)
        assert r.seniority_count == expected

    @pytest.mark.parametrize(
        ("months", "expected"), [(47, 0), (48, 1), (83, 1), (84, 2), (120, 3)]
    )
    def test_seniority_first_cadence(self, months: int, expected: int) -> None:
        """First increment after first_cadence_months, then every cadence_months."""
        ccnl = _ccnl(**{"parameters.seniority_increments.first_cadence_months": 48})
        r = compute(ccnl, "4", _DATE, _RULES, _PERMANENT, seniority_months=months)
        assert r.seniority_count == expected

    def test_seniority_first_cadence_by_level(self) -> None:
        """Per-level first cadence (e.g. operai lump step at 48 months)."""
        ccnl = _ccnl(**{
            "parameters.seniority_increments.first_cadence_months_by_level": {"4": 48}
        })
        assert (
            compute(
                ccnl, "4", _DATE, _RULES, _PERMANENT, seniority_months=47
            ).seniority_count
            == 0
        )
        assert (
            compute(
                ccnl, "4", _DATE, _RULES, _PERMANENT, seniority_months=48
            ).seniority_count
            == 1
        )
        assert (
            compute(
                ccnl, "3", _DATE, _RULES, _PERMANENT, seniority_months=36
            ).seniority_count
            == 1
        )

    def test_seniority_per_level_maximum(self) -> None:
        """maximum_count_by_level overrides maximum_count for that level."""
        ccnl = _ccnl(**{
            "parameters.seniority_increments.maximum_count_by_level": {"4": 1}
        })
        r = compute(ccnl, "4", _DATE, _RULES, _PERMANENT, seniority_months=360)
        assert r.seniority_count == 1
        assert r.seniority_monthly == _D("20.00")
        with pytest.raises(ValueError, match="exceeds the maximum of 1"):
            compute(ccnl, "4", _DATE, _RULES, _PERMANENT, seniority_count=2)

    def test_excluded_category_zeroes_seniority(self) -> None:
        """Workers with category in excluded_categories accrue no scatti."""
        ccnl = _ccnl(**{
            "levels.2.category": "operaio",
            "parameters.seniority_increments.excluded_categories": ["operaio"],
        })
        r = compute(ccnl, "4", _DATE, _RULES, _PERMANENT, seniority_months=120)
        assert r.seniority_count == 0
        assert r.seniority_monthly == _D("0.00")

    def test_part_time_scales_all_components(self) -> None:
        """part_time_pct=0.5 halves every component; components sum to gross."""
        ccnl = _ccnl(**{"levels.2.fixed_allowances": [_allowance("edr", "10.33")]})
        r = compute(
            ccnl,
            "4",
            _DATE,
            _RULES,
            _PERMANENT,
            part_time_pct=_D("0.50"),
            seniority_count=1,
        )

        assert r.base_monthly == _D("500.00")
        assert r.seniority_monthly == _D("10.00")
        assert r.allowances_monthly == _D("5.17")
        assert r.gross_monthly == _D("515.17")
        assert r.gross_annual == _D("6182.04")

    def test_negotiated_ral(self) -> None:
        """negotiated_ral overrides gross_annual; gross_monthly stays consistent."""
        ral = _D("20000.00")
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, negotiated_ral=ral)

        assert r.gross_annual == ral
        assert r.gross_monthly == _D("1666.67")

    def test_level_without_seniority_entry(self) -> None:
        """Level '3' has no seniority in amount_by_level — seniority stays zero."""
        r = compute(_CCNL, "3", _DATE, _RULES, _PERMANENT, seniority_count=5)

        assert r.seniority_monthly == _D("0.00")
        assert r.base_monthly == _D("800.00")
        assert r.gross_annual == _D("9600.00")

    def test_ad_personam_added_unscaled(self) -> None:
        """ad_personam_monthly is added as given, even under part-time."""
        r = compute(
            _CCNL,
            "4",
            _DATE,
            _RULES,
            _PERMANENT,
            part_time_pct=_D("0.50"),
            ad_personam_monthly=_D("30.00"),
        )
        assert r.ad_personam_monthly == _D("30.00")
        assert r.gross_monthly == _D("530.00")
        assert r.gross_annual == _D("6360.00")


# ---------------------------------------------------------------------------
# Allowances
# ---------------------------------------------------------------------------


class TestComputeAllowances:
    """Role filter, months_per_year and relevance flags on fixed allowances."""

    def test_role_filter(self) -> None:
        """Role-scoped allowances apply only when the role is passed."""
        ccnl = _ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance("edr", "10.00"),
                _allowance("quadro", "100.00", role="quadro"),
            ]
        })
        plain = compute(ccnl, "4", _DATE, _RULES, _PERMANENT)
        quadro = compute(
            ccnl, "4", _DATE, _RULES, _PERMANENT, roles=frozenset({"quadro"})
        )
        assert plain.allowances_monthly == _D("10.00")
        assert quadro.allowances_monthly == _D("110.00")

    def test_months_per_year(self) -> None:
        """An allowance paid 12 times contributes 12 x monthly to gross_annual."""
        ccnl = _ccnl(**{
            "parameters.additional_months": _series("14"),
            "levels.2.fixed_allowances": [
                _allowance("ind", "50.00", months_per_year=12)
            ],
        })
        r = compute(ccnl, "4", _DATE, _RULES, _PERMANENT)
        assert r.gross_monthly == _D("1050.00")
        assert r.gross_annual == _D("14600.00")  # 1000*14 + 50*12

    def test_relevance_flags(self) -> None:
        """Non-relevant allowances are excluded from the INPS and TFR bases."""
        ccnl = _ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance(
                    "edr",
                    "100.00",
                    tfr_relevant=False,
                    contribution_relevant=False,
                )
            ]
        })
        r = compute(ccnl, "4", _DATE, _RULES, _PERMANENT)
        base = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT)
        assert r.gross_annual == _D("13200.00")
        assert r.inps_employee_annual == base.inps_employee_annual
        assert r.inps_employer_annual == base.inps_employer_annual
        assert r.tfr_annual == base.tfr_annual
        assert r.taxable_income == r.gross_annual - r.inps_employee_annual


# ---------------------------------------------------------------------------
# Employer funds and category rates
# ---------------------------------------------------------------------------


class TestComputeEmployerFunds:
    """Employer funds by category and category-specific employer rates."""

    _FUND = {
        "code": "cassa",
        "description": "Cassa",
        "rate": _series("0.10"),
        "applies_to_categories": ["operaio"],
    }

    def test_fund_applies_to_category(self) -> None:
        """A fund restricted to operai applies only to operaio levels."""
        ccnl = _ccnl(**{
            "parameters.employer_funds": [self._FUND],
            "levels.2.category": "operaio",
            "levels.1.category": "impiegato",
        })
        operaio = compute(ccnl, "4", _DATE, _RULES, _PERMANENT)
        impiegato = compute(ccnl, "3", _DATE, _RULES, _PERMANENT)
        uncategorised = compute(ccnl, "2", _DATE, _RULES, _PERMANENT)
        assert operaio.employer_funds_annual == _D("1200.00")
        assert operaio.employer_cost_annual == (
            operaio.gross_annual
            + operaio.inps_employer_annual
            + operaio.employer_funds_annual
            + operaio.tfr_annual
        )
        assert impiegato.employer_funds_annual == _D("0.00")
        assert uncategorised.employer_funds_annual == _D("0.00")

    def test_fund_without_category_restriction(self) -> None:
        """A fund with applies_to_categories=None applies to every level."""
        fund = {**self._FUND, "applies_to_categories": None}
        ccnl = _ccnl(**{"parameters.employer_funds": [fund]})
        r = compute(ccnl, "3", _DATE, _RULES, _PERMANENT)
        assert r.employer_funds_annual == _D("960.00")

    def test_employer_rate_by_category(self) -> None:
        """Employer rate override applies to matching categories only."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employer_rate": "0.30",
                "ceiling": None,
                "employer_rate_by_category": {"impiegato": "0.20"},
            }
        )
        ccnl = _ccnl(**{
            "levels.1.category": "impiegato",
            "levels.2.category": "operaio",
        })
        impiegato = compute(ccnl, "3", _DATE, rules, _PERMANENT)
        operaio = compute(ccnl, "4", _DATE, rules, _PERMANENT)
        assert impiegato.inps_employer_annual == _D("1920.00")  # 9600 * 0.20
        assert operaio.inps_employer_annual == _D("3600.00")  # 12000 * 0.30


# ---------------------------------------------------------------------------
# Fixed-term employment
# ---------------------------------------------------------------------------


class TestComputeFixedTerm:
    """Fixed-term contract adds NASpI addizionale to employer INPS."""

    def test_fixed_term_naspi_addizionale(self) -> None:
        """Employer INPS for fixed-term must exceed permanent by 1.4% of gross."""
        r_fixed = compute(_CCNL, "4", _DATE, _RULES, _FIXED_TERM)
        r_perm = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT)

        expected_diff = r_fixed.gross_annual * _D("0.014")
        actual_diff = r_fixed.inps_employer_annual - r_perm.inps_employer_annual
        assert abs(actual_diff - expected_diff) <= _D("0.01")
        assert r_fixed.employment_type == "fixed_term"


# ---------------------------------------------------------------------------
# IRPEF floor
# ---------------------------------------------------------------------------


class TestComputeIrpefFloor:
    """net = gross - inps when deduction exceeds gross IRPEF."""

    def test_irpef_net_floored_at_zero(self) -> None:
        """Low income: deduction > irpef_gross → irpef_net == 0."""
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, negotiated_ral=_D("5000.00"))

        assert r.irpef_net == _D("0.00")
        assert r.net_annual == r.gross_annual - r.inps_employee_annual


# ---------------------------------------------------------------------------
# Apprentice — percentage
# ---------------------------------------------------------------------------


class TestComputeApprenticePercentage:
    """Percentage track dispatch."""

    def test_basic(self) -> None:
        """Apprentice salary = destination-level salary * pct (0.80)."""
        r = compute(_CCNL, "4", _DATE, _RULES, Apprentice(months_elapsed=0))

        assert r.apprenticeship_pct == _D("0.80")
        assert r.apprenticeship_under_level_code is None
        assert r.base_monthly == _D("800.00")
        assert r.gross_annual == _D("9600.00")
        assert r.employment_type == "apprentice"

    def test_apprentice_contribution_rates(self) -> None:
        """Apprentices use the reduced statutory INPS rates."""
        r = compute(_CCNL, "4", _DATE, _RULES, Apprentice(months_elapsed=0))
        assert r.inps_employee_annual == _D("560.64")  # 9600 * 0.0584
        assert r.inps_employer_annual == _D("1114.56")  # 9600 * 0.1161

    def test_small_firm_rates_by_months(self) -> None:
        """Small-firm employer rate steps at 12 and 24 months."""
        rules = make_year_rules(
            apprentice={
                "employee_rate": "0.0584",
                "employer_rate_months_0_11": "0.0311",
                "employer_rate_months_12_23": "0.0461",
                "employer_rate_after": "0.1161",
            }
        )
        rates = [
            compute(
                _CCNL, "4", _DATE, rules, Apprentice(months_elapsed=m)
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
            _CCNL, "4", _DATE, _RULES, Apprentice(months_elapsed=0), seniority_count=2
        )
        assert r.seniority_monthly == _D("0.00")

    def test_apprentice_amount(self) -> None:
        """apprentice_amount replaces the level increment for apprentices."""
        ccnl = _ccnl(**{
            "parameters.seniority_increments.apprentice_amount": _series("6.00")
        })
        r = compute(
            ccnl, "4", _DATE, _RULES, Apprentice(months_elapsed=0), seniority_count=2
        )
        assert r.seniority_monthly == _D("9.60")  # 12 * 0.80

    def test_negotiated_ral(self) -> None:
        """negotiated_ral is applied as base before percentage multiplication."""
        ral = _D("20000.00")
        r = compute(
            _CCNL, "4", _DATE, _RULES, Apprentice(months_elapsed=0), negotiated_ral=ral
        )

        assert r.gross_annual == _D("16000.00")
        assert r.gross_monthly == _D("1333.33")

    def test_level_without_track_raises(self) -> None:
        """A destination level not covered by any track must raise ValueError."""
        with pytest.raises(ValueError, match=r"eligible destination levels: \['4'\]"):
            compute(_CCNL, "3", _DATE, _RULES, Apprentice(months_elapsed=0))

    def test_no_tracks_raises(self) -> None:
        """A CCNL without apprenticeship tracks reports its coverage status."""
        ccnl = _ccnl("none")
        with pytest.raises(ValueError, match=r"coverage\.layer_2 is partial"):
            compute(ccnl, "4", _DATE, _RULES, Apprentice(months_elapsed=0))

    def test_ambiguous_tracks_require_name(self) -> None:
        """Two tracks on one level: the caller must name the track."""
        second = copy.deepcopy(_CCNL.apprenticeship[0].model_dump())
        second["name"] = "gruppo_2"
        second["periods"][0]["percentage"] = "0.70"
        data = make_ccnl_dict()
        data["apprenticeship"].append(second)
        ccnl = CCNL.model_validate(data)
        with pytest.raises(ValueError, match=r"set Apprentice\.track"):
            compute(ccnl, "4", _DATE, _RULES, Apprentice(months_elapsed=0))
        r = compute(
            ccnl, "4", _DATE, _RULES, Apprentice(months_elapsed=0, track="gruppo_2")
        )
        assert r.apprenticeship_pct == _D("0.70")

    def test_named_track_not_covering_level_raises(self) -> None:
        """A named track must cover the requested destination level."""
        with pytest.raises(ValueError, match="does not cover destination level '3'"):
            compute(
                _CCNL,
                "3",
                _DATE,
                _RULES,
                Apprentice(months_elapsed=0, track="standard"),
            )

    def test_unknown_track_name_raises(self) -> None:
        """An unknown track name raises KeyError."""
        with pytest.raises(KeyError, match="no apprenticeship track named 'nope'"):
            compute(
                _CCNL, "4", _DATE, _RULES, Apprentice(months_elapsed=0, track="nope")
            )


# ---------------------------------------------------------------------------
# Apprentice — under-classification
# ---------------------------------------------------------------------------


class TestComputeApprenticeUnderClassification:
    """Under-classification track dispatch."""

    def test_basic(self) -> None:
        """Apprentice paid one level below (level '3': 800/month * 12 = 9600)."""
        r = compute(_CCNL_UC, "4", _DATE, _RULES, Apprentice(months_elapsed=0))

        assert r.apprenticeship_under_level_code == "3"
        assert r.apprenticeship_pct is None
        assert r.gross_annual == _D("9600.00")

    def test_levels_below_progression(self) -> None:
        """Each period resolves the pay level by order offset."""
        track = copy.deepcopy(_CCNL_UC.apprenticeship[0].model_dump())
        track["periods"] = [
            {"months_from": 0, "months_until": 12, "levels_below": 2},
            {"months_from": 12, "months_until": 24, "levels_below": 1},
            {"months_from": 24, "months_until": None, "levels_below": 0},
        ]
        ccnl = _ccnl("under_classification", **{"apprenticeship.0": track})
        codes = [
            compute(
                ccnl, "4", _DATE, _RULES, Apprentice(months_elapsed=m)
            ).apprenticeship_under_level_code
            for m in (0, 12, 24)
        ]
        assert codes == ["2", "3", "4"]

    def test_midpoint_to_destination(self) -> None:
        """Midpoint period pays the mean of pay-level and destination base."""
        track = copy.deepcopy(_CCNL_UC.apprenticeship[0].model_dump())
        track["periods"][0]["midpoint_to_destination"] = True
        ccnl = _ccnl("under_classification", **{"apprenticeship.0": track})
        r = compute(ccnl, "4", _DATE, _RULES, Apprentice(months_elapsed=0))
        assert r.base_monthly == _D("900.00")
        assert r.apprenticeship_under_level_code == "3"

    def test_negotiated_ral(self) -> None:
        """negotiated_ral overrides the under-classification pay computation."""
        ral = _D("20000.00")
        r = compute(
            _CCNL_UC,
            "4",
            _DATE,
            _RULES,
            Apprentice(months_elapsed=0),
            negotiated_ral=ral,
        )

        assert r.gross_annual == ral
        assert r.gross_monthly == _D("1666.67")


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
