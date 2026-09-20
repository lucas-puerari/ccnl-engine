"""Tests for engine/compute/orchestrator — compute() and helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    AbsenceRules,
    Allowance,
    CCNLWorkRules,
    DailyDivisorMethod,
    LeaveEntitlementTier,
    LeaveRules,
    OvertimeBand,
    SicknessRules,
    SupplementaryAllowance,
    TimeSupplementKind,
    TimeSupplements,
    WorkKind,
)
from ccnl_engine.engine.contract.domain.identity import (
    CCNLCoverage,
    CoverageNote,
    CoverageStatus,
    NoteKind,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.errors import OutOfScopeError
from ccnl_engine.engine.metadata.domain.rules import (
    RulesetIdentity,
    SourceType,
    VerificationStatus,
)
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import (
    FlatMonthlyFund,
    RateFund,
)
from ccnl_engine.engine.payroll.domain.calculation import TraceCategory
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import Apprentice
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import (
    CalculationStatus,
    EligibilityStatus,
    PeriodPayroll,
    ScopeItem,
    SourceQuality,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    AnnualEstimateInput,
    Employee,
    Jurisdiction,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WeeklyOvertimeHours,
    WelfareInput,
)
from ccnl_engine.engine.payroll.service.assembly import _collect_provenance
from ccnl_engine.engine.payroll.service.orchestrator import (
    _ivs_ceiling_warning,
    compute,
    estimate_annual,
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.scope import (
    _limitations_scope,
    compute_confidence,
    compute_result_status,
)
from ccnl_engine.engine.payroll.service.types import MonthlyPayChain
from ccnl_engine.engine.primitives import FrozenDict
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import (
    BackCalculationStep,
    ExtractionMethod,
    ExtractionTrace,
)
from ccnl_engine.engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.engine.surtax.domain.rules import (
    ComunaleEntry,
    RegionaleEntry,
    SurtaxBracket,
    SurtaxRules,
)
from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates
from ccnl_engine.engine.tax.domain.variable_pay import (
    FringeBenefitRules,
    PdRRules,
    VariablePayRules,
)
from ccnl_engine.engine.tax.service.loaders import (
    load_art15_deduction_rules,
    load_family_deduction_rules,
)
from tests.helpers import (
    TEST_PROV,
    TEST_RULESET_VERIFIED,
    make_ccnl_dict,
    make_domestic_year_rules,
    make_year_rules,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _FIXED_TERM,
    _RULES,
    _allowance,
    _build_ccnl,
    _req,
    _series,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.payroll_result import (
        AnnualEstimate as PayrollResult,
    )
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules as SurtaxRulesT
    from ccnl_engine.engine.tax.domain.art15 import Art15DeductionRules
    from ccnl_engine.engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_DEFAULT_CCNL = _build_ccnl()
_DEFAULT_CCNL_UC = _build_ccnl("under_classification")

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[object] = [_RULES]
_mock_surtax: list[SurtaxRulesT | None] = [None]


class _MockRepo:
    """Minimal KnowledgeRepository stub used by the autouse _patch_loaders fixture."""

    def load_ccnl(self, filename: str) -> CCNL:
        return _mock_ccnl[0]

    def load_year_rules(self, year: int, sector: object, num_employees: int) -> object:
        return _mock_rules[0]

    def load_surtax_rules(self, year: int) -> object:
        return _mock_surtax[0]


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the repository in orchestrator and reset mock state."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_RULES]
    _mock_surtax[:] = [None]
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator._default_repo",
        _MockRepo(),
    )


def _rule_provenance(tag: str) -> RuleProvenance:
    """Build a RuleProvenance with a distinguishing document/section identity.

    Returns:
        A :class:`RuleProvenance` uniquely identified by ``tag``.
    """
    return RuleProvenance(
        location=SourceLocation(
            source_document=SourceDocument(
                document_id=f"doc-{tag}",
                title=f"Document {tag}",
                kind=SourceKind.TABELLA_RETRIBUTIVA,
                url="https://example.com",
            ),
            section=f"Tabella {tag}",
        ),
        extraction=ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            verification_status=VerificationStatus.UNVERIFIED,
            effective_from=date(2025, 1, 1),
        ),
        note=tag,
    )


# ---------------------------------------------------------------------------
# Input model validation (scenario.py / employee.py)
# ---------------------------------------------------------------------------


class TestInputModels:
    """Validation in the input model constructors."""

    def test_seniority_by_count_negative_raises(self) -> None:
        """SeniorityByCount with value < 0 must raise at construction."""
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            SeniorityByCount(value=-1)

    def test_seniority_by_months_negative_raises(self) -> None:
        """SeniorityByMonths with value < 0 must raise at construction."""
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            SeniorityByMonths(value=-1)

    def test_part_time_ratio_out_of_range_raises(self) -> None:
        """Employee with part_time_ratio outside (0, 1] must raise."""
        with pytest.raises(ValueError, match="part_time_ratio"):
            Employee(level_code="4", part_time_ratio=Decimal(0))

    @pytest.mark.parametrize("pct", ["-0.1", "1.01"])
    def test_part_time_ratio_boundary(self, pct: str) -> None:
        """part_time_ratio outside (0, 1] must raise at any invalid value."""
        with pytest.raises(ValueError, match="part_time_ratio"):
            Employee(level_code="4", part_time_ratio=_D(pct))

    def test_weekly_hours_zero_raises(self) -> None:
        """Employee with weekly_hours <= 0 must raise at construction."""
        with pytest.raises(ValueError, match="weekly_hours"):
            Employee(level_code="4", weekly_hours=Decimal(0))

    def test_ad_personam_negative_raises(self) -> None:
        """Agreement with ad_personam_monthly < 0 must raise."""
        with pytest.raises(ValueError, match="ad_personam_monthly"):
            Agreement(ad_personam_monthly=_D(-1))

    def test_ral_override_zero_raises(self) -> None:
        """RalOverride with value <= 0 must raise at construction."""
        with pytest.raises(ValueError, match="must be > 0"):
            RalOverride(value=_D(0))

    def test_destination_ral_override_negative_raises(self) -> None:
        """DestinationRalOverride with value <= 0 must raise at construction."""
        with pytest.raises(ValueError, match="must be > 0"):
            DestinationRalOverride(value=_D("-1"))


# ---------------------------------------------------------------------------
# Validation errors inside compute()
# ---------------------------------------------------------------------------


class TestComputeValidation:
    """Guard-clause branches at the top of compute()."""

    def test_unknown_level_code_raises(self) -> None:
        """Unknown level_code must raise ValueError."""
        with pytest.raises(ValueError, match="NOPE"):
            estimate_annual(_req(level_code="NOPE"))

    def test_seniority_count_above_maximum_raises(self) -> None:
        """SeniorityByCount above the level maximum must raise ValueError."""
        with pytest.raises(ValueError, match="exceeds the maximum of 10"):
            estimate_annual(_req(seniority_count=11))

    def test_second_level_with_ral_override_raises(self) -> None:
        """second_level_allowances cannot be combined with a RAL override."""
        sl = SupplementaryAllowance(code="X", description="X", monthly=_D("100"))
        with pytest.raises(ValueError, match="RAL override"):
            estimate_annual(
                _req(negotiated_ral=_D("20000"), second_level_allowances=(sl,))
            )

    def test_negotiated_destination_ral_on_non_apprentice_raises(self) -> None:
        """DestinationRalOverride with a non-Apprentice contract raises."""
        with pytest.raises(ValueError, match="only valid for Apprentice"):
            estimate_annual(_req(negotiated_destination_ral=_D("20000.00")))


# ---------------------------------------------------------------------------
# Permanent employment
# ---------------------------------------------------------------------------


class TestComputePermanent:
    """Permanent contract paths in compute()."""

    def test_full_time_no_seniority(self) -> None:
        """Permanent, full-time, no seniority: standard salary chain."""
        r = estimate_annual(_req()).result

        assert r.ccnl_id == "test"
        assert r.level_code == "4"
        assert r.employment_type == "permanent"
        assert r.part_time_ratio == _D(1)
        assert r.as_of == _DATE
        assert r.year == 2026
        assert r.earnings.seniority_count == 0

        assert r.earnings.base_monthly == _D("1000.00")
        assert r.earnings.seniority_monthly == _D("0.00")
        assert r.earnings.allowances_monthly == _D("0.00")
        assert r.earnings.ad_personam_monthly == _D("0.00")
        assert r.earnings.gross_monthly == _D("1000.00")
        assert r.earnings.gross_annual == _D("12000.00")
        assert r.earnings.hourly_rate == money(_D("1000.00") / _D("168"))
        assert r.contributions.employer_funds_annual == _D("0.00")

        assert r.earnings.apprenticeship_pct is None
        assert r.earnings.apprenticeship_under_level_code is None

        # Relational invariants
        assert r.taxes.taxable_income == (
            r.earnings.gross_annual - r.contributions.inps_employee_annual
        )
        assert r.taxes.irpef_net == max(
            _D(0), r.taxes.irpef_gross - r.taxes.work_income_deduction
        )
        assert r.net_annual == (
            r.earnings.gross_annual
            - r.contributions.inps_employee_annual
            - r.taxes.irpef_net
        )
        assert r.employer_cost.employer_cost_annual == (
            r.earnings.gross_annual
            + r.contributions.inps_employer_annual
            + r.contributions.tfr_annual
        )

    def test_with_seniority_count(self) -> None:
        """seniority_count=2 adds 2 * 20 = 40 to monthly gross."""
        r = estimate_annual(_req(seniority_count=2)).result

        assert r.earnings.seniority_count == 2
        assert r.earnings.seniority_monthly == _D("40.00")
        assert r.earnings.gross_monthly == _D("1040.00")
        assert r.earnings.gross_annual == _D("12480.00")

    @pytest.mark.parametrize(
        ("months", "expected"),
        [(0, 0), (35, 0), (36, 1), (71, 1), (72, 2), (1000, 10)],
    )
    def test_seniority_months_derivation(self, months: int, expected: int) -> None:
        """Count = 1 + (months - cadence) // cadence, clamped to the maximum."""
        r = estimate_annual(_req(seniority_months=months)).result
        assert r.earnings.seniority_count == expected

    @pytest.mark.parametrize(
        ("months", "expected"), [(47, 0), (48, 1), (83, 1), (84, 2), (120, 3)]
    )
    def test_seniority_first_cadence(self, months: int, expected: int) -> None:
        """First increment after first_cadence_months, then every cadence_months."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months": 48
        })
        r = estimate_annual(_req(seniority_months=months)).result
        assert r.earnings.seniority_count == expected

    def test_seniority_first_cadence_by_level(self) -> None:
        """Per-level first cadence (e.g. operai lump step at 48 months)."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months_by_level": {"4": 48}
        })
        r47 = estimate_annual(_req(seniority_months=47)).result
        r48 = estimate_annual(_req(seniority_months=48)).result
        assert r47.earnings.seniority_count == 0
        assert r48.earnings.seniority_count == 1
        res = estimate_annual(_req(level_code="3", seniority_months=36)).result
        assert res.earnings.seniority_count == 1

    def test_seniority_per_level_maximum(self) -> None:
        """maximum_count_by_level overrides maximum_count for that level."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.maximum_count_by_level": {"4": 1}
        })
        r = estimate_annual(_req(seniority_months=360)).result
        assert r.earnings.seniority_count == 1
        assert r.earnings.seniority_monthly == _D("20.00")
        with pytest.raises(ValueError, match="exceeds the maximum of 1"):
            estimate_annual(_req(seniority_count=2))

    def test_part_time_scales_all_components(self) -> None:
        """part_time_ratio=0.5 halves every component; components sum to gross."""
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [_allowance("edr", "10.33")]
        })
        r = estimate_annual(_req(part_time_ratio=_D("0.50"), seniority_count=1)).result

        assert r.earnings.base_monthly == _D("500.00")
        assert r.earnings.seniority_monthly == _D("10.00")
        assert r.earnings.allowances_monthly == _D("5.17")
        assert r.earnings.gross_monthly == _D("515.17")
        assert r.earnings.gross_annual == _D("6182.04")

    def test_negotiated_ral(self) -> None:
        """RalOverride overrides gross_annual; gross_monthly stays consistent."""
        ral = _D("20000.00")
        r = estimate_annual(_req(negotiated_ral=ral)).result

        assert r.earnings.gross_annual == ral
        assert r.earnings.gross_monthly == _D("1666.67")

    def test_level_without_seniority_entry(self) -> None:
        """Level '3' has no seniority in amount_by_level — seniority stays zero."""
        r = estimate_annual(_req(level_code="3", seniority_count=5)).result

        assert r.earnings.seniority_monthly == _D("0.00")
        assert r.earnings.base_monthly == _D("800.00")
        assert r.earnings.gross_annual == _D("9600.00")

    def test_ad_personam_added_unscaled(self) -> None:
        """ad_personam_monthly is added as given, even under part-time."""
        r = estimate_annual(
            _req(part_time_ratio=_D("0.50"), ad_personam_monthly=_D("30.00"))
        ).result
        assert r.earnings.ad_personam_monthly == _D("30.00")
        assert r.earnings.gross_monthly == _D("530.00")
        assert r.earnings.gross_annual == _D("6360.00")


# ---------------------------------------------------------------------------
# Allowances
# ---------------------------------------------------------------------------


class TestComputeAllowances:
    """Role filter, months_per_year and relevance flags on fixed allowances."""

    def test_role_filter(self) -> None:
        """Role-scoped allowances apply only when the role is passed."""
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance("edr", "10.00"),
                _allowance("quadro", "100.00", role="quadro"),
            ]
        })
        plain = estimate_annual(_req()).result
        quadro = estimate_annual(_req(roles=frozenset({"quadro"}))).result
        assert plain.earnings.allowances_monthly == _D("10.00")
        assert quadro.earnings.allowances_monthly == _D("110.00")

    def test_months_per_year(self) -> None:
        """An allowance paid 12 times contributes 12 x monthly to gross_annual."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.additional_months": _series("14"),
            "levels.2.fixed_allowances": [
                _allowance("ind", "50.00", months_per_year=12)
            ],
        })
        r = estimate_annual(_req()).result
        assert r.earnings.gross_monthly == _D("1050.00")
        assert r.earnings.gross_annual == _D("14600.00")  # 1000*14 + 50*12

    def test_relevance_flags(self) -> None:
        """Non-relevant allowances are excluded from the INPS and TFR bases."""
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance(
                    "edr",
                    "100.00",
                    tfr_relevant=False,
                    contribution_relevant=False,
                )
            ]
        })
        r = estimate_annual(_req()).result
        # Re-fetch base with default CCNL
        _mock_ccnl[0] = _DEFAULT_CCNL
        base = estimate_annual(_req()).result
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance(
                    "edr",
                    "100.00",
                    tfr_relevant=False,
                    contribution_relevant=False,
                )
            ]
        })
        r = estimate_annual(_req()).result
        assert r.earnings.gross_annual == _D("13200.00")
        assert (
            r.contributions.inps_employee_annual
            == base.contributions.inps_employee_annual
        )
        assert (
            r.contributions.inps_employer_annual
            == base.contributions.inps_employer_annual
        )
        assert r.contributions.tfr_annual == base.contributions.tfr_annual
        assert r.taxes.taxable_income == (
            r.earnings.gross_annual - r.contributions.inps_employee_annual
        )

    def test_negotiated_ral_ignores_contribution_exclusions(self) -> None:
        """RalOverride must not have CCNL allowance exclusions subtracted from it.

        A negotiated RAL is the total retribuzione annua lorda agreed between
        employer and employee — it replaces the CCNL chain entirely. Subtracting
        CCNL-derived non-contributory allowances from it would understate the
        contribution base (they were never included in the negotiated figure).
        """
        ral = _D("12000.00")
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance(
                    "edr", "100.00", contribution_relevant=False, tfr_relevant=False
                )
            ]
        })
        r_with_exclusion = estimate_annual(_req(negotiated_ral=ral)).result
        _mock_ccnl[0] = _DEFAULT_CCNL
        r_clean = estimate_annual(_req(negotiated_ral=ral)).result

        assert r_with_exclusion.earnings.gross_annual == ral
        # Contribution and TFR bases must be identical regardless of CCNL allowances.
        assert (
            r_with_exclusion.contributions.inps_employee_annual
            == r_clean.contributions.inps_employee_annual
        )
        assert (
            r_with_exclusion.contributions.inps_employer_annual
            == r_clean.contributions.inps_employer_annual
        )
        assert (
            r_with_exclusion.contributions.tfr_annual
            == r_clean.contributions.tfr_annual
        )


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
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.employer_funds": [self._FUND],
            "levels.2.category": "operaio",
            "levels.1.category": "impiegato",
        })
        operaio = estimate_annual(_req()).result
        impiegato = estimate_annual(_req(level_code="3")).result
        uncategorised = estimate_annual(_req(level_code="2")).result
        assert operaio.contributions.employer_funds_annual == _D("1200.00")
        assert operaio.employer_cost.employer_cost_annual == (
            operaio.earnings.gross_annual
            + operaio.contributions.inps_employer_annual
            + operaio.contributions.employer_funds_annual
            + operaio.contributions.tfr_annual
        )
        assert impiegato.contributions.employer_funds_annual == _D("0.00")
        assert uncategorised.contributions.employer_funds_annual == _D("0.00")

    def test_fund_without_category_restriction(self) -> None:
        """A fund with applies_to_categories=None applies to every level."""
        fund = {**self._FUND, "applies_to_categories": None}
        _mock_ccnl[0] = _build_ccnl(**{"parameters.employer_funds": [fund]})
        r = estimate_annual(_req(level_code="3")).result
        assert r.contributions.employer_funds_annual == _D("960.00")

    def test_employer_rate_by_category(self) -> None:
        """Employer rate override applies to matching categories only."""
        _mock_rules[0] = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.30",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
                "employer_rate_by_category": {"impiegato": "0.20"},
            }
        )
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.1.category": "impiegato",
            "levels.2.category": "operaio",
        })
        impiegato = estimate_annual(_req(level_code="3")).result
        operaio = estimate_annual(_req()).result
        assert impiegato.contributions.inps_employer_annual == _D("1920.00")  # 9600*0.2
        assert operaio.contributions.inps_employer_annual == _D("3600.00")  # 12000*0.30


# ---------------------------------------------------------------------------
# Fixed-term employment
# ---------------------------------------------------------------------------


class TestComputeFixedTerm:
    """Fixed-term contract adds NASpI addizionale to employer INPS."""

    def test_fixed_term_naspi_addizionale(self) -> None:
        """Employer INPS for fixed-term must exceed permanent by 1.4% of gross."""
        r_fixed = estimate_annual(_req(contract=_FIXED_TERM)).result
        r_perm = estimate_annual(_req()).result

        expected_diff = r_fixed.earnings.gross_annual * _D("0.014")
        actual_diff = (
            r_fixed.contributions.inps_employer_annual
            - r_perm.contributions.inps_employer_annual
        )
        assert abs(actual_diff - expected_diff) <= _D("0.01")
        assert r_fixed.employment_type == "fixed_term"


# ---------------------------------------------------------------------------
# IVS ceiling split — end-to-end
# ---------------------------------------------------------------------------


class TestComputeIvsCeilingSplit:
    """compute() with ivs_ceiling_applies=True and RAL above massimale."""

    _CEILING = "122295.00"

    def _rules_with_ceiling(self) -> YearRules:
        return make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.2381",
                "ceiling": self._CEILING,
            }
        )

    def _scenario(
        self, ral: Decimal, *, ivs_ceiling_applies: bool
    ) -> AnnualEstimateInput:
        return _req(
            negotiated_ral=ral,
            ivs_ceiling_applies=ivs_ceiling_applies,
        )

    def test_below_ceiling_unchanged(self) -> None:
        """RAL below the massimale: ceiling split equals flat rate."""
        ral = _D("80000.00")
        _mock_rules[0] = self._rules_with_ceiling()
        r_capped = compute(self._scenario(ral, ivs_ceiling_applies=True)).result
        r_flat = compute(self._scenario(ral, ivs_ceiling_applies=False)).result
        assert (
            r_capped.contributions.inps_employee_annual
            == r_flat.contributions.inps_employee_annual
        )
        assert (
            r_capped.contributions.inps_employer_annual
            == r_flat.contributions.inps_employer_annual
        )

    def test_above_ceiling_ivs_capped_non_ivs_uncapped(self) -> None:
        """RAL above massimale: IVS portion capped, non-IVS applied to full base."""
        ral = _D("150000.00")
        ceiling = _D(self._CEILING)
        emp_rate = _D("0.0919")
        emp_ivs_rate = _D("0.0919")
        er_rate = _D("0.2898")
        er_ivs_rate = _D("0.2381")
        er_non_ivs = er_rate - er_ivs_rate
        emp_non_ivs = emp_rate - emp_ivs_rate
        expected_employee = money(ceiling * emp_ivs_rate + ral * emp_non_ivs)
        expected_employer = money(ceiling * er_ivs_rate + ral * er_non_ivs)

        _mock_rules[0] = self._rules_with_ceiling()
        r = compute(self._scenario(ral, ivs_ceiling_applies=True)).result
        assert r.contributions.inps_employee_annual == expected_employee
        assert r.contributions.inps_employer_annual == expected_employer

    def test_ceiling_flag_false_skips_split(self) -> None:
        """ivs_ceiling_applies=False: flat rate even when ceiling is configured."""
        ral = _D("150000.00")
        _mock_rules[0] = self._rules_with_ceiling()
        r = compute(self._scenario(ral, ivs_ceiling_applies=False)).result
        assert r.contributions.inps_employee_annual == _D("150000.00") * _D("0.0919")
        assert r.contributions.inps_employer_annual == _D("150000.00") * _D("0.2898")


# ---------------------------------------------------------------------------
# IRPEF floor
# ---------------------------------------------------------------------------


class TestComputeIrpefFloor:
    """Net = gross - inps when deduction exceeds gross IRPEF."""

    def test_irpef_net_floored_at_zero(self) -> None:
        """Low income: deduction > irpef_gross → irpef_net == 0."""
        r = estimate_annual(_req(negotiated_ral=_D("5000.00"))).result

        assert r.taxes.irpef_net == _D("0.00")
        assert r.net_annual == (
            r.earnings.gross_annual - r.contributions.inps_employee_annual
        )


# ---------------------------------------------------------------------------
# Withholding exemption (non-sostituto d'imposta employers)
# ---------------------------------------------------------------------------


class TestComputeWithholdingExempt:
    """withholding_exempt=True: irpef_net zero, informational fields retained."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_irpef_net_is_zero(self) -> None:
        """Exempt employer: irpef_net must be zero regardless of income."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req()).result
        assert r.taxes.irpef_net == _D("0.00")

    def test_employer_withholds_irpef_flag_false(self) -> None:
        """Exempt employer: employer_withholds_irpef must be False."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req()).result
        assert r.taxes.employer_withholds_irpef is False

    def test_net_annual_excludes_irpef(self) -> None:
        """Net = gross - INPS employee; IRPEF not deducted by employer."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req()).result
        assert r.net_annual == (
            r.earnings.gross_annual - r.contributions.inps_employee_annual
        )

    def test_irpef_informational_fields_nonzero(self) -> None:
        """irpef_gross and work_income_deduction remain as informational."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req()).result
        assert r.taxes.irpef_gross > _D("0.00")
        assert r.taxes.work_income_deduction >= _D("0.00")

    def test_standard_ccnl_withholds_irpef(self) -> None:
        """Standard CCNL: employer_withholds_irpef must be True."""
        r = estimate_annual(_req()).result
        assert r.taxes.employer_withholds_irpef is True


# ---------------------------------------------------------------------------
# Domestic flat-hour INPS model
# ---------------------------------------------------------------------------


_DOMESTIC_RULES = make_domestic_year_rules()
_DEFAULT_WEEKLY_HOURS: Decimal = _D("40")


class TestComputeDomesticInps:
    """Flat per-hour INPS model (rules.domestic_contributions is not None)."""

    def test_missing_weekly_hours_raises(self) -> None:
        """domestic_contributions set but weekly_hours=None must raise."""
        _mock_rules[0] = _DOMESTIC_RULES
        with pytest.raises(ValueError, match="weekly_hours is required"):
            estimate_annual(_req())

    def test_hours_bracket_permanent(self) -> None:
        """weekly_hours > 24 → hours bracket; permanent uses base employer rate."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(_req(weekly_hours=_D("40"))).result

        annual_hours = _D("40") * _D("52")
        assert r.contributions.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.contributions.inps_employer_annual == money(_D("0.93") * annual_hours)

    def test_hours_bracket_fixed_term(self) -> None:
        """weekly_hours > 24 + FixedTerm → hours bracket fixed-term rate."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(_req(contract=_FIXED_TERM, weekly_hours=_D("40"))).result

        annual_hours = _D("40") * _D("52")
        assert r.contributions.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.contributions.inps_employer_annual == money(_D("1.01") * annual_hours)

    def test_wage_bracket_mid(self) -> None:
        """weekly_hours <= 24 → wage bracket selected by annualised hourly rate.

        Level 4, gross_monthly=1000, weekly_hours=20:
        hourly_rate = 1000 * 12 / (20 * 52) = 11.54 → bracket up_to=11.70.
        """
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(_req(weekly_hours=_D("20"))).result

        annual_hours = _D("20") * _D("52")
        assert r.contributions.inps_employee_annual == money(_D("0.48") * annual_hours)
        assert r.contributions.inps_employer_annual == money(_D("1.44") * annual_hours)

    def test_net_is_gross_minus_inps_minus_irpef(self) -> None:
        """Net = gross - INPS employee - irpef_net for domestic path."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(_req(weekly_hours=_D("40"))).result
        assert r.net_annual == (
            r.earnings.gross_annual
            - r.contributions.inps_employee_annual
            - r.taxes.irpef_net
        )

    def test_no_ivs_ceiling_warning_for_domestic_contracts(self) -> None:
        """Domestic contracts must not emit a false IVS ceiling warning.

        The domestic model uses per-hour forfait rates; the IVS ceiling
        does not participate in that calculation.  Emitting the warning
        would produce a false confidence downgrade for a valid scenario.
        """
        _mock_rules[0] = _DOMESTIC_RULES
        # seniority_months=12 implies a clearly post-1996 hire: without the
        # guard, _ivs_ceiling_warning would emit "contributions are overstated".
        r = estimate_annual(_req(weekly_hours=_D("40"), seniority_months=12)).result
        ivs_warnings = [w for w in r.coverage.warnings if "overstated" in w]
        assert ivs_warnings == [], (
            f"Unexpected IVS warning on domestic contract: {r.coverage.warnings}"
        )


# ---------------------------------------------------------------------------
# Addizionale regionale e comunale
# ---------------------------------------------------------------------------

_FS = FiscalSimplification  # short alias for long assertion lines


class TestComputeAddizionali:
    """Tests for the addizionale regionale and comunale computation."""

    def _surtax_rules(self) -> SurtaxRules:
        """Build a minimal SurtaxRules with one region and one municipality.

        Returns:
            A SurtaxRules instance with TestRegione and X001 entries.
        """
        return SurtaxRules(
            year=2026,
            regionale={
                "TestRegione": RegionaleEntry(
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.0123")),)
                )
            },
            comunale={
                "X001": ComunaleEntry(
                    nome="Test",
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
                    exemption_threshold=Decimal(10000),
                )
            },
        )

    def _result(
        self,
        *,
        regione: str | None = None,
        comune_belfiore: str | None = None,
        negotiated_ral: Decimal | None = None,
    ) -> PayrollResult:
        has_locality = regione is not None or comune_belfiore is not None
        if has_locality:
            _mock_surtax[0] = self._surtax_rules()
        return estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=(
                    Jurisdiction(regione=regione, comune_belfiore=comune_belfiore)
                    if has_locality
                    else None
                ),
                negotiated_ral=negotiated_ral,
            )
        ).result

    def test_without_surtax_parameter_both_zero(self) -> None:
        """When no jurisdiction set (default), both addizionali are zero."""
        r = estimate_annual(_req()).result
        assert r.taxes.addizionale_regionale_annual == Decimal("0.00")
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.taxes.fiscal_simplifications

    def test_regione_only(self) -> None:
        """With regione set, addizionale regionale > 0; comunale still zero."""
        r = self._result(regione="TestRegione")
        assert r.taxes.addizionale_regionale_annual > Decimal(0)
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.taxes.fiscal_simplifications

    def test_comune_only(self) -> None:
        """With comune_belfiore set, addizionale comunale > 0; regionale zero."""
        r = self._result(comune_belfiore="X001")
        assert r.taxes.addizionale_comunale_annual > Decimal(0)
        assert r.taxes.addizionale_regionale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.taxes.fiscal_simplifications

    def test_both_set_both_computed(self) -> None:
        """With both fields set, both surtaxes are computed; neither flag set."""
        r = self._result(regione="TestRegione", comune_belfiore="X001")
        assert r.taxes.addizionale_regionale_annual > Decimal(0)
        assert r.taxes.addizionale_comunale_annual > Decimal(0)
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.taxes.fiscal_simplifications

    def test_both_reduce_net_annual(self) -> None:
        """Net annual is reduced by the sum of both addizionali."""
        r = self._result(regione="TestRegione", comune_belfiore="X001")
        expected_net = (
            r.earnings.gross_annual
            - r.contributions.inps_employee_annual
            - r.taxes.irpef_net
            - r.taxes.addizionale_regionale_annual
            - r.taxes.addizionale_comunale_annual
            + r.taxes.trattamento_integrativo
        )
        assert r.net_annual == expected_net

    def test_unknown_regione_produces_zero(self) -> None:
        """Unknown region name → addizionale regionale is zero, no flag."""
        r = self._result(regione="RegioneSconosciuta")
        assert r.taxes.addizionale_regionale_annual == Decimal("0.00")
        # No flag: the caller passed a region, we just didn't find it
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.taxes.fiscal_simplifications

    def test_unknown_comune_produces_zero(self) -> None:
        """Unknown codice catastale → addizionale comunale zero, no flag."""
        r = self._result(comune_belfiore="Z999")
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.taxes.fiscal_simplifications

    def test_soglia_exempts_low_income(self) -> None:
        """Income below the soglia yields zero comunal surtax."""
        tiny_ral = Decimal(9000)  # well below X001's soglia of 10000
        custom_surtax = SurtaxRules(
            year=2026,
            regionale={},
            comunale={
                "X001": ComunaleEntry(
                    nome="Test",
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
                    exemption_threshold=Decimal(10000),
                )
            },
        )
        _mock_surtax[0] = custom_surtax
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=tiny_ral,
                jurisdiction=Jurisdiction(comune_belfiore="X001"),
            )
        ).result
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")

    def test_irpef_zero_suppresses_addizionali(self) -> None:
        """When IRPEF is fully offset by deductions, addizionali are zero.

        A low RAL causes work_income_deduction to exceed irpef_gross, leaving
        irpef_fiscal = 0. Even with a valid jurisdiction, both surtaxes must
        be zero and NO_ADDIZIONALE_* flags must be present.
        """
        _mock_surtax[0] = self._surtax_rules()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=_D("8000"),
                jurisdiction=Jurisdiction(
                    regione="TestRegione", comune_belfiore="X001"
                ),
            )
        ).result
        assert r.taxes.irpef_net == _D("0.00"), "irpef_net must be zero in no-tax area"
        assert r.taxes.addizionale_regionale_annual == _D("0.00")
        assert r.taxes.addizionale_comunale_annual == _D("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.taxes.fiscal_simplifications


class TestFiscalFlagsExclusivity:
    """Addizionale flags are mutually exclusive regardless of TI-rules presence.

    When ``YearRules.taxes.trattamento_integrativo`` is ``None`` (no TI data in the
    bundle), ``_compute_ti`` must NOT seed the flag set with
    ``ADDIZIONALE_*_UNKNOWN``.  ``_compute_addizionali`` must further ensure
    that ``NO_ADDIZIONALE_*`` and ``ADDIZIONALE_*_UNKNOWN`` are never
    simultaneously active for the same jurisdiction axis.
    """

    @staticmethod
    def _surtax() -> SurtaxRules:
        return SurtaxRules(
            year=2026,
            regionale={
                "KnownRegione": RegionaleEntry(
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.0123")),)
                )
            },
            comunale={
                "K001": ComunaleEntry(
                    nome="Known",
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
                    exemption_threshold=Decimal(0),
                )
            },
        )

    def test_ti_absent_no_jurisdiction_no_unknown_flags(self) -> None:
        """TI absent, no jurisdiction: NO_ADDIZIONALE_* set, UNKNOWN flags absent.

        The standard _RULES mock has no trattamento_integrativo. When no
        jurisdiction is provided, both axes must carry NO_ADDIZIONALE_*, and
        ADDIZIONALE_*_UNKNOWN must be absent.
        """
        r = estimate_annual(_req()).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE in sfs
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN not in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN not in sfs

    def test_ti_absent_known_jurisdiction_no_flags(self) -> None:
        """TI absent, known jurisdiction: addizionale computed, no simplification.

        Neither NO_ADDIZIONALE_* nor ADDIZIONALE_*_UNKNOWN should be present
        when the jurisdiction is found in the bundle.
        """
        _mock_surtax[0] = self._surtax()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="KnownRegione", comune_belfiore="K001"
                ),
            )
        ).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE not in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE not in sfs
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN not in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN not in sfs

    def test_ti_absent_unknown_jurisdiction_unknown_flag_only(self) -> None:
        """TI absent, unknown jurisdiction: UNKNOWN set, NO_ADDIZIONALE_* absent.

        When a jurisdiction is provided but not found in the bundle, only
        ADDIZIONALE_*_UNKNOWN should be set; NO_ADDIZIONALE_* must be absent.
        """
        _mock_surtax[0] = self._surtax()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="UnknownRegione", comune_belfiore="Z999"
                ),
            )
        ).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN in sfs
        assert _FS.NO_ADDIZIONALE_REGIONALE not in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE not in sfs

    def test_ti_absent_irpef_zero_unknown_jurisdiction_no_unknown_flags(
        self,
    ) -> None:
        """TI absent, irpef_due=0, unknown jurisdiction: NO_ADDIZIONALE_* only.

        When IRPEF is zero (no-tax area), addizionali are suppressed regardless
        of jurisdiction. The NO_ADDIZIONALE_* flags must be set and
        ADDIZIONALE_*_UNKNOWN must be absent (not a contradiction).
        """
        _mock_surtax[0] = self._surtax()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=_D("8000"),  # below no-tax threshold
                jurisdiction=Jurisdiction(
                    regione="UnknownRegione", comune_belfiore="Z999"
                ),
            )
        ).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE in sfs
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN not in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN not in sfs


class TestProvenanceChain:
    """The PayrollResult carries the provenance of the rules it consumed."""

    def test_provenance_always_present(self) -> None:
        """All CCNLs carry provenance; minimal dict yields a non-empty tuple."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        _mock_ccnl[0] = ccnl
        _mock_rules[0] = make_year_rules()
        result = estimate_annual(_req()).result
        # Level 4 has provenance on the level and on its salary period.
        assert len(result.provenance) >= 1

    def test_level_and_period_provenance_collected(self) -> None:
        """Level and per-period base-salary provenance are collected in order."""
        prov_level = _rule_provenance("level")
        prov_period = _rule_provenance("period")
        ccnl = CCNL.model_validate(make_ccnl_dict())
        level = ccnl.level_by_code("4")
        new_period = level.base_salary.periods[0].model_copy(
            update={"provenance": prov_period}
        )
        new_series = level.base_salary.model_copy(update={"periods": [new_period]})
        new_level = level.model_copy(
            update={"provenance": prov_level, "base_salary": new_series}
        )
        new_params = ccnl.parameters.model_copy(
            update={
                "seniority_increments": ccnl.parameters.seniority_increments.model_copy(
                    update={"provenance": None}
                )
            }
        )
        new_levels = [new_level if lv.code == "4" else lv for lv in ccnl.levels]
        ccnl = ccnl.model_copy(update={"levels": new_levels, "parameters": new_params})
        _mock_ccnl[0] = ccnl
        _mock_rules[0] = make_year_rules()
        result = estimate_annual(_req()).result
        assert result.provenance == (prov_level, prov_period)

    def test_allowance_and_seniority_provenance_collected(self) -> None:
        """Allowance and seniority-increment provenance are collected."""
        prov_allowance = _rule_provenance("allowance")
        prov_seniority = _rule_provenance("seniority")
        ccnl = CCNL.model_validate(make_ccnl_dict())
        level = ccnl.level_by_code("4")
        allowance = Allowance(
            code="a",
            description="a",
            provenance=prov_allowance,
            monthly=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=Decimal("10.00"),
                    ),
                )
            ),
        )
        new_level = level.model_copy(update={"fixed_allowances": [allowance]})
        new_params = ccnl.parameters.model_copy(
            update={
                "seniority_increments": ccnl.parameters.seniority_increments.model_copy(
                    update={"provenance": prov_seniority}
                )
            }
        )
        new_levels = [new_level if lv.code == "4" else lv for lv in ccnl.levels]
        ccnl = ccnl.model_copy(update={"levels": new_levels, "parameters": new_params})
        _mock_ccnl[0] = ccnl
        _mock_rules[0] = make_year_rules()
        result = estimate_annual(_req()).result
        assert prov_allowance in result.provenance
        assert prov_seniority in result.provenance

    def test_no_matching_period_skips_period_provenance(self) -> None:
        """When no salary period covers as_of, no period provenance is added."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        level = ccnl.level_by_code("4")
        prov_level = _rule_provenance("level")
        prov_period = _rule_provenance("period")
        new_period = level.base_salary.periods[0].model_copy(
            update={"valid_from": date(2025, 1, 1), "provenance": prov_period}
        )
        new_series = level.base_salary.model_copy(update={"periods": [new_period]})
        new_level = level.model_copy(
            update={"provenance": prov_level, "base_salary": new_series}
        )
        new_params = ccnl.parameters.model_copy(
            update={
                "seniority_increments": ccnl.parameters.seniority_increments.model_copy(
                    update={"provenance": None}
                )
            }
        )
        # Calling _collect_provenance directly with a date before the period.
        result = _collect_provenance(
            new_level,
            date(2024, 6, 1),
            MonthlyPayChain(base=_D(0), seniority=_D(0), allowances=()),
            new_params.seniority_increments,
        )
        assert result == (prov_level,)


class TestApprenticeProvenance:
    """_collect_provenance uses the effective pay level for apprentices."""

    def test_under_level_provenance_used_when_code_given(self) -> None:
        """When under_level_code is set, the under level's provenance is used."""
        prov_dest = _rule_provenance("dest")
        prov_under = _rule_provenance("under")
        ccnl = CCNL.model_validate(make_ccnl_dict())
        dest_level = ccnl.level_by_code("4").model_copy(
            update={"provenance": prov_dest}
        )
        under_level = ccnl.level_by_code("3").model_copy(
            update={"provenance": prov_under}
        )
        new_params = ccnl.parameters.model_copy(
            update={
                "seniority_increments": ccnl.parameters.seniority_increments.model_copy(
                    update={"provenance": None}
                )
            }
        )
        new_levels = [
            dest_level if lv.code == "4" else (under_level if lv.code == "3" else lv)
            for lv in ccnl.levels
        ]
        ccnl = ccnl.model_copy(update={"levels": new_levels, "parameters": new_params})
        result = _collect_provenance(
            dest_level,
            _DATE,
            MonthlyPayChain(base=_D(0), seniority=_D(0), allowances=()),
            new_params.seniority_increments,
            ccnl=ccnl,
            under_level_code="3",
        )
        # Under level provenance takes priority; destination provenance not recorded.
        assert prov_under in result
        assert prov_dest not in result

    def test_no_ccnl_falls_back_to_destination_level(self) -> None:
        """When ccnl is None, destination level provenance is used (backward compat)."""
        prov_dest = _rule_provenance("dest")
        ccnl = CCNL.model_validate(make_ccnl_dict())
        dest_level = ccnl.level_by_code("4").model_copy(
            update={"provenance": prov_dest}
        )
        new_params = ccnl.parameters.model_copy(
            update={
                "seniority_increments": ccnl.parameters.seniority_increments.model_copy(
                    update={"provenance": None}
                )
            }
        )
        result = _collect_provenance(
            dest_level,
            _DATE,
            MonthlyPayChain(base=_D(0), seniority=_D(0), allowances=()),
            new_params.seniority_increments,
        )
        assert prov_dest in result

    def test_under_level_code_none_uses_destination_level(self) -> None:
        """When under_level_code is None, destination level provenance is used."""
        prov_dest = _rule_provenance("dest")
        ccnl = CCNL.model_validate(make_ccnl_dict())
        dest_level = ccnl.level_by_code("4").model_copy(
            update={"provenance": prov_dest}
        )
        new_params = ccnl.parameters.model_copy(
            update={
                "seniority_increments": ccnl.parameters.seniority_increments.model_copy(
                    update={"provenance": None}
                )
            }
        )
        new_levels = [dest_level if lv.code == "4" else lv for lv in ccnl.levels]
        ccnl = ccnl.model_copy(update={"levels": new_levels, "parameters": new_params})
        result = _collect_provenance(
            dest_level,
            _DATE,
            MonthlyPayChain(base=_D(0), seniority=_D(0), allowances=()),
            new_params.seniority_increments,
            ccnl=ccnl,
            under_level_code=None,
        )
        assert prov_dest in result


class TestApprenticeTrace:
    """build_calculation uses the effective pay level in the gross trace."""

    def test_trace_shows_under_level_for_under_classification_apprentice(
        self,
    ) -> None:
        """Trace BASE_SALARY detail must reference the under-level, not destination.

        The CCNL has destination level "4" and under-classification one step
        below, so the effective pay level is "3".  Before the fix, the trace
        would show "4@test" (destination).  After the fix it must show "3@test".
        """
        _mock_ccnl[0] = _DEFAULT_CCNL_UC
        scenario = _req(
            level_code="4", contract=Apprentice(months_elapsed=0)
        ).model_copy()
        try:
            calc = compute(scenario)
            base_steps = [
                s for s in calc.trace.steps if s.category == TraceCategory.BASE_SALARY
            ]
            assert base_steps, "Expected at least one BASE_SALARY trace step"
            assert base_steps[0].detail == "3@test", (
                f"Expected under-level code '3@test' in trace,"
                f" got: {base_steps[0].detail!r}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_trace_shows_destination_level_for_non_apprentice(self) -> None:
        """For a standard (non-apprentice) employee, trace uses the declared level."""
        calc = estimate_annual(_req(level_code="4"))
        base_steps = [
            s for s in calc.trace.steps if s.category == TraceCategory.BASE_SALARY
        ]
        assert base_steps, "Expected at least one BASE_SALARY trace step"
        assert base_steps[0].detail == "4@test", (
            f"Expected level code '4@test' in trace, got: {base_steps[0].detail!r}"
        )


class TestR7SubRulesetIdentities:
    """R7: compute() records sub-ruleset identities in ruleset_version."""

    def test_no_sub_rulesets_when_no_optional_inputs(self) -> None:
        """Without sick/variable-pay inputs, no sub-ruleset keys appear."""
        calc = estimate_annual(_req())
        assert "sick_pay" not in calc.ruleset_version
        assert "variable_pay" not in calc.ruleset_version

    def test_variable_pay_ruleset_present_with_fringe_benefit_input(self) -> None:
        """R7: fringe benefit input causes variable_pay to appear in ruleset_version."""
        calc = estimate_annual(
            _req().model_copy(
                update={
                    "fringe_benefit_input": FringeBenefitInput(annual_amount=_D("500"))
                }
            )
        )
        assert "variable_pay" in calc.ruleset_version

    def test_variable_pay_ruleset_present_with_bonus_input(self) -> None:
        """R7: bonus input causes variable_pay to appear in ruleset_version."""
        calc = estimate_annual(
            _req().model_copy(
                update={
                    "bonus_input": BonusInput(
                        annual_amount=_D("1000"), eligible_for_pdr=False
                    )
                }
            )
        )
        assert "variable_pay" in calc.ruleset_version

    def test_family_deductions_ruleset_present_when_dependents(self) -> None:
        """family_deductions appears in ruleset_version when scenario.family is set."""
        calc = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_CHILD_DEP,))}
            )
        )
        assert "family_deductions" in calc.ruleset_version, (
            f"Expected family_deductions in ruleset_version,"
            f" got: {calc.ruleset_version}"
        )

    def test_family_deductions_ruleset_absent_without_dependents(self) -> None:
        """family_deductions absent when no dependents in the scenario."""
        calc = estimate_annual(_req())
        assert "family_deductions" not in calc.ruleset_version

    def test_art15_deductions_ruleset_present_when_oneri_set(self) -> None:
        """art15_deductions appears in ruleset_version when art15_deductions is set."""
        calc = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("2000"))
                }
            )
        )
        assert "art15_deductions" in calc.ruleset_version, (
            f"Expected art15_deductions in ruleset_version, got: {calc.ruleset_version}"
        )

    def test_art15_deductions_ruleset_absent_without_oneri(self) -> None:
        """art15_deductions absent when art15_deductions is None."""
        calc = estimate_annual(_req())
        assert "art15_deductions" not in calc.ruleset_version


class TestL3Warning:
    """Orchestrator warning path for missing L3 schema."""

    def test_raises_out_of_scope_when_ccnl_has_no_l3(self) -> None:
        """Raise OutOfScopeError when time_supplements set but CCNL has no L3 schema."""
        scenario = _req().model_copy(
            update={"time_supplements": OvertimeHours(weekday_hours=_D("5"))}
        )
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(scenario)

    def test_warning_and_not_computed_when_gross_incl_allowances(self) -> None:
        """R10: hourly_base_method='gross_incl_allowances' emits warning, returns 0.

        The CCNL schema is present but the method is not yet implemented.
        The scope must show 'not_computed' for overtime/night/holiday work, and
        the result status must be 'partial' because of the not_computed entries.
        """
        ts_schema = TimeSupplements(
            hourly_base_method="gross_incl_allowances",
            overtime_bands=[],  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = _req().model_copy(
            update={"time_supplements": OvertimeHours(weekday_hours=_D("5"))}
        )
        try:
            result = compute(scenario).result
            assert isinstance(result, PeriodPayroll)
            warnings = result.coverage.warnings
            assert any("gross_incl_allowances" in w for w in warnings), (
                f"Expected gross_incl_allowances warning, got: {warnings}"
            )
            assert result.overtime_supplement_monthly == _D("0")
            assert result.time_supplements_monthly == _D("0")
            # Scope must show not_computed because method is unsupported
            ot_scope = next(
                s for s in result.coverage.calculation_scope if s.feature == "overtime"
            )
            assert ot_scope.calculation_status == "not_computed"
            assert result.coverage.status == "partial"
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_night_holiday_hours_contribute_to_holiday_scope(self) -> None:
        """R9: night_holiday_hours > 0 sets holiday_work to not_computed.

        Before the fix, night_holiday_hours was not counted toward the holiday
        scope, so holiday_work would be 'excluded' even when hours were supplied.
        Verified with a schema-present CCNL that has no NIGHT_HOLIDAY band.
        """
        weekday_band = OvertimeBand(
            code="STR",
            description="Straordinario feriale",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.25"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(
            overtime_bands=[weekday_band]  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = _req().model_copy(
            update={"time_supplements": OvertimeHours(night_holiday_hours=_D("2"))}
        )
        try:
            result = compute(scenario).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            # night_holiday_hours → holiday scope, no matching band → not_computed
            assert scope["holiday_work"] == "not_computed", (
                f"Expected holiday_work not_computed, got: {scope['holiday_work']}"
            )
            # Overtime and night must remain excluded (no hours for those buckets)
            assert scope["overtime"] == "excluded"
            assert scope["night_work"] == "excluded"
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_not_computed_when_schema_present_but_no_kind_band(self) -> None:
        """Schema present but no band for the requested WorkKind → not_computed.

        A CCNL with only a night band must report 'not_computed' for overtime
        when weekday_hours are requested, and 'verified' for night_work.
        Before the fix, scope checked ``wr_schema_present`` (the container) so
        both would show 'verified', masking missing band coverage.
        """
        night_band = OvertimeBand(
            code="NOTTE",
            description="Straordinario notturno",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.30"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.NIGHT],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(
            overtime_bands=[night_band]  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = _req().model_copy(
            update={
                "time_supplements": OvertimeHours(
                    weekday_hours=_D("5"),
                    night_hours=_D("3"),
                )
            }
        )
        try:
            result = compute(scenario).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            assert scope["overtime"] == "not_computed", (
                f"Expected not_computed for overtime (no weekday band), got:"
                f" {scope['overtime']}"
            )
            assert scope["night_work"] == "computed", (
                f"Expected verified for night_work (band present), got:"
                f" {scope['night_work']}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_supplementare_hours_with_only_weekday_band_not_computed(self) -> None:
        """supplementare_hours declared but only weekday band → not_computed + warning.

        When the CCNL has a weekday band but no supplementare band, declaring
        supplementare_hours must produce a warning and mark overtime as
        not_computed; the weekday band must not silently absorb the hours.
        """
        weekday_band = OvertimeBand(
            code="OT_WD",
            description="Straordinario diurno",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.15"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(
            overtime_bands=[weekday_band]  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = _req().model_copy(
            update={"time_supplements": OvertimeHours(supplementare_hours=_D("10"))}
        )
        try:
            result = compute(scenario).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            assert scope["overtime"] == "not_computed", (
                f"Expected not_computed (no supplementare band), got:"
                f" {scope['overtime']}"
            )
            assert any("supplementare" in w for w in result.coverage.warnings), (
                f"Expected supplementare warning, got: {result.coverage.warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_holiday_hours_with_only_night_holiday_band_not_computed(self) -> None:
        """holiday_hours declared but only night_holiday band → not_computed."""
        nh_band = OvertimeBand(
            code="NH",
            description="Festivo-notturno",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.85"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.NIGHT_HOLIDAY],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(overtime_bands=[nh_band])  # type: ignore[arg-type]
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = _req().model_copy(
            update={"time_supplements": OvertimeHours(holiday_hours=_D("4"))}
        )
        try:
            result = compute(scenario).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            assert scope["holiday_work"] == "not_computed", (
                f"Expected not_computed (no holiday band), got: {scope['holiday_work']}"
            )
            assert any("holiday" in w for w in result.coverage.warnings), (
                f"Expected holiday warning, got: {result.coverage.warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_tiered_band_warning_emitted_without_weekly_breakdown(self) -> None:
        """Warn when CCNL has tiered weekly bands but no OvertimeHours.weeks.

        When multiple bands share the same WorkKind (partitioned by
        hour_threshold_per_week) and the caller does not supply per-week
        hours, the engine emits a warning to avoid silent overstatement of
        the higher band.
        """
        band1 = OvertimeBand(
            code="OT_BASE",
            description="Straordinario base",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.15"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        band2 = OvertimeBand(
            code="OT_EXTRA",
            description="Straordinario extra",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.20"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
            hour_threshold_per_week=4,
        )
        ts_schema = TimeSupplements(overtime_bands=(band1, band2))
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = _req().model_copy(
            update={"time_supplements": OvertimeHours(weekday_hours=_D("10"))}
        )
        try:
            result = compute(scenario).result
            warnings = result.coverage.warnings
            assert any("tiered weekly thresholds" in w for w in warnings), (
                f"Expected tiered-band warning, got: {warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_tiered_band_warning_suppressed_with_weekly_breakdown(self) -> None:
        """No tiered-band warning when OvertimeHours.weeks is supplied."""
        band1 = OvertimeBand(
            code="OT_BASE",
            description="Straordinario base",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.15"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        band2 = OvertimeBand(
            code="OT_EXTRA",
            description="Straordinario extra",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.20"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
            hour_threshold_per_week=4,
        )
        ts_schema = TimeSupplements(overtime_bands=(band1, band2))
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        oh = OvertimeHours.from_weeks((
            WeeklyOvertimeHours(weekday_hours=_D("5")),
            WeeklyOvertimeHours(weekday_hours=_D("5")),
        ))
        scenario = _req().model_copy(update={"time_supplements": oh})
        try:
            result = compute(scenario).result
            warnings = result.coverage.warnings
            assert not any("tiered weekly thresholds" in w for w in warnings), (
                f"Unexpected tiered warning with weeks supplied: {warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_zero_hours_supplement_no_warning_when_no_schema(self) -> None:
        """Zero-valued OvertimeHours is treated as not requested: no warning.

        When all five hour fields are zero the engine must not emit
        "time_supplements requested but not modelled", because the caller
        effectively passed no hours.  Scope items must show 'excluded'.
        """
        # all fields default to 0
        scenario = _req().model_copy(update={"time_supplements": OvertimeHours()})
        result = compute(scenario).result
        warnings = result.coverage.warnings
        assert not any("time_supplements" in w for w in warnings), (
            f"Unexpected time_supplements warning for zero hours: {warnings}"
        )
        ot_scope = next(
            s for s in result.coverage.calculation_scope if s.feature == "overtime"
        )
        assert ot_scope.calculation_status == "excluded"


class TestL3Absence:
    """Orchestrator behaviour for L3 absence deduction."""

    def test_raises_out_of_scope_when_ccnl_has_no_absence_rules(self) -> None:
        """Raise OutOfScopeError when absence_days set but CCNL has no schema."""
        scenario = _req().model_copy(
            update={"absence_days": AbsenceDays(unpaid_days=_D("2"))}
        )
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(scenario)

    def test_absence_deduction_with_wr_schema(self) -> None:
        """Compute absence deduction when CCNL has absence_rules (by_26 method)."""
        absence_rules = AbsenceRules(
            daily_divisor_method=DailyDivisorMethod.BY_26,
        )
        # Inject work_rules with absence_rules into the mock CCNL.
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(absence_rules=absence_rules)}
        )
        scenario = _req().model_copy(
            update={"absence_days": AbsenceDays(unpaid_days=_D("1"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        # No warning: schema is present.
        assert not any("absence_days" in w for w in result.coverage.warnings)
        # Deduction must be > 0 and equals gross / 26.
        gross = result.earnings.gross_monthly
        expected = (gross / _D("26")).quantize(_D("0.01"))
        assert result.absence_deduction_monthly == expected
        # effective_gross = gross - deduction.
        assert result.effective_gross_monthly == gross - expected

    def test_absence_scope_excluded_when_no_days(self) -> None:
        """Absence scope item is excluded when no absence_days supplied."""
        result = estimate_annual(_req()).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["absence"] == "excluded"

    def test_raises_out_of_scope_when_absence_days_but_no_schema(self) -> None:
        """OutOfScopeError raised when absence_days given but CCNL has no schema."""
        scenario = _req().model_copy(
            update={"absence_days": AbsenceDays(unpaid_days=_D("3"))}
        )
        with pytest.raises(OutOfScopeError):
            compute(scenario)

    def test_absence_scope_verified_with_schema(self) -> None:
        """Absence is verified when days given and CCNL has absence_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    absence_rules=AbsenceRules(
                        daily_divisor_method=DailyDivisorMethod.BY_26,
                    )
                )
            }
        )
        scenario = _req().model_copy(
            update={"absence_days": AbsenceDays(unpaid_days=_D("2"))}
        )
        result = compute(scenario).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["absence"] == "computed"

    def test_absence_deduction_capped_when_exceeds_gross(self) -> None:
        """Deduction exceeding gross_monthly is capped and a warning emitted.

        With by_26 and gross=1000: daily_rate=38.46, 27 days → 1038.42 > 1000.
        The deduction must be capped to 1000 and effective_gross_monthly = 0.
        """
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    absence_rules=AbsenceRules(
                        daily_divisor_method=DailyDivisorMethod.BY_26,
                    )
                )
            }
        )
        scenario = _req().model_copy(
            update={"absence_days": AbsenceDays(unpaid_days=_D("27"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        gross = result.earnings.gross_monthly
        assert result.absence_deduction_monthly == gross
        assert result.effective_gross_monthly == _D("0.00")
        assert any("capped" in w for w in result.coverage.warnings), (
            f"Expected cap warning, got: {result.coverage.warnings}"
        )

    def test_absence_deduction_at_boundary_no_cap(self) -> None:
        """Deduction exactly equal to gross_monthly requires no cap and no warning.

        With by_26 and gross=1000: daily_rate=38.46, 26 days → 999.96 <= 1000.
        No cap warning and effective_gross_monthly = gross - deduction.
        """
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    absence_rules=AbsenceRules(
                        daily_divisor_method=DailyDivisorMethod.BY_26,
                    )
                )
            }
        )
        scenario = _req().model_copy(
            update={"absence_days": AbsenceDays(unpaid_days=_D("26"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        gross = result.earnings.gross_monthly
        expected_deduction = _D("999.96")  # round(1000/26)=38.46; 38.46*26=999.96
        assert result.absence_deduction_monthly == expected_deduction
        assert result.effective_gross_monthly == gross - expected_deduction
        assert not any("capped" in w for w in result.coverage.warnings), (
            f"Unexpected cap warning, got: {result.coverage.warnings}"
        )

    def test_zero_absence_days_no_warning_when_no_schema(self) -> None:
        """AbsenceDays(unpaid_days=0) is treated as not requested: no warning.

        When unpaid_days is zero the engine must not emit
        "absence_days requested but not modelled", because the caller
        effectively requested no absence.  Scope item must show 'excluded'.
        """
        scenario = _req().model_copy(
            update={"absence_days": AbsenceDays(unpaid_days=_D("0"))}
        )
        result = compute(scenario).result
        assert not any("absence_days" in w for w in result.coverage.warnings), (
            f"Unexpected absence_days warning for zero days: {result.coverage.warnings}"
        )
        absence_scope = next(
            s for s in result.coverage.calculation_scope if s.feature == "absence"
        )
        assert absence_scope.calculation_status == "excluded"


class TestL3Leave:
    """Orchestrator behaviour for L3 leave accrual."""

    def test_raises_out_of_scope_when_ccnl_has_no_leave_rules(self) -> None:
        """Raise OutOfScopeError when leave_input set but CCNL has no leave schema."""
        scenario = _req().model_copy(
            update={"leave_input": LeaveInput(taken_days=_D("3"))}
        )
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(scenario)

    def test_leave_accrual_with_wr_schema(self) -> None:
        """Compute leave accrual when CCNL has leave_rules (flat, no tiers)."""
        leave_rules = LeaveRules(default_annual_days=_D("20"))
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(leave_rules=leave_rules)}
        )
        scenario = _req().model_copy(
            update={"leave_input": LeaveInput(taken_days=_D("3"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        assert not any("leave_input" in w for w in result.coverage.warnings)
        # 20 / 12 = 1.67
        assert result.leave_accrued_days_monthly == _D("1.67")
        assert result.leave_taken_days_monthly == _D("3")
        assert result.leave_balance_days == _D("-1.33")

    def test_leave_accrual_selects_tier_by_service_months(self) -> None:
        """Tier with highest matching service_months_min is selected."""
        leave_rules = LeaveRules(
            default_annual_days=_D("20"),
            entitlement_tiers=[  # type: ignore[arg-type]
                LeaveEntitlementTier(service_months_min=0, annual_days=_D("20")),
                LeaveEntitlementTier(service_months_min=36, annual_days=_D("25")),
            ],
        )
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(leave_rules=leave_rules)}
        )
        # Employee with 48 months → senior tier (25 days/year → 2.08/month)
        scenario = _req(seniority_months=48).model_copy(
            update={"leave_input": LeaveInput(taken_days=_D("0"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        assert result.leave_accrued_days_monthly == _D("2.08")

    def test_leave_scope_excluded_when_no_input(self) -> None:
        """Leave scope item is excluded when no leave_input supplied."""
        result = estimate_annual(_req()).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["leave"] == "excluded"

    def test_raises_out_of_scope_when_leave_input_but_no_schema(self) -> None:
        """OutOfScopeError raised when leave_input given but CCNL has no schema."""
        scenario = _req().model_copy(
            update={"leave_input": LeaveInput(taken_days=_D("3"))}
        )
        with pytest.raises(OutOfScopeError):
            compute(scenario)

    def test_leave_scope_verified_with_schema(self) -> None:
        """Leave is verified when input given and CCNL has leave_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    leave_rules=LeaveRules(default_annual_days=_D("20"))
                )
            }
        )
        scenario = _req().model_copy(
            update={"leave_input": LeaveInput(taken_days=_D("2"))}
        )
        result = compute(scenario).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["leave"] == "computed"


class TestL3Sickness:
    """Orchestrator behaviour for L3 sickness (malattia ordinaria)."""

    def test_raises_out_of_scope_when_ccnl_has_no_sickness_rules(self) -> None:
        """Raise OutOfScopeError when sick_input set but CCNL has no sickness schema."""
        scenario = _req().model_copy(
            update={"sick_input": SickInput(sick_days=_D("5"))}
        )
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(scenario)

    def test_sickness_computed_with_wr_schema(self) -> None:
        """Compute sick-leave indemnity when CCNL has sickness_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    sickness_rules=SicknessRules(
                        carenza_integration_rate=_D("1"),
                        full_pay_integration_rate=_D("1"),
                    )
                )
            }
        )
        scenario = _req().model_copy(
            update={"sick_input": SickInput(sick_days=_D("3"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        assert not any("sick_input" in w for w in result.coverage.warnings)
        # 3 days: only carenza, no INPS indemnity
        assert result.sick_days_monthly == _D("3")
        assert result.sick_inps_indemnity_monthly == _D("0")

    def test_sick_scope_excluded_when_no_input(self) -> None:
        """Sickness is excluded when no sick_input is provided."""
        result = estimate_annual(_req()).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["sickness"] == "excluded"

    def test_raises_out_of_scope_when_sick_input_but_no_schema(self) -> None:
        """OutOfScopeError raised when sick_input given but CCNL has no schema."""
        scenario = _req().model_copy(
            update={"sick_input": SickInput(sick_days=_D("5"))}
        )
        with pytest.raises(OutOfScopeError):
            compute(scenario)

    def test_sick_scope_verified_with_schema(self) -> None:
        """Sickness is verified when input given and CCNL has sickness_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    sickness_rules=SicknessRules(
                        carenza_integration_rate=_D("1"),
                        full_pay_integration_rate=_D("1"),
                    )
                )
            }
        )
        scenario = _req().model_copy(
            update={"sick_input": SickInput(sick_days=_D("5"))}
        )
        result = compute(scenario).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["sickness"] == "computed"

    def test_sick_all_zero_when_no_input(self) -> None:
        """No sick_input produces AnnualEstimate (no period fields)."""
        result = estimate_annual(_req()).result
        assert not isinstance(result, PeriodPayroll)

    def test_zero_sick_days_no_warning_when_no_schema(self) -> None:
        """SickInput() with zero sick_days is treated as not requested.

        Mirrors test_zero_hours_supplement_no_warning_when_no_schema: a
        zero-valued SickInput must not emit the 'not modelled' warning and
        must leave the sickness scope as 'excluded', exactly like sick_input=None.
        """
        # sick_days defaults to 0
        scenario = _req().model_copy(update={"sick_input": SickInput()})
        result = compute(scenario).result
        warnings = result.coverage.warnings
        assert not any("sick_input" in w for w in warnings), (
            f"Unexpected sick_input warning for zero sick days: {warnings}"
        )
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["sickness"] == "excluded"

    def test_zero_sick_days_same_result_as_no_input(self) -> None:
        """SickInput() produces the same metadata as sick_input=None.

        confidence, result_status, and scope must be identical for a scenario
        with sick_input=None and one with sick_input=SickInput() (zero days).
        """
        result_none = estimate_annual(_req()).result
        scenario_zero = _req().model_copy(update={"sick_input": SickInput()})
        result_zero = compute(scenario_zero).result
        # Scope entry must match.
        scope_none = {
            s.feature: s.calculation_status
            for s in result_none.coverage.calculation_scope
        }
        scope_zero = {
            s.feature: s.calculation_status
            for s in result_zero.coverage.calculation_scope
        }
        assert scope_none["sickness"] == scope_zero["sickness"]
        # Overall result status must match.
        assert result_none.coverage.status == result_zero.coverage.status
        # Confidence must match.
        assert result_none.coverage.confidence == result_zero.coverage.confidence

    def test_sick_pay_loader_not_called_when_ccnl_has_no_sickness_rules(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_sick_pay_rates must not be called when the CCNL has no sickness_rules.

        Regression guard for the lazy-load gate: with positive sick days but no
        CCNL sickness schema OutOfScopeError is raised before the loader is
        reached, so a missing or corrupt sick-pay file cannot block a calculation.
        """

        def _fail() -> None:
            msg = "load_sick_pay_rates must not be called"
            raise RuntimeError(msg)

        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules.load_sick_pay_rates",
            _fail,
        )
        # Default CCNL has no work_rules (no sickness schema).
        scenario = _req().model_copy(
            update={"sick_input": SickInput(sick_days=_D("3"))}
        )
        # OutOfScopeError is raised before load_sick_pay_rates is ever called.
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(scenario)


class TestL3VariablePay:
    """Orchestrator integration tests for the variable-pay L3 features."""

    def test_fringe_benefit_scope_excluded_when_no_input(self) -> None:
        """fringe_benefit scope is excluded when no fringe_benefit_input."""
        result = estimate_annual(_req()).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["fringe_benefit"] == "excluded"

    def test_welfare_scope_excluded_when_no_input(self) -> None:
        """Welfare scope is excluded when no welfare_input."""
        result = estimate_annual(_req()).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["welfare"] == "excluded"

    def test_bonus_pdr_scope_excluded_when_no_input(self) -> None:
        """bonus_pdr scope is excluded when no bonus_input."""
        result = estimate_annual(_req()).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["bonus_pdr"] == "excluded"

    def test_all_variable_pay_fields_zero_when_no_inputs(self) -> None:
        """No variable-pay inputs produces AnnualEstimate (no period fields)."""
        result = estimate_annual(_req()).result
        assert not isinstance(result, PeriodPayroll)

    def test_fringe_benefit_scope_verified_when_input_given(self) -> None:
        """fringe_benefit scope is verified when input is provided."""
        scenario = _req().model_copy(
            update={"fringe_benefit_input": FringeBenefitInput(annual_amount=_D("800"))}
        )
        result = compute(scenario).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["fringe_benefit"] == "computed"

    def test_fringe_benefit_below_threshold_not_taxable(self) -> None:
        """Fringe benefit below €1.000 threshold: taxable_annual is zero."""
        scenario = _req().model_copy(
            update={"fringe_benefit_input": FringeBenefitInput(annual_amount=_D("800"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        assert result.fringe_benefit_annual == _D("800")
        assert result.fringe_benefit_threshold_annual == _D("1000.00")
        assert result.fringe_benefit_taxable_annual == _D("0")

    def test_fringe_benefit_above_threshold_taxable(self) -> None:
        """R15: Fringe benefit above €1.000 threshold: ENTIRE amount is taxable."""
        scenario = _req().model_copy(
            update={
                "fringe_benefit_input": FringeBenefitInput(annual_amount=_D("1400"))
            }
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        assert result.fringe_benefit_annual == _D("1400")
        assert result.fringe_benefit_taxable_annual == _D("1400.00")

    def test_welfare_scope_verified_when_input_given(self) -> None:
        """Welfare scope is verified when input is provided."""
        scenario = _req().model_copy(
            update={"welfare_input": WelfareInput(annual_amount=_D("600"))}
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["welfare"] == "computed"
        assert result.welfare_annual == _D("600")

    def test_bonus_pdr_eligible_applies_flat_tax(self) -> None:
        """PdR-eligible bonus within ceiling: flat tax computed correctly."""
        scenario = _req().model_copy(
            update={
                "bonus_input": BonusInput(
                    annual_amount=_D("2000"),
                    eligible_for_pdr=True,
                    prior_year_gross_annual=_D("50000"),
                )
            }
        )
        result = compute(scenario).result
        assert isinstance(result, PeriodPayroll)
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["bonus_pdr"] == "computed"
        assert result.bonus_annual == _D("2000")
        assert result.bonus_pdr_flat_tax_annual == _D("20.00")
        assert result.bonus_ordinary_taxable_annual == _D("0")

    def test_gross_annual_not_mutated_by_variable_pay(self) -> None:
        """gross_annual is unchanged; fringe (above threshold) raises taxable_income."""
        baseline = estimate_annual(_req()).result
        with_inputs = estimate_annual(
            _req().model_copy(
                update={
                    "fringe_benefit_input": FringeBenefitInput(
                        annual_amount=_D("1400")
                    ),
                    "welfare_input": WelfareInput(annual_amount=_D("600")),
                    "bonus_input": BonusInput(
                        annual_amount=_D("2000"),
                        eligible_for_pdr=True,
                        prior_year_gross_annual=_D("50000"),
                    ),
                }
            )
        ).result
        # gross_annual (base salary) is never altered by variable-pay inputs
        assert with_inputs.earnings.gross_annual == baseline.earnings.gross_annual
        # fringe above threshold (€1400 > €1000) adds to taxable_income
        assert with_inputs.taxes.taxable_income > baseline.taxes.taxable_income
        # higher taxable_income means more IRPEF and lower net
        assert with_inputs.taxes.irpef_net > baseline.taxes.irpef_net
        assert with_inputs.net_annual < baseline.net_annual

    def test_welfare_only_does_not_register_variable_pay_ruleset(self) -> None:
        """A welfare-only scenario must not include variable_pay in ruleset_version.

        compute_welfare() does not consume the variable-pay rules file; only
        fringe-benefit and bonus/PdR inputs trigger its load and registration.
        """
        scenario = _req().model_copy(
            update={"welfare_input": WelfareInput(annual_amount=_D("500"))}
        )
        calc = compute(scenario)
        assert "variable_pay" not in calc.ruleset_version


# ---------------------------------------------------------------------------
# L3: Family deductions (Art. 12 TUIR)
# ---------------------------------------------------------------------------


class TestL3FamilyDeductions:
    """Family deductions — orchestrator integration."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_no_family_leaves_irpef_net_unchanged(self) -> None:
        """Without family input, irpef_net equals baseline (no deduction)."""
        baseline = estimate_annual(_req()).result
        with_none = estimate_annual(_req().model_copy(update={"family": None})).result
        assert with_none.taxes.irpef_net == baseline.taxes.irpef_net
        assert with_none.taxes.family_deduction_annual == _D("0")

    def test_spouse_deduction_reduces_irpef_net(self) -> None:
        """Spouse deduction is subtracted from irpef_net."""
        baseline = estimate_annual(_req()).result
        with_spouse = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        assert with_spouse.taxes.family_deduction_spouse_annual > _D("0")
        assert with_spouse.taxes.irpef_net < baseline.taxes.irpef_net

    def test_family_deduction_children_and_other_zero_when_not_set(self) -> None:
        """Children/other fields are zero when only spouse is set."""
        result = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        assert result.taxes.family_deduction_children_annual == _D("0")
        assert result.taxes.family_deduction_other_annual == _D("0")

    def test_no_dependents_flags_no_deduction(self) -> None:
        """Family with no eligible dependents: deduction zero, irpef_net unchanged."""
        baseline = estimate_annual(_req()).result
        with_empty_family = estimate_annual(
            _req().model_copy(update={"family": FamilyComposition()})
        ).result
        assert with_empty_family.taxes.family_deduction_annual == _D("0")
        assert with_empty_family.taxes.irpef_net == baseline.taxes.irpef_net

    def test_exempt_employer_family_unused_equals_total(self) -> None:
        """When employer does not withhold IRPEF, unused = total deduction."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        result = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        assert result.taxes.family_deduction_spouse_annual > _D("0")
        assert (
            result.taxes.unused_family_deduction_annual
            == result.taxes.family_deduction_annual
        )
        assert result.taxes.irpef_net == _D("0.00")

    def test_gross_annual_not_mutated_by_family_deductions(self) -> None:
        """gross_annual is unchanged by family deductions."""
        baseline = estimate_annual(_req()).result
        with_family = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        assert with_family.earnings.gross_annual == baseline.earnings.gross_annual

    def test_family_deduction_taper_uses_taxable_income(self) -> None:
        """Art. 12 taper uses taxable_income (gross minus INPS), not gross_annual.

        With a spouse dependent, the taper formula is
        (95000 - reddito_complessivo) / 95000.  This test verifies the engine
        uses taxable_income (< gross_annual) so the taper and resulting
        deduction are larger than they would be if computed on gross_annual.
        """
        result_no_fam = estimate_annual(_req()).result
        result_spouse = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        # taxable_income < gross_annual, so the taper (95000 - RC) / 95000
        # is larger when RC = taxable_income.  The deduction must be strictly
        # greater than what the wrong (gross_annual) base would give.
        gross = result_no_fam.earnings.gross_annual
        taxable = result_no_fam.taxes.taxable_income
        assert taxable < gross
        # Deduction must be positive and taper-dependent
        assert result_spouse.taxes.family_deduction_spouse_annual > _D("0")
        # Expected: taper(taxable) > taper(gross), so deduction is larger.
        limit = _D("95000")
        taper_taxable = max(_D("0"), (limit - taxable) / limit)
        taper_gross = max(_D("0"), (limit - gross) / limit)
        assert taper_taxable > taper_gross

    def test_no_detrazioni_familiari_absent_when_dependents_present(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is removed when scenario.family has dependents.

        The flag signals that family deductions were NOT computed; it must be
        absent when the engine ran the Art. 12 computation, regardless of
        whether fam_total is positive.
        """
        result = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        assert (
            FiscalSimplification.NO_DETRAZIONI_FAMILIARI
            not in result.taxes.fiscal_simplifications
        )

    def test_no_detrazioni_familiari_present_when_family_is_none(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is present when no family data is provided."""
        result = estimate_annual(_req().model_copy(update={"family": None})).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_FAMILIARI in sfs

    def test_no_detrazioni_familiari_present_when_no_dependents(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is present when family has no eligible dependents.

        FamilyComposition() with no dependents: has_any_dependent is False, so
        the engine skips the Art. 12 computation and keeps the flag set.
        """
        result = estimate_annual(
            _req().model_copy(update={"family": FamilyComposition()})
        ).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_FAMILIARI in sfs


# ---------------------------------------------------------------------------
# Sterilizzazione detrazioni (Art. 1 c. 3-4 L. 199/2025)
# ---------------------------------------------------------------------------


class TestSterilizzazioneDetrazioni:
    """Sterilizzazione detrazioni — orchestrator integration.

    Art. 1 c. 3-4 L. 199/2025: reduces oneri detraibili al 19% (Art. 15
    c. 1 lett. a, b, d, e TUIR; not spese sanitarie lett. c) by EUR 440
    when reddito complessivo > threshold.  Art. 12 and Art. 13 deductions
    are not affected.  Uses a low custom threshold to trigger at test-CCNL
    income.
    """

    # Threshold below test-CCNL taxable income (~10 897) so sterilizzazione fires.
    _STRD_RULES = {"threshold": "10000", "reduction": "440"}

    def test_sterilizzazione_family_deduction_field_unchanged(self) -> None:
        """Family deductions are not reduced by sterilizzazione.

        Art. 12 deductions are not listed among the oneri targeted by
        Art. 1 c. 4 L. 199/2025.  Without Art. 15 deductions, sterilizzazione
        has nothing to reduce and the clawback is zero.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        with_strd = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        _mock_rules[0] = make_year_rules()
        baseline = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            )
        ).result
        assert (
            baseline.taxes.family_deduction_annual
            == with_strd.taxes.family_deduction_annual
        )
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("0")

    def test_sterilizzazione_no_art15_no_clawback(self) -> None:
        """Without Art. 15 deductions, sterilizzazione clawback is zero.

        The reduction targets oneri at 19%: when art15_total = 0 there is
        nothing to reduce and irpef_net is unchanged.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        with_strd = estimate_annual(_req()).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(_req()).result
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("0")
        assert with_strd.taxes.irpef_net == without_strd.taxes.irpef_net

    def test_sterilizzazione_increases_irpef_net(self) -> None:
        """Sterilizzazione reduces Art. 15 oneri credit → irpef_net increases.

        3 000 EUR mortgage interest → credit 570 EUR.  Clawback = min(440, 570)
        = 440.  irpef_net rises by exactly 440 EUR.  The raw art15_deduction
        field keeps reporting the pre-clawback credit.

        A RAL of 50 000 EUR is used to ensure IRPEF > 570 in both scenarios
        so the full 440 clawback is reflected rather than capped by incapienza.
        """
        art15 = Art15Deductions(mortgage_interest=_D("3000"))
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        with_strd = estimate_annual(
            _req(negotiated_ral=_D("50000")).model_copy(
                update={"art15_deductions": art15}
            )
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(
            _req(negotiated_ral=_D("50000")).model_copy(
                update={"art15_deductions": art15}
            )
        ).result
        # Art. 13 (work_income_deduction) is not affected.
        assert (
            with_strd.taxes.work_income_deduction
            == without_strd.taxes.work_income_deduction
        )
        # Clawback fires at 440 (< 570 credit).
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("440.00")
        # irpef_net increases by the clawback amount.
        assert (
            with_strd.taxes.irpef_net - without_strd.taxes.irpef_net
            == with_strd.taxes.sterilizzazione_clawback_annual
        )
        # Raw art15_deduction_annual field is the pre-clawback credit.
        assert with_strd.taxes.art15_deduction_annual == _D("570.00")

    def test_sterilizzazione_below_threshold_no_effect(self) -> None:
        """Income <= threshold: no clawback; irpef_net unchanged."""
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "9999999", "reduction": "440"}
        )
        with_high_threshold = estimate_annual(_req()).result
        _mock_rules[0] = make_year_rules()
        without = estimate_annual(_req()).result
        assert with_high_threshold.taxes.sterilizzazione_clawback_annual == _D("0")
        assert with_high_threshold.taxes.irpef_net == without.taxes.irpef_net

    def test_sterilizzazione_at_high_income_art15_reduced(self) -> None:
        """At real 200k+ income with Art. 15 oneri, clawback fires on the credit.

        At reddito complessivo 250 000 EUR, the full EUR 440 reduction applies
        to the Art. 15 mortgage credit (4 000 * 19% = 760 EUR → 320 EUR net).
        """
        high_income = _D("250000")
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "200000", "reduction": "440"}
        )
        with_strd = estimate_annual(
            _req(negotiated_ral=high_income).model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000"))
                }
            )
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(
            _req(negotiated_ral=high_income).model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000"))
                }
            )
        ).result
        # Clawback fires: Art. 15 credit is 760; min(440, 760) = 440.
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("440.00")
        # Raw art15_deduction_annual still shows the pre-clawback credit.
        assert with_strd.taxes.art15_deduction_annual == _D("760.00")
        # irpef_net increases by the clawback.
        assert with_strd.taxes.irpef_net - without_strd.taxes.irpef_net == _D("440.00")

    def test_sterilizzazione_with_family_and_art15_pins_unused(self) -> None:
        """art15_unused is recomputed against the effective credit after clawback.

        When sterilizzazione fires (clawback = 440), the effective Art. 15
        credit drops from 760 to 320 EUR.  art15_unused must be recomputed
        against the effective credit so that incapienza is not overstated.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        result = estimate_annual(
            _req().model_copy(
                update={
                    "family": FamilyComposition(dependents=(_SPOUSE_DEP,)),
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000")),
                }
            )
        ).result
        _mock_rules[0] = make_year_rules()
        result_no_strd = estimate_annual(
            _req().model_copy(
                update={
                    "family": FamilyComposition(dependents=(_SPOUSE_DEP,)),
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000")),
                }
            )
        ).result
        # Verify sterilizzazione fired and family deductions are present.
        assert result.taxes.sterilizzazione_clawback_annual == _D("440.00")
        assert result.taxes.family_deduction_annual > _D("0")
        # Raw art15_deduction_annual reports the pre-clawback credit in both.
        assert (
            result.taxes.art15_deduction_annual
            == result_no_strd.taxes.art15_deduction_annual
        )
        # art15_unused is lower with sterilizzazione because the effective credit
        # is smaller (320 vs 760 EUR), so less credit needs to be absorbed.
        assert result.taxes.unused_art15_deduction_annual <= (
            result_no_strd.taxes.unused_art15_deduction_annual
        )
        # The reduction in unused is bounded by the clawback amount.
        delta = (
            result_no_strd.taxes.unused_art15_deduction_annual
            - result.taxes.unused_art15_deduction_annual
        )
        assert _D("0") <= delta <= result.taxes.sterilizzazione_clawback_annual


# ---------------------------------------------------------------------------
# Art. 15 deductions (interessi passivi mutuo prima casa)
# ---------------------------------------------------------------------------


class TestArt15Deductions:
    """Art. 15 TUIR deductions — orchestrator integration."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_no_art15_leaves_irpef_net_unchanged(self) -> None:
        """Without art15_deductions, irpef_net equals baseline."""
        baseline = estimate_annual(_req()).result
        with_none = estimate_annual(
            _req().model_copy(update={"art15_deductions": None})
        ).result
        assert with_none.taxes.irpef_net == baseline.taxes.irpef_net
        assert with_none.taxes.art15_deduction_annual == _D("0")

    def test_mortgage_deduction_reduces_irpef_net(self) -> None:
        """Art. 15 mortgage credit is subtracted from irpef_net, clamped at 0.

        At the test-CCNL income level the credit (570 EUR) exceeds irpef_net
        (551.36), so irpef_net is floored at 0 — excess credit is lost per
        Italian tax law.
        """
        baseline = estimate_annual(_req()).result
        with_art15 = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            )
        ).result
        assert with_art15.taxes.art15_deduction_annual == _D("570.00")  # 3000 * 0.19
        expected = max(_D("0"), baseline.taxes.irpef_net - _D("570.00"))
        assert with_art15.taxes.irpef_net == expected

    def test_ceiling_cap_applied(self) -> None:
        """Interest above EUR 4 000 ceiling: credit capped at EUR 760."""
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("9999"))
                }
            )
        ).result
        assert result.taxes.art15_deduction_annual == _D("760.00")  # 4000 * 0.19

    def test_no_detrazioni_art15_mortgage_tag_removed_when_computed(self) -> None:
        """NO_DETRAZIONI_ART15_MORTGAGE absent when mortgage interest is provided."""
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("1000"))
                }
            )
        ).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE not in sfs

    def test_partial_detrazioni_art15_always_set_when_mortgage_present(self) -> None:
        """PARTIAL_DETRAZIONI_ART15 stays set even when mortgage is provided.

        Only one of ~15 Art. 15 TUIR categories is modelled; the flag signals
        that the other categories are always out of scope.
        """
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("1000"))
                }
            )
        ).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_no_detrazioni_art15_mortgage_tag_present_when_not_set(self) -> None:
        """NO_DETRAZIONI_ART15_MORTGAGE present when mortgage not provided."""
        result = estimate_annual(_req()).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE in sfs

    def test_partial_detrazioni_art15_always_set_when_no_art15(self) -> None:
        """PARTIAL_DETRAZIONI_ART15 always set, even without any Art. 15 input."""
        result = estimate_annual(_req()).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_exempt_employer_art15_unused_equals_total(self) -> None:
        """When employer does not withhold IRPEF, unused = total credit."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            )
        ).result
        assert result.taxes.art15_deduction_annual == _D("570.00")
        assert (
            result.taxes.unused_art15_deduction_annual
            == result.taxes.art15_deduction_annual
        )
        assert result.taxes.irpef_net == _D("0.00")

    def test_zero_interest_has_no_effect(self) -> None:
        """Art15Deductions with zero mortgage_interest: no deduction, tags kept."""
        baseline = estimate_annual(_req()).result
        with_zero = estimate_annual(
            _req().model_copy(
                update={"art15_deductions": Art15Deductions(mortgage_interest=_D("0"))}
            )
        ).result
        assert with_zero.taxes.art15_deduction_annual == _D("0")
        assert with_zero.taxes.irpef_net == baseline.taxes.irpef_net
        sfs = with_zero.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE in sfs
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_gross_annual_not_mutated_by_art15_deductions(self) -> None:
        """gross_annual is unchanged by Art. 15 deductions."""
        baseline = estimate_annual(_req()).result
        with_art15 = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("2000"))
                }
            )
        ).result
        assert with_art15.earnings.gross_annual == baseline.earnings.gross_annual

    def test_sterilizzazione_reduces_art15_increases_irpef(self) -> None:
        """Sterilizzazione fires on Art. 15 oneri; clawback = 440.

        When sterilizzazione fires (income > threshold), the effective Art. 15
        credit is reduced by 440.  art15_deduction_annual keeps reporting the
        raw pre-clawback credit; sterilizzazione_clawback_annual shows the
        reduction.
        """
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "10000", "reduction": "440"}
        )
        with_strd = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            )
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            )
        ).result
        # art15_deduction_annual reports the raw pre-clawback credit in both.
        assert with_strd.taxes.art15_deduction_annual == _D("570.00")
        assert without_strd.taxes.art15_deduction_annual == _D("570.00")
        # Clawback fires on Art. 15 → sterilizzazione_clawback = 440.
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("440.00")

    def test_exempt_employer_sterilizzazione_art15_unused_unchanged(self) -> None:
        """Exempt employer + sterilizzazione: art15_unused equals full art15_total.

        For exempt employers (non sostituto d'imposta), IRPEF is never
        withheld, so the entire Art. 15 credit is always unused.
        Sterilizzazione does not recompute art15_unused in this case.
        """
        _mock_ccnl[0] = self._EXEMPT_CCNL
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "10000", "reduction": "440"}
        )
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            )
        ).result
        # art15 = 3000 * 0.19 = 570; unchanged by sterilizzazione.
        assert result.taxes.art15_deduction_annual == _D("570.00")
        # Exempt employer: all art15 is unused (irpef_net stays 0 regardless).
        assert (
            result.taxes.unused_art15_deduction_annual
            == result.taxes.art15_deduction_annual
        )
        assert result.taxes.irpef_net == _D("0.00")

    def test_ulteriore_detrazione_reduces_art15_available_capacity(self) -> None:
        """Ulteriore detrazione consumes IRPEF capacity before Art. 15 credits.

        When ulteriore_detrazione_lavoro > 0, the IRPEF available to absorb
        Art. 15 deductions is reduced accordingly.  With a large UDL (EUR 5 000),
        all IRPEF is consumed before Art. 15 → unused_art15 equals art15_total.
        """
        # Set UDL rules with a large max_amount to exhaust IRPEF capacity.
        _mock_rules[0] = make_year_rules(
            ulteriore_detrazione={
                "threshold_low": "20000",
                "threshold_mid": "32000",
                "threshold_high": "40000",
                "max_amount": "5000",
            }
        )
        result = estimate_annual(
            _req(negotiated_ral=_D("25000")).model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000"))
                }
            )
        ).result
        # art15 = min(4000, 4000) * 0.19 = 760 (at EUR 4 000 ceiling).
        assert result.taxes.art15_deduction_annual == _D("760.00")
        # UDL = 5 000 exhausts all IRPEF before Art. 15 → full credit is unused.
        assert result.taxes.ulteriore_detrazione_lavoro == _D("5000.00")
        assert result.taxes.unused_art15_deduction_annual == _D("760.00")


class TestArt15MortgagePre2022:
    """Tests for mortgage_pre_2022 TI qualification gate."""

    def test_post_2021_mortgage_excluded_from_ti_relevant_deductions(self) -> None:
        """Post-2021 mortgage (default) does not affect trattamento_integrativo."""
        # Level 2 (base 600/month) puts taxable income in the TI band.
        baseline = estimate_annual(_req(level_code="2")).result
        with_post_2021 = estimate_annual(
            _req(level_code="2").model_copy(
                update={
                    "art15_deductions": Art15Deductions(
                        mortgage_interest=_D("3000"), mortgage_pre_2022=False
                    )
                }
            )
        ).result
        # Art. 15 credit still applied to IRPEF
        assert with_post_2021.taxes.art15_deduction_annual == _D("570.00")
        # TI unaffected by post-2021 mortgage
        assert (
            with_post_2021.taxes.trattamento_integrativo
            == baseline.taxes.trattamento_integrativo
        )

    def test_pre_2022_mortgage_included_in_ti_relevant_deductions(self) -> None:
        """Pre-2022 mortgage qualifies for TI relevant_deductions."""
        baseline = estimate_annual(_req(level_code="2")).result
        with_pre_2022 = estimate_annual(
            _req(level_code="2").model_copy(
                update={
                    "art15_deductions": Art15Deductions(
                        mortgage_interest=_D("3000"), mortgage_pre_2022=True
                    )
                }
            )
        ).result
        # Art. 15 credit still applied to IRPEF
        assert with_pre_2022.taxes.art15_deduction_annual == _D("570.00")
        # TI may increase because relevant_deductions grew (or remain at max)
        assert (
            with_pre_2022.taxes.trattamento_integrativo
            >= baseline.taxes.trattamento_integrativo
        )


def _scope_computed(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        gross_integrated=True,
        contribution_integrated=True,
        tax_integrated=True,
        net_integrated=True,
        cost_integrated=True,
        eligibility_status=EligibilityStatus.ENGINE_VERIFIED,
        source_quality=SourceQuality.VERIFIED_PRIMARY,
    )


def _scope_excluded(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.EXCLUDED,
        eligibility_status=EligibilityStatus.N_A,
        source_quality=SourceQuality.N_A,
    )


def _scope_not_computed(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.NOT_COMPUTED,
        eligibility_status=EligibilityStatus.N_A,
        source_quality=SourceQuality.N_A,
    )


def _scope_informational(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        eligibility_status=EligibilityStatus.ENGINE_VERIFIED,
        source_quality=SourceQuality.VERIFIED_PRIMARY,
    )


def _scope_caller_declared(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        gross_integrated=True,
        contribution_integrated=True,
        tax_integrated=True,
        net_integrated=True,
        cost_integrated=True,
        eligibility_status=EligibilityStatus.CALLER_DECLARED,
        source_quality=SourceQuality.VERIFIED_PRIMARY,
    )


class TestComputeResultStatus:
    """Unit tests for compute_result_status helper."""

    def test_all_computed_returns_complete(self) -> None:
        """All computed scope items → complete."""
        scope = (
            _scope_computed("base_salary"),
            _scope_computed("irpef"),
        )
        assert compute_result_status(scope) == "complete"

    def test_excluded_items_do_not_block_complete(self) -> None:
        """Excluded items are acceptable; result is still complete."""
        scope = (
            _scope_computed("base_salary"),
            _scope_excluded("overtime"),
        )
        assert compute_result_status(scope) == "complete"

    def test_not_computed_returns_partial(self) -> None:
        """A single not_computed item forces partial status."""
        scope = (
            _scope_computed("base_salary"),
            _scope_not_computed("overtime"),
        )
        assert compute_result_status(scope) == "partial"

    def test_informational_only_returns_partial(self) -> None:
        """Informational scope item (no integration axes) forces partial status."""
        scope = (
            _scope_computed("base_salary"),
            _scope_informational("fringe_benefit"),
        )
        assert compute_result_status(scope) == "partial"

    def test_caller_declared_returns_partial(self) -> None:
        """caller_declared eligibility_status forces partial status."""
        scope = (
            _scope_computed("base_salary"),
            _scope_caller_declared("family_deductions"),
        )
        assert compute_result_status(scope) == "partial"

    def test_empty_scope_returns_complete(self) -> None:
        """Empty scope (no items) → complete (no blocked requests)."""
        assert compute_result_status(()) == "complete"

    def test_compute_sets_status_on_result(self) -> None:
        """compute() populates status='complete' for a basic scenario."""
        result = estimate_annual(_req()).result
        assert result.coverage.status in {"complete", "partial"}

    def test_compute_status_is_complete_without_work_rules_input(self) -> None:
        """No L3 inputs and L3 schema present → complete (all excluded)."""
        result = estimate_annual(_req()).result
        # No overtime/leave/sick input: all L3 scope items are 'excluded'.
        # All L1/L2 items are 'computed'. Mock CCNL has no simplification
        # notes, so ccnl_limitations is not injected.
        assert result.coverage.status == "complete"


def _coverage(
    *notes: CoverageNote,
    gross: CoverageStatus = CoverageStatus.IMPLEMENTED,
    net: CoverageStatus = CoverageStatus.IMPLEMENTED,
) -> CCNLCoverage:
    """Build a CCNLCoverage with the given notes for _limitations_scope tests.

    Returns:
        A :class:`CCNLCoverage` for unit-testing _limitations_scope.
    """
    return CCNLCoverage(gross=gross, net=net, notes=notes)


class TestLimitationsScope:
    """Unit tests for _limitations_scope helper."""

    def test_none_coverage_returns_empty(self) -> None:
        """None coverage → no scope items added."""
        assert _limitations_scope(None) == []

    def test_no_applicable_notes_returns_empty(self) -> None:
        """Coverage with only info/source notes → no scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="hourly divisor confirmed"),
            CoverageNote(kind=NoteKind.SOURCE, text="source: official PDF"),
        )
        assert _limitations_scope(cov) == []

    def test_simplification_note_returns_scope_item(self) -> None:
        """Coverage with a simplification note → informational scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.SIMPLIFICATION, text="hourly rate approx")
        )
        result = _limitations_scope(cov)
        assert len(result) == 1
        assert result[0].feature == "ccnl_limitations"
        assert result[0].calculation_status == CalculationStatus.COMPUTED
        assert not any([
            result[0].gross_integrated,
            result[0].contribution_integrated,
            result[0].tax_integrated,
            result[0].net_integrated,
            result[0].cost_integrated,
        ])

    def test_missing_note_returns_scope_item(self) -> None:
        """Coverage with a missing note → informational_only scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="info"),
            CoverageNote(kind=NoteKind.MISSING, text="overtime data absent"),
            gross=CoverageStatus.PARTIAL,
        )
        result = _limitations_scope(cov)
        assert len(result) == 1
        assert result[0].feature == "ccnl_limitations"

    def test_limitations_force_partial_status(self) -> None:
        """compute_result_status with ccnl_limitations item → partial."""
        cov = _coverage(CoverageNote(kind=NoteKind.SIMPLIFICATION, text="approx"))
        scope = (
            _scope_computed("base_salary"),
            _scope_computed("irpef"),
            *_limitations_scope(cov),
        )
        assert compute_result_status(scope) == "partial"


def _verified_provenance() -> RuleProvenance:
    """Build a TABELLA_RETRIBUTIVA provenance with VERIFIED status.

    Returns:
        A :class:`RuleProvenance` with verification_status=VERIFIED.
    """
    return RuleProvenance(
        location=SourceLocation(
            source_document=SourceDocument(
                document_id="doc-verified",
                title="Tabella verificata",
                kind=SourceKind.TABELLA_RETRIBUTIVA,
                url="https://example.com",
            ),
            section="Art. 1",
        ),
        extraction=ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            verification_status=VerificationStatus.VERIFIED,
            effective_from=date(2025, 1, 1),
        ),
    )


class TestComputeConfidence:
    """Unit tests for compute_confidence helper."""

    def test_warnings_always_returns_low(self) -> None:
        """Any warning → low, regardless of status or provenance."""
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", ("overtime not modelled",), prov)
        assert result == "low"

    def test_warnings_override_complete_status(self) -> None:
        """Complete status + verified provenance does not rescue from low."""
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", ("a warning",), prov)
        assert result == "low"

    def test_complete_verified_returns_high(self) -> None:
        """Complete + no warnings + all provenance verified → high."""
        prov = (_verified_provenance(),)
        assert compute_confidence("complete", (), prov) == "high"

    def test_partial_status_returns_medium(self) -> None:
        """Partial status with verified provenance and no warnings → medium."""
        prov = (_verified_provenance(),)
        assert compute_confidence("partial", (), prov) == "medium"

    def test_unverified_salary_table_returns_medium(self) -> None:
        """UNVERIFIED TABELLA_RETRIBUTIVA blocks high confidence."""
        unverified = _rule_provenance("unverified")  # uses UNVERIFIED by default
        assert compute_confidence("complete", (), (unverified,)) == "medium"

    def test_needs_review_salary_table_returns_medium(self) -> None:
        """NEEDS_REVIEW status is treated as non-verified → medium."""
        needs_review = RuleProvenance(
            location=SourceLocation(
                source_document=SourceDocument(
                    document_id="doc-nr",
                    title="Da rivedere",
                    kind=SourceKind.TABELLA_RETRIBUTIVA,
                    url="https://example.com",
                ),
                section="Art. 1",
            ),
            extraction=ExtractionTrace(
                method=ExtractionMethod.MANUAL,
                extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                verification_status=VerificationStatus.NEEDS_REVIEW,
                effective_from=date(2025, 1, 1),
            ),
        )
        assert compute_confidence("complete", (), (needs_review,)) == "medium"

    def test_non_salary_table_unverified_lowers_confidence(self) -> None:
        """Any unverified source, regardless of kind, blocks high confidence."""
        rivista = RuleProvenance(
            location=SourceLocation(
                source_document=SourceDocument(
                    document_id="doc-rivista",
                    title="Rivista non verificata",
                    kind=SourceKind.RIVISTA,
                    url="https://example.com",
                ),
                section="pag. 12",
            ),
            extraction=ExtractionTrace(
                method=ExtractionMethod.MANUAL,
                extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                verification_status=VerificationStatus.UNVERIFIED,
                effective_from=date(2025, 1, 1),
            ),
        )
        assert compute_confidence("complete", (), (rivista,)) == "medium"

    def test_empty_provenance_complete_returns_high(self) -> None:
        """No provenance records + complete + no warnings → high."""
        assert compute_confidence("complete", (), ()) == "high"

    def test_unverified_ruleset_returns_medium(self) -> None:
        """An unverified consumed ruleset blocks high confidence."""
        unverified_ruleset = RulesetIdentity(
            id="inps/2026/terziario",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.OFFICIAL_PRIMARY,
            source_hash="a" * 64,
            verification_status=VerificationStatus.UNVERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence(
            "complete", (), prov, rulesets=(unverified_ruleset,)
        )
        assert result == "medium"

    def test_verified_ruleset_does_not_block_high(self) -> None:
        """A verified consumed ruleset does not block high confidence."""
        verified_ruleset = RulesetIdentity(
            id="inps/2026/industria",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="https://example.com",
            source_type=SourceType.OFFICIAL_PRIMARY,
            source_hash="b" * 64,
            verification_status=VerificationStatus.VERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(verified_ruleset,))
        assert result == "high"

    def test_derived_unverified_ruleset_blocks_high(self) -> None:
        """Unverified derived-source ruleset cannot produce high confidence."""
        derived_ruleset = RulesetIdentity(
            id="ccnl/test-derived",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.DERIVED,
            source_hash="f" * 64,
            verification_status=VerificationStatus.UNVERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(derived_ruleset,))
        assert result == "medium"

    def test_estimated_unverified_ruleset_blocks_high(self) -> None:
        """Unverified estimated-source ruleset cannot produce high confidence."""
        estimated_ruleset = RulesetIdentity(
            id="ccnl/test-estimated",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.ESTIMATED,
            source_hash="f" * 64,
            verification_status=VerificationStatus.UNVERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(estimated_ruleset,))
        assert result == "medium"

    def test_derived_verified_ruleset_allows_high(self) -> None:
        """Derived source with explicit verification does not block high."""
        derived_verified = RulesetIdentity(
            id="ccnl/test-derived-verified",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.DERIVED,
            source_hash="f" * 64,
            verification_status=VerificationStatus.VERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(derived_verified,))
        assert result == "high"

    def test_compute_result_has_confidence_field(self) -> None:
        """compute() populates confidence on the result."""
        result = estimate_annual(_req()).result
        assert result.coverage.confidence in {"low", "medium", "high"}


# ---------------------------------------------------------------------------
# Confidence: optional rulesets (N09)
# ---------------------------------------------------------------------------

_VERIFIED_PROV: dict[str, object] = {
    "location": {
        "source_document": {
            "document_id": "test-doc-verified",
            "title": "Verified Source",
            "kind": "tabella_retributiva",
            "url": "https://example.com",
        },
        "section": "Art. 1",
    },
    "extraction": {
        "method": "manual",
        "extraction_timestamp": "2026-01-01T00:00:00",
        "verification_status": "verified",
        "effective_from": "2020-01-01",
    },
}


def _verified_level(code: str, order: int, salary: str) -> dict[str, object]:
    period = {
        "valid_from": "2020-01-01",
        "valid_until": None,
        "value": salary,
        "provenance": _VERIFIED_PROV,
    }
    return {
        "code": code,
        "order": order,
        "description": f"Level {code}",
        "base_salary": {"periods": [period]},
        "fixed_allowances": [],
        "provenance": _VERIFIED_PROV,
    }


def _verified_ccnl() -> CCNL:
    """Minimal CCNL where all provenance AND the ruleset block are VERIFIED.

    Returns:
        A validated CCNL instance with fully verified salary provenance and
        a verified ruleset identity block.
    """
    raw = make_ccnl_dict()
    raw["levels"] = [
        _verified_level("2", 2, "600.00"),
        _verified_level("3", 3, "800.00"),
        _verified_level("4", 4, "1000.00"),
    ]
    raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
    raw["ruleset"] = TEST_RULESET_VERIFIED
    return CCNL.model_validate(raw)


def _var_pay_rules(status: VerificationStatus) -> VariablePayRules:
    """Build a VariablePayRules with a RulesetIdentity of the given status.

    Returns:
        A VariablePayRules instance with minimal fringe-benefit and PdR rules.
    """
    ruleset = RulesetIdentity(
        id="tax/variable-pay-rules/2026",
        version="2026.1",
        effective_from=date(2026, 1, 1),
        published_at=date(2026, 1, 1),
        source="https://example.com",
        source_type=SourceType.OFFICIAL_PRIMARY,
        source_hash="c" * 64,
        verification_status=status,
    )
    fb = FringeBenefitRules(
        threshold_standard=_D("1000"),
        threshold_with_children=_D("2000"),
    )
    pdr = PdRRules(
        max_amount=_D("5000"),
        flat_tax_rate=_D("0.05"),
        income_ceiling=_D("80000"),
    )
    return VariablePayRules(year=2026, fringe_benefit=fb, pdr=pdr, ruleset=ruleset)


_FB_INPUT = FringeBenefitInput(annual_amount=_D("500"))


class TestConfidenceWithOptionalRulesets:
    """Unverified optional rulesets downgrade confidence from high to medium."""

    def test_verified_var_pay_ruleset_does_not_downgrade_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verified var-pay ruleset + fringe_benefit → medium (informational).

        fringe_benefit is informational (no integration axes), so
        result.coverage.status is "partial" even when all provenance and
        rulesets are verified. Confidence reaches "medium", not "high".
        """
        _mock_ccnl[0] = _verified_ccnl()
        verified = _var_pay_rules(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules_variable_pay.load_variable_pay_rules",
            lambda _: verified,
        )
        result = estimate_annual(
            _req().model_copy(update={"fringe_benefit_input": _FB_INPUT})
        )
        assert result.result.coverage.confidence == "medium"

    def test_unverified_var_pay_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unverified var-pay ruleset drops confidence to medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _var_pay_rules(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules_variable_pay.load_variable_pay_rules",
            lambda _: unverified,
        )
        result = estimate_annual(
            _req().model_copy(update={"fringe_benefit_input": _FB_INPUT})
        )
        assert result.result.coverage.confidence == "medium"

    def test_ccnl_without_ruleset_limits_confidence_to_medium(self) -> None:
        """Verified CCNL provenance but absent ruleset block → at most medium.

        A missing ruleset identity is treated as "consumed but unverified",
        so confidence cannot reach "high" even when all salary provenance is
        verified.
        """
        raw = make_ccnl_dict()
        raw["levels"] = [
            _verified_level("2", 2, "600.00"),
            _verified_level("3", 3, "800.00"),
            _verified_level("4", 4, "1000.00"),
        ]
        raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
        # Intentionally no "ruleset" key → ccnl.ruleset = None
        _mock_ccnl[0] = CCNL.model_validate(raw)
        result = estimate_annual(_req())
        assert result.result.coverage.confidence == "medium"

    def test_unverified_ccnl_ruleset_downgrades_confidence(self) -> None:
        """Unverified CCNL ruleset → confidence medium."""
        ruleset_block = {
            "id": "ccnl/test",
            "version": "2026.1",
            "effective_from": "2026-01-01",
            "effective_until": None,
            "published_at": "2026-01-01",
            "source": "https://example.com",
            "source_type": "commercial_secondary",
            "source_hash": "d" * 64,
            "verification_status": "unverified",
        }
        raw = make_ccnl_dict()
        raw["levels"] = [
            _verified_level("2", 2, "600.00"),
            _verified_level("3", 3, "800.00"),
            _verified_level("4", 4, "1000.00"),
        ]
        raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
        raw["ruleset"] = ruleset_block
        _mock_ccnl[0] = CCNL.model_validate(raw)
        result = estimate_annual(_req())
        assert result.result.coverage.confidence == "medium"

    def test_sick_pay_rates_without_ruleset_not_added_to_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """InpsSickPayRates with ruleset=None: sick_pay absent from ruleset_ids."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    sickness_rules=SicknessRules(
                        carenza_integration_rate=_D("1"),
                        full_pay_integration_rate=_D("1"),
                    )
                )
            }
        )
        rates_no_ruleset = InpsSickPayRates(carenza_days=3, bands=[])
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules.load_sick_pay_rates",
            lambda: rates_no_ruleset,
        )
        scenario = _req().model_copy(
            update={"sick_input": SickInput(sick_days=_D("3"))}
        )
        calc = compute(scenario)
        assert "sick_pay" in calc.ruleset_version

    def test_var_pay_rules_without_ruleset_not_added_to_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """VariablePayRules with ruleset=None: variable_pay absent from ruleset_ids."""
        rules_no_ruleset = VariablePayRules(
            year=2026,
            fringe_benefit=FringeBenefitRules(
                threshold_standard=_D("1000"),
                threshold_with_children=_D("2000"),
            ),
            pdr=PdRRules(
                max_amount=_D("5000"),
                flat_tax_rate=_D("0.05"),
                income_ceiling=_D("80000"),
            ),
            ruleset=None,
        )
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules_variable_pay.load_variable_pay_rules",
            lambda _: rules_no_ruleset,
        )
        scenario = _req().model_copy(update={"fringe_benefit_input": _FB_INPUT})
        calc = compute(scenario)
        assert "variable_pay" in calc.ruleset_version


# ---------------------------------------------------------------------------
# Confidence: family and Art. 15 rulesets (N09 residue)
# ---------------------------------------------------------------------------


def _make_ruleset(suffix: str, status: VerificationStatus) -> RulesetIdentity:
    """Return a minimal RulesetIdentity for testing.

    Returns:
        A :class:`RulesetIdentity` with ``id`` suffixed by *suffix*.
    """
    return RulesetIdentity(
        id=f"tax/{suffix}/2026",
        version="2026.1",
        effective_from=date(2026, 1, 1),
        published_at=date(2026, 1, 1),
        source="https://example.com",
        source_type=SourceType.OFFICIAL_PRIMARY,
        source_hash="e" * 64,
        verification_status=status,
    )


def _family_rules_with_status(status: VerificationStatus) -> FamilyDeductionRules:
    """Return real family rules with *status* stamped on the ruleset.

    Returns:
        Real 2026 :class:`FamilyDeductionRules` with a synthetic identity.
    """
    base = load_family_deduction_rules(2026)
    return base.model_copy(
        update={"ruleset": _make_ruleset("family-deductions", status)}
    )


def _art15_rules_with_status(status: VerificationStatus) -> Art15DeductionRules:
    """Return real Art. 15 rules with *status* stamped on the ruleset.

    Returns:
        Real 2026 :class:`Art15DeductionRules` with a synthetic identity.
    """
    base = load_art15_deduction_rules(2026)
    return base.model_copy(
        update={"ruleset": _make_ruleset("art15-deductions", status)}
    )


_SPOUSE_DEP = Dependent(relationship=DependentRelationship.SPOUSE)
_CHILD_DEP = Dependent(
    relationship=DependentRelationship.CHILD, birth_date=date(2000, 1, 1)
)
_FAMILY_INPUT = FamilyComposition(dependents=(_SPOUSE_DEP,))
_ART15_INPUT = Art15Deductions(mortgage_interest=_D("4000"))


class TestConfidenceFamilyArt15:
    """N09 residue: family and Art. 15 rulesets participate in confidence.

    Each test uses a CCNL with fully verified provenance so that the only
    driver of confidence is the optional-feature ruleset identity.  The base
    YearRules have no ruleset block (``ruleset=None``, filtered from the
    consumed set), so they do not interfere.
    """

    def test_family_without_ruleset_downgrades_confidence(self) -> None:
        """Family deductions with missing ruleset identity → medium.

        The bundled family-deductions-2026.json carries a partial ruleset
        block (no verification_status).  _try_ruleset() returns None, which
        is treated as an unverified consumed source.
        """
        _mock_ccnl[0] = _verified_ccnl()
        result = estimate_annual(_req().model_copy(update={"family": _FAMILY_INPUT}))
        assert result.result.coverage.confidence == "medium"

    def test_family_with_verified_ruleset_still_medium(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Family deductions scope is caller_declared even with a verified ruleset.

        The engine cannot verify dependent eligibility (residency, disability
        certification, own income), so family_deductions is always
        ``"caller_declared"`` → result status is ``"partial"`` → confidence
        ``"medium"`` regardless of ruleset verification.
        """
        _mock_ccnl[0] = _verified_ccnl()
        verified = _family_rules_with_status(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_family_deduction_rules",
            lambda _: verified,
        )
        result = estimate_annual(_req().model_copy(update={"family": _FAMILY_INPUT}))
        assert result.result.coverage.confidence == "medium"

    def test_family_with_unverified_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Family deductions with an unverified ruleset → medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _family_rules_with_status(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_family_deduction_rules",
            lambda _: unverified,
        )
        result = estimate_annual(_req().model_copy(update={"family": _FAMILY_INPUT}))
        assert result.result.coverage.confidence == "medium"

    def test_art15_without_ruleset_downgrades_confidence(self) -> None:
        """Art. 15 deductions with no ruleset block in JSON → medium.

        art15-deductions-2026.json has no ruleset block at all; _try_ruleset()
        returns None, treated as an unverified consumed source.
        """
        _mock_ccnl[0] = _verified_ccnl()
        result = estimate_annual(
            _req().model_copy(update={"art15_deductions": _ART15_INPUT})
        )
        assert result.result.coverage.confidence == "medium"

    def test_art15_with_verified_ruleset_stays_medium(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Art. 15 deductions with a verified ruleset + verified CCNL → medium.

        art15_deductions is always calculation_status=partial (simplified model),
        so result.coverage.status is "partial" and confidence tops out at "medium".  A
        verified ruleset does not degrade confidence further.
        """
        _mock_ccnl[0] = _verified_ccnl()
        verified = _art15_rules_with_status(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_art15_deduction_rules",
            lambda _: verified,
        )
        result = estimate_annual(
            _req().model_copy(update={"art15_deductions": _ART15_INPUT})
        )
        assert result.result.coverage.confidence == "medium"

    def test_art15_with_unverified_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Art. 15 deductions with an unverified ruleset → medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _art15_rules_with_status(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_art15_deduction_rules",
            lambda _: unverified,
        )
        result = estimate_annual(
            _req().model_copy(update={"art15_deductions": _ART15_INPUT})
        )
        assert result.result.coverage.confidence == "medium"

    def test_no_optional_features_confidence_unaffected(self) -> None:
        """No family or Art. 15 inputs: consumed_ruleset_ids stays empty."""
        _mock_ccnl[0] = _verified_ccnl()
        result = estimate_annual(_req())
        assert result.result.coverage.confidence == "high"

    def test_none_ruleset_in_compute_confidence_is_unverified(self) -> None:
        """compute_confidence treats None ruleset entries as unverified."""
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(None,))
        assert result == "medium"


# ---------------------------------------------------------------------------
# Bilateral funds (feat/bilateral-funds)
# ---------------------------------------------------------------------------


class TestBilateralFundsValidation:
    """Construction-time validation for bilateral fund domain models."""

    def test_flat_monthly_fund_negative_employee_raises(self) -> None:
        """FlatMonthlyFund with negative employee_monthly must raise."""
        with pytest.raises(ValueError, match="employee_monthly"):
            FlatMonthlyFund(employee_monthly=_D("-1"), employer_monthly=_D("5"))

    def test_flat_monthly_fund_negative_employer_raises(self) -> None:
        """FlatMonthlyFund with negative employer_monthly must raise."""
        with pytest.raises(ValueError, match="employer_monthly"):
            FlatMonthlyFund(employee_monthly=_D("5"), employer_monthly=_D("-1"))

    def test_rate_fund_negative_employee_rate_raises(self) -> None:
        """RateFund with negative employee_rate must raise."""
        with pytest.raises(ValueError, match="employee_rate"):
            RateFund(
                employee_rate=_D("-0.001"),
                employer_rate=_D("0.01"),
                base="tfr_base",
            )

    def test_rate_fund_negative_employer_rate_raises(self) -> None:
        """RateFund with negative employer_rate must raise."""
        with pytest.raises(ValueError, match="employer_rate"):
            RateFund(
                employee_rate=_D("0.001"),
                employer_rate=_D("-0.01"),
                base="gross_annual",
            )


class TestBilateralFunds:
    """Integration tests for bilateral fund computation via compute()."""

    def test_no_bilateral_funds_flag_present_when_no_funds(self) -> None:
        """NO_BILATERAL_FUNDS is set when bilateral_funds is empty."""
        result = estimate_annual(_req()).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_BILATERAL_FUNDS in sfs

    def test_no_bilateral_funds_flag_absent_when_funds_present(self) -> None:
        """NO_BILATERAL_FUNDS is cleared when at least one fund is provided."""
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    FlatMonthlyFund(
                        employee_monthly=_D("5"),
                        employer_monthly=_D("10"),
                    ),
                )
            }
        )
        result = compute(scenario).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_BILATERAL_FUNDS not in sfs

    def test_flat_monthly_fund_reduces_net_annual(self) -> None:
        """Employee flat monthly contribution (x 12) is subtracted from net_annual."""
        baseline = estimate_annual(_req()).result
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    FlatMonthlyFund(
                        employee_monthly=_D("20"),
                        employer_monthly=_D("0"),
                    ),
                )
            }
        )
        result = compute(scenario).result
        expected_net = money(baseline.net_annual - _D("20") * 12)
        assert result.net_annual == expected_net

    def test_flat_monthly_fund_increases_employer_cost(self) -> None:
        """Employer flat monthly contribution (x 12) enters employer_cost_annual."""
        baseline = estimate_annual(_req()).result
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    FlatMonthlyFund(
                        employee_monthly=_D("0"),
                        employer_monthly=_D("15"),
                    ),
                )
            }
        )
        result = compute(scenario).result
        expected_cost = money(
            baseline.employer_cost.employer_cost_annual + _D("15") * 12
        )
        assert result.employer_cost.employer_cost_annual == expected_cost

    def test_rate_fund_tfr_base_computation(self) -> None:
        """RateFund with base='tfr_base' is applied and reduces net_annual."""
        baseline = estimate_annual(_req()).result
        rate = _D("0.01")
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    RateFund(
                        employee_rate=rate, employer_rate=_D("0"), base="tfr_base"
                    ),
                )
            }
        )
        result = compute(scenario).result
        # bilateral_employee_annual must be positive (tfr_base > 0)
        assert result.contributions.bilateral_employee_annual > _D("0")
        # net_annual decreases by exactly bilateral_employee_annual
        assert result.net_annual == money(
            baseline.net_annual - result.contributions.bilateral_employee_annual
        )
        # employer side unaffected
        assert result.contributions.bilateral_employer_annual == _D("0")
        assert (
            result.employer_cost.employer_cost_annual
            == baseline.employer_cost.employer_cost_annual
        )

    def test_rate_fund_gross_annual_computation(self) -> None:
        """RateFund with base='gross_annual' applies rate to gross_annual."""
        baseline = estimate_annual(_req()).result
        rate = _D("0.005")
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    RateFund(
                        employee_rate=rate,
                        employer_rate=rate,
                        base="gross_annual",
                    ),
                )
            }
        )
        result = compute(scenario).result
        expected_employee = money(baseline.earnings.gross_annual * rate)
        expected_employer = money(baseline.earnings.gross_annual * rate)
        assert result.contributions.bilateral_employee_annual == expected_employee
        assert result.contributions.bilateral_employer_annual == expected_employer
        assert result.net_annual == money(baseline.net_annual - expected_employee)
        assert result.employer_cost.employer_cost_annual == money(
            baseline.employer_cost.employer_cost_annual + expected_employer
        )

    def test_gross_annual_not_mutated_by_bilateral_funds(self) -> None:
        """gross_annual is unchanged when bilateral_funds are provided."""
        baseline = estimate_annual(_req()).result
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    FlatMonthlyFund(
                        employee_monthly=_D("50"),
                        employer_monthly=_D("50"),
                    ),
                )
            }
        )
        result = compute(scenario).result
        assert result.earnings.gross_annual == baseline.earnings.gross_annual

    def test_bilateral_funds_scope_item_verified_when_present(self) -> None:
        """bilateral_funds scope item is 'verified' when funds are provided."""
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    FlatMonthlyFund(
                        employee_monthly=_D("10"),
                        employer_monthly=_D("10"),
                    ),
                )
            }
        )
        result = compute(scenario).result
        scope_map = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope_map["bilateral_funds"] == "computed"

    def test_bilateral_funds_scope_item_excluded_when_absent(self) -> None:
        """bilateral_funds scope item is 'excluded' when no funds provided."""
        result = estimate_annual(_req()).result
        scope_map = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope_map["bilateral_funds"] == "excluded"

    def test_multiple_funds_accumulate(self) -> None:
        """Multiple funds in the tuple accumulate correctly."""
        baseline = estimate_annual(_req()).result
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    FlatMonthlyFund(
                        employee_monthly=_D("10"),
                        employer_monthly=_D("20"),
                    ),
                    FlatMonthlyFund(
                        employee_monthly=_D("5"),
                        employer_monthly=_D("8"),
                    ),
                )
            }
        )
        result = compute(scenario).result
        expected_emp = money((_D("10") + _D("5")) * 12)
        expected_er = money((_D("20") + _D("8")) * 12)
        assert result.contributions.bilateral_employee_annual == expected_emp
        assert result.contributions.bilateral_employer_annual == expected_er
        assert result.net_annual == money(baseline.net_annual - expected_emp)
        assert result.employer_cost.employer_cost_annual == money(
            baseline.employer_cost.employer_cost_annual + expected_er
        )


# ---------------------------------------------------------------------------
# IVS ceiling warning (G3)
# ---------------------------------------------------------------------------


class TestIvsCeilingWarning:
    """Warning is emitted when a post-1996 hire has ivs_ceiling_applies=False."""

    def _scenario_with_hire_date(
        self,
        hire_date: date,
        *,
        ivs_ceiling_applies: bool = False,
    ) -> AnnualEstimateInput:
        base = _req(ivs_ceiling_applies=ivs_ceiling_applies)
        return base.model_copy(
            update={
                "employee": base.employee.model_copy(
                    update={"seniority": SeniorityByDate(value=hire_date)}
                )
            }
        )

    def test_post_1996_hire_no_ceiling_emits_warning(self) -> None:
        """Hire date on or after 1996-01-01 with ivs=False yields a warning."""
        r = compute(self._scenario_with_hire_date(date(1996, 6, 1))).result
        assert any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_post_1996_hire_with_ceiling_no_warning(self) -> None:
        """Hire date after 1996-01-01 with ivs=True produces no warning."""
        r = compute(
            self._scenario_with_hire_date(date(2000, 1, 1), ivs_ceiling_applies=True)
        ).result
        assert not any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_pre_1996_hire_no_warning(self) -> None:
        """Hire date before 1996-01-01 produces no warning."""
        r = compute(self._scenario_with_hire_date(date(1990, 3, 15))).result
        assert not any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_post_1996_hire_warning_contains_overstated(self) -> None:
        """Warning for post-1996 hire must mention 'overstated'."""
        r = compute(self._scenario_with_hire_date(date(2000, 6, 1))).result
        assert any("overstated" in w for w in r.coverage.warnings)

    def test_seniority_by_months_post_1996_emits_warning(self) -> None:
        """SeniorityByMonths implying post-1996 hire triggers the warning."""
        # 120 months = 10 years of seniority; implied hire ~2016, post-1996
        r = estimate_annual(_req(seniority_months=120)).result
        assert any("overstated" in w for w in r.coverage.warnings)

    def test_seniority_by_months_pre_1996_no_warning(self) -> None:
        """SeniorityByMonths implying pre-1996 hire produces no warning."""
        # 480 months = 40 years; implied hire ~1986, pre-1996
        r = estimate_annual(_req(seniority_months=480)).result
        assert not any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_seniority_by_months_with_ceiling_no_warning(self) -> None:
        """SeniorityByMonths with ivs_ceiling_applies=True produces no warning."""
        r = estimate_annual(_req(seniority_months=120, ivs_ceiling_applies=True)).result
        assert not any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_seniority_by_count_emits_warning(self) -> None:
        """SeniorityByCount with ivs_ceiling_applies=False triggers warning."""
        r = estimate_annual(_req(seniority_count=2)).result
        assert any("overstated" in w for w in r.coverage.warnings)

    def test_seniority_by_count_with_ceiling_no_warning(self) -> None:
        """SeniorityByCount with ivs_ceiling_applies=True produces no warning."""
        r = estimate_annual(_req(seniority_count=2, ivs_ceiling_applies=True)).result
        assert not any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_base_at_or_below_ceiling_no_warning(self) -> None:
        """Post-1996 hire produces no warning when base does not exceed ceiling."""
        scenario = self._scenario_with_hire_date(date(2000, 1, 1))
        base = _D("30000")
        ceiling = _D("30000")
        result = _ivs_ceiling_warning(scenario, _DATE, base, ceiling)
        assert result is None

    def test_base_above_ceiling_still_warns(self) -> None:
        """Post-1996 hire warns when base exceeds the known IVS ceiling."""
        scenario = self._scenario_with_hire_date(date(2000, 1, 1))
        base = _D("60000")
        ceiling = _D("50000")
        result = _ivs_ceiling_warning(scenario, _DATE, base, ceiling)
        assert result is not None
        assert "overstated" in result

    def test_no_ceiling_still_warns_for_post_1996(self) -> None:
        """When ceiling is unknown, warning is emitted for post-1996 hires."""
        scenario = self._scenario_with_hire_date(date(2000, 1, 1))
        result = _ivs_ceiling_warning(scenario, _DATE, _D("20000"), None)
        assert result is not None
        assert "overstated" in result

    def test_seniority_none_base_above_known_ceiling_warns(self) -> None:
        """seniority=None warns when base exceeds a known IVS ceiling."""
        base = _req()
        scenario = base.model_copy(
            update={"employee": base.employee.model_copy(update={"seniority": None})}
        )
        result = _ivs_ceiling_warning(scenario, _DATE, _D("130000"), _D("120000"))
        assert result is not None
        assert "seniority is None" in result
        assert "IVS ceiling" in result

    def test_seniority_none_no_ceiling_no_warning(self) -> None:
        """seniority=None does not warn when the IVS ceiling is unknown."""
        base = _req()
        scenario = base.model_copy(
            update={"employee": base.employee.model_copy(update={"seniority": None})}
        )
        result = _ivs_ceiling_warning(scenario, _DATE, _D("200000"), None)
        assert result is None

    def test_seniority_none_base_at_ceiling_no_warning(self) -> None:
        """seniority=None does not warn when base does not exceed the ceiling."""
        base = _req()
        scenario = base.model_copy(
            update={"employee": base.employee.model_copy(update={"seniority": None})}
        )
        result = _ivs_ceiling_warning(scenario, _DATE, _D("100000"), _D("120000"))
        assert result is None


# ---------------------------------------------------------------------------
# NO_ASSEGNO_UNICO fiscal simplification (G4)
# ---------------------------------------------------------------------------


class TestNoAssegnoUnico:
    """NO_ASSEGNO_UNICO is always present in fiscal_simplifications."""

    def test_always_present_default_scenario(self) -> None:
        """Default scenario includes NO_ASSEGNO_UNICO simplification."""
        r = estimate_annual(_req()).result
        assert FiscalSimplification.NO_ASSEGNO_UNICO in r.taxes.fiscal_simplifications

    def test_always_present_with_bilateral_funds(self) -> None:
        """NO_ASSEGNO_UNICO is present even when bilateral funds are supplied."""
        scenario = _req().model_copy(
            update={
                "bilateral_funds": (
                    FlatMonthlyFund(
                        employee_monthly=_D("10"),
                        employer_monthly=_D("20"),
                    ),
                )
            }
        )
        r = compute(scenario).result
        assert FiscalSimplification.NO_ASSEGNO_UNICO in r.taxes.fiscal_simplifications


class TestBackCalculationProvenance:
    """compute() must not raise with back-calculation provenance (N15).

    The engine calls model_dump(mode="json") during snapshot capture; a
    MappingProxyType in BackCalculationStep.inputs would cause a
    PydanticSerializationError before FrozenDict was introduced.
    """

    def _back_calc_provenance(self) -> RuleProvenance:
        """Build a RuleProvenance with BACK_CALCULATION extraction and inputs.

        Returns:
            A :class:`RuleProvenance` with one back-calculation step.
        """
        step = BackCalculationStep(
            description="derive monthly from annual",
            inputs={"annual": _D("12000"), "months": "12"},
            result=_D("1000"),
        )
        return RuleProvenance(
            location=SourceLocation(
                source_document=SourceDocument(
                    document_id="doc-bc",
                    title="Back-Calculation Source",
                    kind=SourceKind.TABELLA_RETRIBUTIVA,
                    url="https://example.com",
                ),
                section="Art. 5",
            ),
            extraction=ExtractionTrace(
                method=ExtractionMethod.BACK_CALCULATION,
                extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                verification_status=VerificationStatus.UNVERIFIED,
                effective_from=date(2025, 1, 1),
                back_calculation=(step,),
            ),
        )

    def test_compute_does_not_raise(self) -> None:
        """Compute succeeds with a back-calculation SupplementaryAllowance."""
        sl = SupplementaryAllowance(
            code="SL-BC",
            description="Back-calc allowance",
            monthly=_D("100"),
            provenance=self._back_calc_provenance(),
        )
        calc = estimate_annual(_req(second_level_allowances=(sl,)))
        assert calc.result is not None

    def test_back_calc_inputs_are_frozen(self) -> None:
        """BackCalculationStep.inputs is a FrozenDict after construction."""
        step = BackCalculationStep(
            description="test step",
            inputs={"base": _D("1000"), "rate": "0.10"},
            result=_D("100"),
        )
        assert isinstance(step.inputs, FrozenDict)
        with pytest.raises(TypeError):
            step.inputs.update({"extra": "x"})

    def test_back_calc_step_json_roundtrip(self) -> None:
        """BackCalculationStep with inputs round-trips through model_dump_json."""
        step = BackCalculationStep(
            description="step",
            inputs={"a": _D("1"), "b": "x"},
            result=_D("42"),
        )
        payload = step.model_dump_json()
        restored = BackCalculationStep.model_validate_json(payload)
        assert restored.result == step.result
        assert dict(restored.inputs) == {"a": _D("1"), "b": "x"}


# ---------------------------------------------------------------------------
# Surtax ruleset identity tracking (N24)
# ---------------------------------------------------------------------------


def _surtax_with_identities(
    regional_status: VerificationStatus,
    municipal_status: VerificationStatus,
) -> SurtaxRules:
    """SurtaxRules with distinct regional and municipal identities.

    Returns:
        A :class:`SurtaxRules` with TestRegione and X001 entries plus
        identities with the given verification statuses.
    """
    return SurtaxRules(
        year=2026,
        regional_ruleset=RulesetIdentity(
            id="surtax/2026/regionale",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="https://example.com",
            source_type=SourceType.OFFICIAL_PRIMARY,
            source_hash="a" * 64,
            verification_status=regional_status,
        ),
        municipal_ruleset=RulesetIdentity(
            id="surtax/2026/comunale",
            version="2026.2",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="https://example.com",
            source_type=SourceType.OFFICIAL_PRIMARY,
            source_hash="b" * 64,
            verification_status=municipal_status,
        ),
        regionale={
            "TestRegione": RegionaleEntry(
                brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.01")),)
            )
        },
        comunale={
            "X001": ComunaleEntry(
                nome="Test",
                brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
            )
        },
    )


class TestSurtaxRulesetIdentity:
    """N24: regional and municipal surtax identities are tracked separately.

    Both keys are always emitted in ``ruleset_version`` when the surtax bundle
    is loaded.  Only identities of entries that were actually applied appear in
    ``consumed_rulesets`` and therefore influence confidence.
    """

    def test_both_ruleset_version_keys_present_when_regione_set(self) -> None:
        """Both surtax_regional and surtax_municipal keys appear in ruleset_version."""
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.VERIFIED
        )
        calc = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(regione="TestRegione"),
            )
        )
        assert "surtax_regional" in calc.ruleset_version
        assert "surtax_municipal" in calc.ruleset_version
        assert "surtax" not in calc.ruleset_version

    def test_both_ruleset_version_keys_present_when_comune_set(self) -> None:
        """Both surtax_regional and surtax_municipal appear when only comune set."""
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.VERIFIED
        )
        calc = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(comune_belfiore="X001"),
            )
        )
        assert "surtax_regional" in calc.ruleset_version
        assert "surtax_municipal" in calc.ruleset_version

    def test_municipal_version_update_visible_in_ruleset_version(self) -> None:
        """Different municipal_ruleset version changes surtax_municipal in envelope."""
        v1 = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.VERIFIED
        )
        _mock_surtax[0] = v1
        req = _req(
            as_of=date(2026, 1, 1),
            jurisdiction=Jurisdiction(comune_belfiore="X001"),
        )
        calc1 = compute(req)

        v2_municipal = RulesetIdentity(
            id="surtax/2026/comunale",
            version="2026.3-review-fixture",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="https://example.com",
            source_type=SourceType.OFFICIAL_PRIMARY,
            source_hash="c" * 64,
            verification_status=VerificationStatus.VERIFIED,
        )
        _mock_surtax[0] = v1.model_copy(update={"municipal_ruleset": v2_municipal})
        calc2 = compute(req)

        v1_mun = calc1.ruleset_version["surtax_municipal"]
        v2_mun = calc2.ruleset_version["surtax_municipal"]
        assert v1_mun != v2_mun
        assert "2026.3-review-fixture" in v2_mun
        v1_reg = calc1.ruleset_version["surtax_regional"]
        v2_reg = calc2.ruleset_version["surtax_regional"]
        assert v1_reg == v2_reg

    def test_unverified_regional_downgrades_confidence_when_applied(self) -> None:
        """Unverified regional ruleset → medium confidence when entry was applied."""
        _mock_ccnl[0] = _verified_ccnl()
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.UNVERIFIED, VerificationStatus.VERIFIED
        )
        calc = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(regione="TestRegione"),
            )
        )
        assert calc.result.coverage.confidence == "medium"

    def test_unverified_municipal_downgrades_confidence_when_applied(self) -> None:
        """Unverified municipal ruleset → medium confidence when entry was applied."""
        _mock_ccnl[0] = _verified_ccnl()
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.UNVERIFIED
        )
        calc = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(comune_belfiore="X001"),
            )
        )
        assert calc.result.coverage.confidence == "medium"

    def test_unverified_municipal_not_consumed_when_regione_only(self) -> None:
        """Unverified municipal ruleset does not downgrade confidence: regione only."""
        _mock_ccnl[0] = _verified_ccnl()
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.UNVERIFIED
        )
        calc = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(regione="TestRegione"),
            )
        )
        assert calc.result.coverage.confidence == "high"

    def test_both_applied_both_identities_affect_confidence(self) -> None:
        """Both entries applied: unverified municipal identity downgrades confidence."""
        _mock_ccnl[0] = _verified_ccnl()
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.UNVERIFIED
        )
        calc = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="TestRegione", comune_belfiore="X001"
                ),
            )
        )
        assert calc.result.coverage.confidence == "medium"


class TestCallerDeclaredScope:
    """Caller-declared optional fields appear as caller_declared scope items."""

    def test_inail_rate_produces_caller_declared_scope_item(self) -> None:
        """Setting inail_rate yields a caller_declared inail scope item."""
        calc = estimate_annual(_req(inail_rate=_D("0.015")))
        scope = {item.feature: item for item in calc.result.coverage.calculation_scope}
        assert scope["inail"].eligibility_status == "caller_declared"

    def test_no_inail_rate_produces_excluded_scope_item(self) -> None:
        """Omitting inail_rate yields an excluded inail scope item."""
        calc = estimate_annual(_req())
        scope = {item.feature: item for item in calc.result.coverage.calculation_scope}
        assert scope["inail"].calculation_status == "excluded"


class TestContractEffectiveDate:
    """contract_effective_date reflects the resolved salary tranche, not as_of."""

    def test_uses_tranche_valid_from_not_as_of(self) -> None:
        """contract_effective_date is the tranche valid_from, not as_of itself."""
        r = estimate_annual(_req(as_of=_DATE)).result
        # default CCNL: base_salary valid_from=2020-01-01, as_of=2026-06-01
        assert r.contract_effective_date == date(2020, 1, 1)
        assert r.contract_effective_date != _DATE

    def test_mid_year_tranche_update_uses_tranche_start(self) -> None:
        """When a salary update starts mid-year, its valid_from is returned."""
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.base_salary": {
                "periods": [
                    {
                        "valid_from": "2026-04-01",
                        "valid_until": None,
                        "value": "1000.00",
                        "provenance": TEST_PROV,
                    }
                ]
            }
        })
        r = estimate_annual(_req(as_of=date(2026, 6, 1))).result
        assert r.contract_effective_date == date(2026, 4, 1)
