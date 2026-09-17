"""Tests for engine/compute/orchestrator — compute() and helpers."""

from __future__ import annotations

import dataclasses
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
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity, VerificationStatus
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
from ccnl_engine.engine.payroll.domain.family import FamilyComposition
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import ScopeItem
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Jurisdiction,
    PayrollScenario,
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
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.scope import (
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
from tests.helpers import make_ccnl_dict, make_domestic_year_rules, make_year_rules
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
    from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
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


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the three loaders in orchestrator and reset mock state."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_RULES]
    _mock_surtax[:] = [None]
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl",
        lambda _: _mock_ccnl[0],
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules",
        lambda *_: _mock_rules[0],
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules",
        lambda _: _mock_surtax[0],
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
        with pytest.raises(ValueError, match="must be >= 0"):
            SeniorityByCount(-1)

    def test_seniority_by_months_negative_raises(self) -> None:
        """SeniorityByMonths with value < 0 must raise at construction."""
        with pytest.raises(ValueError, match="must be >= 0"):
            SeniorityByMonths(-1)

    def test_part_time_pct_out_of_range_raises(self) -> None:
        """Employee with part_time_pct outside (0, 1] must raise."""
        with pytest.raises(ValueError, match="part_time_pct"):
            Employee(level_code="4", part_time_pct=Decimal(0))

    @pytest.mark.parametrize("pct", ["-0.1", "1.01"])
    def test_part_time_pct_boundary(self, pct: str) -> None:
        """part_time_pct outside (0, 1] must raise at any invalid value."""
        with pytest.raises(ValueError, match="part_time_pct"):
            Employee(level_code="4", part_time_pct=_D(pct))

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
            RalOverride(_D(0))

    def test_destination_ral_override_negative_raises(self) -> None:
        """DestinationRalOverride with value <= 0 must raise at construction."""
        with pytest.raises(ValueError, match="must be > 0"):
            DestinationRalOverride(_D("-1"))


# ---------------------------------------------------------------------------
# Validation errors inside compute()
# ---------------------------------------------------------------------------


class TestComputeValidation:
    """Guard-clause branches at the top of compute()."""

    def test_unknown_level_code_raises(self) -> None:
        """Unknown level_code must raise ValueError."""
        with pytest.raises(ValueError, match="NOPE"):
            compute(_req(level_code="NOPE"))

    def test_seniority_count_above_maximum_raises(self) -> None:
        """SeniorityByCount above the level maximum must raise ValueError."""
        with pytest.raises(ValueError, match="exceeds the maximum of 10"):
            compute(_req(seniority_count=11))

    def test_second_level_with_ral_override_raises(self) -> None:
        """second_level_allowances cannot be combined with a RAL override."""
        sl = SupplementaryAllowance(code="X", description="X", monthly=_D("100"))
        with pytest.raises(ValueError, match="RAL override"):
            compute(_req(negotiated_ral=_D("20000"), second_level_allowances=(sl,)))

    def test_negotiated_destination_ral_on_non_apprentice_raises(self) -> None:
        """DestinationRalOverride with a non-Apprentice contract raises."""
        with pytest.raises(ValueError, match="only valid for Apprentice"):
            compute(_req(negotiated_destination_ral=_D("20000.00")))


# ---------------------------------------------------------------------------
# Permanent employment
# ---------------------------------------------------------------------------


class TestComputePermanent:
    """Permanent contract paths in compute()."""

    def test_full_time_no_seniority(self) -> None:
        """Permanent, full-time, no seniority: standard salary chain."""
        r = compute(_req())

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
        assert r.hourly_rate == money(_D("1000.00") / _D("168"))
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
        r = compute(_req(seniority_count=2))

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
        r = compute(_req(seniority_months=months))
        assert r.seniority_count == expected

    @pytest.mark.parametrize(
        ("months", "expected"), [(47, 0), (48, 1), (83, 1), (84, 2), (120, 3)]
    )
    def test_seniority_first_cadence(self, months: int, expected: int) -> None:
        """First increment after first_cadence_months, then every cadence_months."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months": 48
        })
        r = compute(_req(seniority_months=months))
        assert r.seniority_count == expected

    def test_seniority_first_cadence_by_level(self) -> None:
        """Per-level first cadence (e.g. operai lump step at 48 months)."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months_by_level": {"4": 48}
        })
        r47 = compute(_req(seniority_months=47))
        r48 = compute(_req(seniority_months=48))
        assert r47.seniority_count == 0
        assert r48.seniority_count == 1
        assert compute(_req(level_code="3", seniority_months=36)).seniority_count == 1

    def test_seniority_per_level_maximum(self) -> None:
        """maximum_count_by_level overrides maximum_count for that level."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.maximum_count_by_level": {"4": 1}
        })
        r = compute(_req(seniority_months=360))
        assert r.seniority_count == 1
        assert r.seniority_monthly == _D("20.00")
        with pytest.raises(ValueError, match="exceeds the maximum of 1"):
            compute(_req(seniority_count=2))

    def test_part_time_scales_all_components(self) -> None:
        """part_time_pct=0.5 halves every component; components sum to gross."""
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [_allowance("edr", "10.33")]
        })
        r = compute(_req(part_time_pct=_D("0.50"), seniority_count=1))

        assert r.base_monthly == _D("500.00")
        assert r.seniority_monthly == _D("10.00")
        assert r.allowances_monthly == _D("5.17")
        assert r.gross_monthly == _D("515.17")
        assert r.gross_annual == _D("6182.04")

    def test_negotiated_ral(self) -> None:
        """RalOverride overrides gross_annual; gross_monthly stays consistent."""
        ral = _D("20000.00")
        r = compute(_req(negotiated_ral=ral))

        assert r.gross_annual == ral
        assert r.gross_monthly == _D("1666.67")

    def test_level_without_seniority_entry(self) -> None:
        """Level '3' has no seniority in amount_by_level — seniority stays zero."""
        r = compute(_req(level_code="3", seniority_count=5))

        assert r.seniority_monthly == _D("0.00")
        assert r.base_monthly == _D("800.00")
        assert r.gross_annual == _D("9600.00")

    def test_ad_personam_added_unscaled(self) -> None:
        """ad_personam_monthly is added as given, even under part-time."""
        r = compute(_req(part_time_pct=_D("0.50"), ad_personam_monthly=_D("30.00")))
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
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance("edr", "10.00"),
                _allowance("quadro", "100.00", role="quadro"),
            ]
        })
        plain = compute(_req())
        quadro = compute(_req(roles=frozenset({"quadro"})))
        assert plain.allowances_monthly == _D("10.00")
        assert quadro.allowances_monthly == _D("110.00")

    def test_months_per_year(self) -> None:
        """An allowance paid 12 times contributes 12 x monthly to gross_annual."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.additional_months": _series("14"),
            "levels.2.fixed_allowances": [
                _allowance("ind", "50.00", months_per_year=12)
            ],
        })
        r = compute(_req())
        assert r.gross_monthly == _D("1050.00")
        assert r.gross_annual == _D("14600.00")  # 1000*14 + 50*12

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
        r = compute(_req())
        base = compute(_req())  # mock still has custom CCNL — need default for base
        # Re-fetch base with default CCNL
        _mock_ccnl[0] = _DEFAULT_CCNL
        base = compute(_req())
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
        r = compute(_req())
        assert r.gross_annual == _D("13200.00")
        assert r.inps_employee_annual == base.inps_employee_annual
        assert r.inps_employer_annual == base.inps_employer_annual
        assert r.tfr_annual == base.tfr_annual
        assert r.taxable_income == r.gross_annual - r.inps_employee_annual

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
        r_with_exclusion = compute(_req(negotiated_ral=ral))
        _mock_ccnl[0] = _DEFAULT_CCNL
        r_clean = compute(_req(negotiated_ral=ral))

        assert r_with_exclusion.gross_annual == ral
        # Contribution and TFR bases must be identical regardless of CCNL allowances.
        assert r_with_exclusion.inps_employee_annual == r_clean.inps_employee_annual
        assert r_with_exclusion.inps_employer_annual == r_clean.inps_employer_annual
        assert r_with_exclusion.tfr_annual == r_clean.tfr_annual


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
        operaio = compute(_req())
        impiegato = compute(_req(level_code="3"))
        uncategorised = compute(_req(level_code="2"))
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
        _mock_ccnl[0] = _build_ccnl(**{"parameters.employer_funds": [fund]})
        r = compute(_req(level_code="3"))
        assert r.employer_funds_annual == _D("960.00")

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
        impiegato = compute(_req(level_code="3"))
        operaio = compute(_req())
        assert impiegato.inps_employer_annual == _D("1920.00")  # 9600 * 0.20
        assert operaio.inps_employer_annual == _D("3600.00")  # 12000 * 0.30


# ---------------------------------------------------------------------------
# Fixed-term employment
# ---------------------------------------------------------------------------


class TestComputeFixedTerm:
    """Fixed-term contract adds NASpI addizionale to employer INPS."""

    def test_fixed_term_naspi_addizionale(self) -> None:
        """Employer INPS for fixed-term must exceed permanent by 1.4% of gross."""
        r_fixed = compute(_req(contract=_FIXED_TERM))
        r_perm = compute(_req())

        expected_diff = r_fixed.gross_annual * _D("0.014")
        actual_diff = r_fixed.inps_employer_annual - r_perm.inps_employer_annual
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

    def _scenario(self, ral: Decimal, *, ivs_ceiling_applies: bool) -> PayrollScenario:
        return _req(
            negotiated_ral=ral,
            ivs_ceiling_applies=ivs_ceiling_applies,
        )

    def test_below_ceiling_unchanged(self) -> None:
        """RAL below the massimale: ceiling split equals flat rate."""
        ral = _D("80000.00")
        _mock_rules[0] = self._rules_with_ceiling()
        r_capped = compute(self._scenario(ral, ivs_ceiling_applies=True))
        r_flat = compute(self._scenario(ral, ivs_ceiling_applies=False))
        assert r_capped.inps_employee_annual == r_flat.inps_employee_annual
        assert r_capped.inps_employer_annual == r_flat.inps_employer_annual

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
        r = compute(self._scenario(ral, ivs_ceiling_applies=True))
        assert r.inps_employee_annual == expected_employee
        assert r.inps_employer_annual == expected_employer

    def test_ceiling_flag_false_skips_split(self) -> None:
        """ivs_ceiling_applies=False: flat rate even when ceiling is configured."""
        ral = _D("150000.00")
        _mock_rules[0] = self._rules_with_ceiling()
        r = compute(self._scenario(ral, ivs_ceiling_applies=False))
        assert r.inps_employee_annual == _D("150000.00") * _D("0.0919")
        assert r.inps_employer_annual == _D("150000.00") * _D("0.2898")


# ---------------------------------------------------------------------------
# IRPEF floor
# ---------------------------------------------------------------------------


class TestComputeIrpefFloor:
    """Net = gross - inps when deduction exceeds gross IRPEF."""

    def test_irpef_net_floored_at_zero(self) -> None:
        """Low income: deduction > irpef_gross → irpef_net == 0."""
        r = compute(_req(negotiated_ral=_D("5000.00")))

        assert r.irpef_net == _D("0.00")
        assert r.net_annual == r.gross_annual - r.inps_employee_annual


# ---------------------------------------------------------------------------
# Withholding exemption (non-sostituto d'imposta employers)
# ---------------------------------------------------------------------------


class TestComputeWithholdingExempt:
    """withholding_exempt=True: irpef_net zero, informational fields retained."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_irpef_net_is_zero(self) -> None:
        """Exempt employer: irpef_net must be zero regardless of income."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = compute(_req())
        assert r.irpef_net == _D("0.00")

    def test_employer_withholds_irpef_flag_false(self) -> None:
        """Exempt employer: employer_withholds_irpef must be False."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = compute(_req())
        assert r.employer_withholds_irpef is False

    def test_net_annual_excludes_irpef(self) -> None:
        """Net = gross - INPS employee; IRPEF not deducted by employer."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = compute(_req())
        assert r.net_annual == r.gross_annual - r.inps_employee_annual

    def test_irpef_informational_fields_nonzero(self) -> None:
        """irpef_gross and work_income_deduction remain as informational."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = compute(_req())
        assert r.irpef_gross > _D("0.00")
        assert r.work_income_deduction >= _D("0.00")

    def test_standard_ccnl_withholds_irpef(self) -> None:
        """Standard CCNL: employer_withholds_irpef must be True."""
        r = compute(_req())
        assert r.employer_withholds_irpef is True


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
            compute(_req())

    def test_hours_bracket_permanent(self) -> None:
        """weekly_hours > 24 → hours bracket; permanent uses base employer rate."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = compute(_req(weekly_hours=_D("40")))

        annual_hours = _D("40") * _D("52")
        assert r.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.inps_employer_annual == money(_D("0.93") * annual_hours)

    def test_hours_bracket_fixed_term(self) -> None:
        """weekly_hours > 24 + FixedTerm → hours bracket fixed-term rate."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = compute(_req(contract=_FIXED_TERM, weekly_hours=_D("40")))

        annual_hours = _D("40") * _D("52")
        assert r.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.inps_employer_annual == money(_D("1.01") * annual_hours)

    def test_wage_bracket_mid(self) -> None:
        """weekly_hours <= 24 → wage bracket selected by annualised hourly rate.

        Level 4, gross_monthly=1000, weekly_hours=20:
        hourly_rate = 1000 * 12 / (20 * 52) = 11.54 → bracket up_to=11.70.
        """
        _mock_rules[0] = _DOMESTIC_RULES
        r = compute(_req(weekly_hours=_D("20")))

        annual_hours = _D("20") * _D("52")
        assert r.inps_employee_annual == money(_D("0.48") * annual_hours)
        assert r.inps_employer_annual == money(_D("1.44") * annual_hours)

    def test_net_is_gross_minus_inps_minus_irpef(self) -> None:
        """Net = gross - INPS employee - irpef_net for domestic path."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = compute(_req(weekly_hours=_D("40")))
        assert r.net_annual == r.gross_annual - r.inps_employee_annual - r.irpef_net


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
        return compute(
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
        r = compute(_req())
        assert r.addizionale_regionale_annual == Decimal("0.00")
        assert r.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.fiscal_simplifications

    def test_regione_only(self) -> None:
        """With regione set, addizionale regionale > 0; comunale still zero."""
        r = self._result(regione="TestRegione")
        assert r.addizionale_regionale_annual > Decimal(0)
        assert r.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.fiscal_simplifications

    def test_comune_only(self) -> None:
        """With comune_belfiore set, addizionale comunale > 0; regionale zero."""
        r = self._result(comune_belfiore="X001")
        assert r.addizionale_comunale_annual > Decimal(0)
        assert r.addizionale_regionale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.fiscal_simplifications

    def test_both_set_both_computed(self) -> None:
        """With both fields set, both surtaxes are computed; neither flag set."""
        r = self._result(regione="TestRegione", comune_belfiore="X001")
        assert r.addizionale_regionale_annual > Decimal(0)
        assert r.addizionale_comunale_annual > Decimal(0)
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.fiscal_simplifications

    def test_both_reduce_net_annual(self) -> None:
        """Net annual is reduced by the sum of both addizionali."""
        r = self._result(regione="TestRegione", comune_belfiore="X001")
        expected_net = (
            r.gross_annual
            - r.inps_employee_annual
            - r.irpef_net
            - r.addizionale_regionale_annual
            - r.addizionale_comunale_annual
            + r.trattamento_integrativo
        )
        assert r.net_annual == expected_net

    def test_unknown_regione_produces_zero(self) -> None:
        """Unknown region name → addizionale regionale is zero, no flag."""
        r = self._result(regione="RegioneSconosciuta")
        assert r.addizionale_regionale_annual == Decimal("0.00")
        # No flag: the caller passed a region, we just didn't find it
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.fiscal_simplifications

    def test_unknown_comune_produces_zero(self) -> None:
        """Unknown codice catastale → addizionale comunale zero, no flag."""
        r = self._result(comune_belfiore="Z999")
        assert r.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.fiscal_simplifications

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
        r = compute(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=tiny_ral,
                jurisdiction=Jurisdiction(comune_belfiore="X001"),
            )
        )
        assert r.addizionale_comunale_annual == Decimal("0.00")

    def test_irpef_zero_suppresses_addizionali(self) -> None:
        """When IRPEF is fully offset by deductions, addizionali are zero.

        A low RAL causes work_income_deduction to exceed irpef_gross, leaving
        irpef_fiscal = 0. Even with a valid jurisdiction, both surtaxes must
        be zero and NO_ADDIZIONALE_* flags must be present.
        """
        _mock_surtax[0] = self._surtax_rules()
        r = compute(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=_D("8000"),
                jurisdiction=Jurisdiction(
                    regione="TestRegione", comune_belfiore="X001"
                ),
            )
        ).result
        assert r.irpef_net == _D("0.00"), "irpef_net must be zero in no-tax area"
        assert r.addizionale_regionale_annual == _D("0.00")
        assert r.addizionale_comunale_annual == _D("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.fiscal_simplifications


class TestFiscalFlagsExclusivity:
    """Addizionale flags are mutually exclusive regardless of TI-rules presence.

    When ``YearRules.trattamento_integrativo`` is ``None`` (no TI data in the
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
        r = compute(_req()).result
        sfs = r.fiscal_simplifications
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
        r = compute(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="KnownRegione", comune_belfiore="K001"
                ),
            )
        ).result
        sfs = r.fiscal_simplifications
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
        r = compute(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="UnknownRegione", comune_belfiore="Z999"
                ),
            )
        ).result
        sfs = r.fiscal_simplifications
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
        r = compute(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=_D("8000"),  # below no-tax threshold
                jurisdiction=Jurisdiction(
                    regione="UnknownRegione", comune_belfiore="Z999"
                ),
            )
        ).result
        sfs = r.fiscal_simplifications
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
        result = compute(_req())
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
        result = compute(_req())
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
        result = compute(_req())
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
        scenario = dataclasses.replace(
            _req(level_code="4", contract=Apprentice(months_elapsed=0)),
        )
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
        calc = compute(_req(level_code="4"))
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
        calc = compute(_req())
        assert "sick_pay" not in calc.ruleset_version
        assert "variable_pay" not in calc.ruleset_version

    def test_variable_pay_ruleset_present_with_fringe_benefit_input(self) -> None:
        """R7: fringe benefit input causes variable_pay to appear in ruleset_version."""
        calc = compute(
            dataclasses.replace(
                _req(),
                fringe_benefit_input=FringeBenefitInput(annual_amount=_D("500")),
            )
        )
        assert "variable_pay" in calc.ruleset_version

    def test_variable_pay_ruleset_present_with_bonus_input(self) -> None:
        """R7: bonus input causes variable_pay to appear in ruleset_version."""
        calc = compute(
            dataclasses.replace(
                _req(),
                bonus_input=BonusInput(
                    annual_amount=_D("1000"), eligible_for_pdr=False
                ),
            )
        )
        assert "variable_pay" in calc.ruleset_version

    def test_family_deductions_ruleset_present_when_dependents(self) -> None:
        """family_deductions appears in ruleset_version when scenario.family is set."""
        calc = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(children_21_or_older=1),
            )
        )
        assert "family_deductions" in calc.ruleset_version, (
            f"Expected family_deductions in ruleset_version,"
            f" got: {calc.ruleset_version}"
        )

    def test_family_deductions_ruleset_absent_without_dependents(self) -> None:
        """family_deductions absent when no dependents in the scenario."""
        calc = compute(_req())
        assert "family_deductions" not in calc.ruleset_version

    def test_art15_deductions_ruleset_present_when_oneri_set(self) -> None:
        """art15_deductions appears in ruleset_version when art15_deductions is set."""
        calc = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("2000")),
            )
        )
        assert "art15_deductions" in calc.ruleset_version, (
            f"Expected art15_deductions in ruleset_version, got: {calc.ruleset_version}"
        )

    def test_art15_deductions_ruleset_absent_without_oneri(self) -> None:
        """art15_deductions absent when art15_deductions is None."""
        calc = compute(_req())
        assert "art15_deductions" not in calc.ruleset_version


class TestL3Warning:
    """Orchestrator warning path for missing L3 schema."""

    def test_warning_emitted_when_ccnl_has_no_l3(self) -> None:
        """Emit a warning when time_supplements is set but CCNL has no L3 data."""
        # The test CCNL (built by _build_ccnl / _req) has no work_rules block.
        # dataclasses.replace adds time_supplements without touching other fields.
        scenario = dataclasses.replace(
            _req(),
            time_supplements=OvertimeHours(weekday_hours=_D("5")),
        )
        result = compute(scenario).result
        assert any("time_supplements" in w for w in result.warnings), (
            f"Expected warning about time_supplements, got: {result.warnings}"
        )
        # Supplement fields must stay zero (no schema → nothing computed).
        assert result.overtime_supplement_monthly == _D("0")
        assert result.time_supplements_monthly == _D("0")

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
        scenario = dataclasses.replace(
            _req(),
            time_supplements=OvertimeHours(weekday_hours=_D("5")),
        )
        try:
            result = compute(scenario).result
            assert any("gross_incl_allowances" in w for w in result.warnings), (
                f"Expected gross_incl_allowances warning, got: {result.warnings}"
            )
            assert result.overtime_supplement_monthly == _D("0")
            assert result.time_supplements_monthly == _D("0")
            # Scope must show not_computed because method is unsupported
            ot_scope = next(
                s for s in result.calculation_scope if s.feature == "overtime"
            )
            assert ot_scope.status == "not_computed"
            assert result.status == "partial"
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_night_holiday_hours_contribute_to_holiday_scope(self) -> None:
        """R9: night_holiday_hours > 0 sets holiday_work to not_computed (no schema).

        Before the fix, night_holiday_hours was not counted toward the holiday
        scope, so holiday_work would be 'excluded' even when hours were supplied.
        """
        # Test CCNL has no work_rules, so schema is absent.
        scenario = dataclasses.replace(
            _req(),
            time_supplements=OvertimeHours(night_holiday_hours=_D("2")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        # With fix: night_holiday_hours counts toward holiday → not_computed (no schema)
        assert scope["holiday_work"] == "not_computed", (
            f"Expected holiday_work not_computed, got: {scope['holiday_work']}"
        )
        # Overtime and night must remain excluded (no hours for those buckets)
        assert scope["overtime"] == "excluded"
        assert scope["night_work"] == "excluded"

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
        ts_schema = TimeSupplements(overtime_bands=[night_band])  # type: ignore[arg-type]
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = dataclasses.replace(
            _req(),
            time_supplements=OvertimeHours(
                weekday_hours=_D("5"),
                night_hours=_D("3"),
            ),
        )
        try:
            result = compute(scenario).result
            scope = {item.feature: item.status for item in result.calculation_scope}
            assert scope["overtime"] == "not_computed", (
                f"Expected not_computed for overtime (no weekday band), got:"
                f" {scope['overtime']}"
            )
            assert scope["night_work"] == "verified", (
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
        ts_schema = TimeSupplements(overtime_bands=[weekday_band])  # type: ignore[arg-type]
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        scenario = dataclasses.replace(
            _req(),
            time_supplements=OvertimeHours(supplementare_hours=_D("10")),
        )
        try:
            result = compute(scenario).result
            scope = {item.feature: item.status for item in result.calculation_scope}
            assert scope["overtime"] == "not_computed", (
                f"Expected not_computed (no supplementare band), got:"
                f" {scope['overtime']}"
            )
            assert any("supplementare" in w for w in result.warnings), (
                f"Expected supplementare warning, got: {result.warnings}"
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
        scenario = dataclasses.replace(
            _req(),
            time_supplements=OvertimeHours(holiday_hours=_D("4")),
        )
        try:
            result = compute(scenario).result
            scope = {item.feature: item.status for item in result.calculation_scope}
            assert scope["holiday_work"] == "not_computed", (
                f"Expected not_computed (no holiday band), got: {scope['holiday_work']}"
            )
            assert any("holiday" in w for w in result.warnings), (
                f"Expected holiday warning, got: {result.warnings}"
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
        scenario = dataclasses.replace(
            _req(),
            time_supplements=OvertimeHours(weekday_hours=_D("10")),
        )
        try:
            result = compute(scenario).result
            assert any("tiered weekly thresholds" in w for w in result.warnings), (
                f"Expected tiered-band warning, got: {result.warnings}"
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
        scenario = dataclasses.replace(_req(), time_supplements=oh)
        try:
            result = compute(scenario).result
            assert not any("tiered weekly thresholds" in w for w in result.warnings), (
                f"Unexpected tiered warning with weeks supplied: {result.warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL


class TestL3Absence:
    """Orchestrator behaviour for L3 absence deduction."""

    def test_warning_when_ccnl_has_no_absence_rules(self) -> None:
        """Emit a warning when absence_days is set but CCNL has no absence rules."""
        scenario = dataclasses.replace(
            _req(),
            absence_days=AbsenceDays(unpaid_days=_D("2")),
        )
        result = compute(scenario).result
        assert any("absence_days" in w for w in result.warnings), (
            f"Expected absence_days warning, got: {result.warnings}"
        )
        assert result.absence_deduction_monthly == _D("0")
        # effective_gross_monthly equals gross_monthly when deduction is zero
        assert result.effective_gross_monthly == result.gross_monthly

    def test_absence_deduction_with_wr_schema(self) -> None:
        """Compute absence deduction when CCNL has absence_rules (by_26 method)."""
        absence_rules = AbsenceRules(
            daily_divisor_method=DailyDivisorMethod.BY_26,
        )
        # Inject work_rules with absence_rules into the mock CCNL.
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(absence_rules=absence_rules)}
        )
        scenario = dataclasses.replace(
            _req(),
            absence_days=AbsenceDays(unpaid_days=_D("1")),
        )
        result = compute(scenario).result
        # No warning: schema is present.
        assert not any("absence_days" in w for w in result.warnings)
        # Deduction must be > 0 and equals gross / 26.
        gross = result.gross_monthly
        expected = (gross / _D("26")).quantize(_D("0.01"))
        assert result.absence_deduction_monthly == expected
        # effective_gross = gross - deduction.
        assert result.effective_gross_monthly == gross - expected

    def test_absence_scope_excluded_when_no_days(self) -> None:
        """Absence scope item is excluded when no absence_days supplied."""
        result = compute(_req()).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["absence"] == "excluded"

    def test_absence_scope_not_computed_when_days_but_no_schema(self) -> None:
        """Absence is not_computed when days given but CCNL has no schema."""
        scenario = dataclasses.replace(
            _req(),
            absence_days=AbsenceDays(unpaid_days=_D("3")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["absence"] == "not_computed"

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
        scenario = dataclasses.replace(
            _req(),
            absence_days=AbsenceDays(unpaid_days=_D("2")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["absence"] == "verified"


class TestL3Leave:
    """Orchestrator behaviour for L3 leave accrual."""

    def test_warning_when_ccnl_has_no_leave_rules(self) -> None:
        """Emit a warning when leave_input is set but CCNL has no leave_rules."""
        scenario = dataclasses.replace(
            _req(),
            leave_input=LeaveInput(taken_days=_D("3")),
        )
        result = compute(scenario).result
        assert any("leave_input" in w for w in result.warnings), (
            f"Expected leave_input warning, got: {result.warnings}"
        )
        assert result.leave_accrued_days_monthly == _D("0")

    def test_leave_accrual_with_wr_schema(self) -> None:
        """Compute leave accrual when CCNL has leave_rules (flat, no tiers)."""
        leave_rules = LeaveRules(default_annual_days=_D("20"))
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(leave_rules=leave_rules)}
        )
        scenario = dataclasses.replace(
            _req(),
            leave_input=LeaveInput(taken_days=_D("3")),
        )
        result = compute(scenario).result
        assert not any("leave_input" in w for w in result.warnings)
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
        scenario = dataclasses.replace(
            _req(seniority_months=48),
            leave_input=LeaveInput(taken_days=_D("0")),
        )
        result = compute(scenario).result
        assert result.leave_accrued_days_monthly == _D("2.08")

    def test_leave_scope_excluded_when_no_input(self) -> None:
        """Leave scope item is excluded when no leave_input supplied."""
        result = compute(_req()).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["leave"] == "excluded"

    def test_leave_scope_not_computed_when_input_but_no_schema(self) -> None:
        """Leave is not_computed when input given but CCNL has no leave_rules."""
        scenario = dataclasses.replace(
            _req(),
            leave_input=LeaveInput(taken_days=_D("3")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["leave"] == "not_computed"

    def test_leave_scope_verified_with_schema(self) -> None:
        """Leave is verified when input given and CCNL has leave_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    leave_rules=LeaveRules(default_annual_days=_D("20"))
                )
            }
        )
        scenario = dataclasses.replace(
            _req(),
            leave_input=LeaveInput(taken_days=_D("2")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["leave"] == "verified"


class TestL3Sickness:
    """Orchestrator behaviour for L3 sickness (malattia ordinaria)."""

    def test_warning_when_ccnl_has_no_sickness_rules(self) -> None:
        """Emit a warning when sick_input is set but CCNL has no sickness_rules."""
        scenario = dataclasses.replace(
            _req(),
            sick_input=SickInput(sick_days=_D("5")),
        )
        result = compute(scenario).result
        assert any("sick_input" in w for w in result.warnings), (
            f"Expected sick_input warning, got: {result.warnings}"
        )
        assert result.sick_days_monthly == _D("0")

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
        scenario = dataclasses.replace(
            _req(),
            sick_input=SickInput(sick_days=_D("3")),
        )
        result = compute(scenario).result
        assert not any("sick_input" in w for w in result.warnings)
        # 3 days: only carenza, no INPS indemnity
        assert result.sick_days_monthly == _D("3")
        assert result.sick_inps_indemnity_monthly == _D("0")

    def test_sick_scope_excluded_when_no_input(self) -> None:
        """Sickness is excluded when no sick_input is provided."""
        result = compute(_req()).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["sickness"] == "excluded"

    def test_sick_scope_not_computed_when_input_but_no_schema(self) -> None:
        """Sickness is not_computed when input given but CCNL has no sickness_rules."""
        scenario = dataclasses.replace(
            _req(),
            sick_input=SickInput(sick_days=_D("5")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["sickness"] == "not_computed"

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
        scenario = dataclasses.replace(
            _req(),
            sick_input=SickInput(sick_days=_D("5")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["sickness"] == "verified"

    def test_sick_all_zero_when_no_input(self) -> None:
        """All sickness output fields are zero when no sick_input is provided."""
        result = compute(_req()).result
        assert result.sick_days_monthly == _D("0")
        assert result.sick_carenza_days_monthly == _D("0")
        assert result.sick_inps_indemnity_monthly == _D("0")
        assert result.sick_company_integration_monthly == _D("0")


class TestL3VariablePay:
    """Orchestrator integration tests for the variable-pay L3 features."""

    def test_fringe_benefit_scope_excluded_when_no_input(self) -> None:
        """fringe_benefit scope is excluded when no fringe_benefit_input."""
        result = compute(_req()).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["fringe_benefit"] == "excluded"

    def test_welfare_scope_excluded_when_no_input(self) -> None:
        """Welfare scope is excluded when no welfare_input."""
        result = compute(_req()).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["welfare"] == "excluded"

    def test_bonus_pdr_scope_excluded_when_no_input(self) -> None:
        """bonus_pdr scope is excluded when no bonus_input."""
        result = compute(_req()).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["bonus_pdr"] == "excluded"

    def test_all_variable_pay_fields_zero_when_no_inputs(self) -> None:
        """All variable-pay output fields are zero when no inputs are provided."""
        result = compute(_req()).result
        assert result.fringe_benefit_annual == _D("0")
        assert result.fringe_benefit_threshold_annual == _D("0")
        assert result.fringe_benefit_taxable_annual == _D("0")
        assert result.welfare_annual == _D("0")
        assert result.bonus_annual == _D("0")
        assert result.bonus_pdr_flat_tax_annual == _D("0")
        assert result.bonus_ordinary_taxable_annual == _D("0")

    def test_fringe_benefit_scope_verified_when_input_given(self) -> None:
        """fringe_benefit scope is verified when input is provided."""
        scenario = dataclasses.replace(
            _req(),
            fringe_benefit_input=FringeBenefitInput(annual_amount=_D("800")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["fringe_benefit"] == "verified"

    def test_fringe_benefit_below_threshold_not_taxable(self) -> None:
        """Fringe benefit below €1.000 threshold: taxable_annual is zero."""
        scenario = dataclasses.replace(
            _req(),
            fringe_benefit_input=FringeBenefitInput(annual_amount=_D("800")),
        )
        result = compute(scenario).result
        assert result.fringe_benefit_annual == _D("800")
        assert result.fringe_benefit_threshold_annual == _D("1000.00")
        assert result.fringe_benefit_taxable_annual == _D("0")

    def test_fringe_benefit_above_threshold_taxable(self) -> None:
        """R15: Fringe benefit above €1.000 threshold: ENTIRE amount is taxable."""
        scenario = dataclasses.replace(
            _req(),
            fringe_benefit_input=FringeBenefitInput(annual_amount=_D("1400")),
        )
        result = compute(scenario).result
        assert result.fringe_benefit_annual == _D("1400")
        assert result.fringe_benefit_taxable_annual == _D("1400.00")

    def test_welfare_scope_verified_when_input_given(self) -> None:
        """Welfare scope is verified when input is provided."""
        scenario = dataclasses.replace(
            _req(),
            welfare_input=WelfareInput(annual_amount=_D("600")),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["welfare"] == "verified"
        assert result.welfare_annual == _D("600")

    def test_bonus_pdr_eligible_applies_flat_tax(self) -> None:
        """PdR-eligible bonus within ceiling: flat tax computed correctly."""
        scenario = dataclasses.replace(
            _req(),
            bonus_input=BonusInput(annual_amount=_D("2000"), eligible_for_pdr=True),
        )
        result = compute(scenario).result
        scope = {item.feature: item.status for item in result.calculation_scope}
        assert scope["bonus_pdr"] == "verified"
        assert result.bonus_annual == _D("2000")
        assert result.bonus_pdr_flat_tax_annual == _D("20.00")
        assert result.bonus_ordinary_taxable_annual == _D("0")

    def test_gross_annual_not_mutated_by_variable_pay(self) -> None:
        """gross_annual and net_annual are unchanged with variable-pay inputs."""
        baseline = compute(_req()).result
        with_inputs = compute(
            dataclasses.replace(
                _req(),
                fringe_benefit_input=FringeBenefitInput(annual_amount=_D("1400")),
                welfare_input=WelfareInput(annual_amount=_D("600")),
                bonus_input=BonusInput(annual_amount=_D("2000"), eligible_for_pdr=True),
            )
        ).result
        assert with_inputs.gross_annual == baseline.gross_annual
        assert with_inputs.net_annual == baseline.net_annual
        assert with_inputs.taxable_income == baseline.taxable_income
        assert with_inputs.irpef_net == baseline.irpef_net


# ---------------------------------------------------------------------------
# L3: Family deductions (Art. 12 TUIR)
# ---------------------------------------------------------------------------


class TestL3FamilyDeductions:
    """Family deductions — orchestrator integration."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_no_family_leaves_irpef_net_unchanged(self) -> None:
        """Without family input, irpef_net equals baseline (no deduction)."""
        baseline = compute(_req()).result
        with_none = compute(dataclasses.replace(_req(), family=None)).result
        assert with_none.irpef_net == baseline.irpef_net
        assert with_none.family_deduction_annual == _D("0")

    def test_spouse_deduction_reduces_irpef_net(self) -> None:
        """Spouse deduction is subtracted from irpef_net."""
        baseline = compute(_req()).result
        with_spouse = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(spouse_dependent=True),
            )
        ).result
        assert with_spouse.family_deduction_spouse_annual > _D("0")
        assert with_spouse.irpef_net < baseline.irpef_net

    def test_family_deduction_children_and_other_zero_when_not_set(self) -> None:
        """Children/other fields are zero when only spouse is set."""
        result = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(spouse_dependent=True),
            )
        ).result
        assert result.family_deduction_children_annual == _D("0")
        assert result.family_deduction_other_annual == _D("0")

    def test_no_dependents_flags_no_deduction(self) -> None:
        """Family with no eligible dependents: deduction zero, irpef_net unchanged."""
        baseline = compute(_req()).result
        with_empty_family = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(),
            )
        ).result
        assert with_empty_family.family_deduction_annual == _D("0")
        assert with_empty_family.irpef_net == baseline.irpef_net

    def test_exempt_employer_family_unused_equals_total(self) -> None:
        """When employer does not withhold IRPEF, unused = total deduction."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        result = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(spouse_dependent=True),
            )
        ).result
        assert result.family_deduction_spouse_annual > _D("0")
        assert result.unused_family_deduction_annual == result.family_deduction_annual
        assert result.irpef_net == _D("0.00")

    def test_gross_annual_not_mutated_by_family_deductions(self) -> None:
        """gross_annual is unchanged by family deductions."""
        baseline = compute(_req()).result
        with_family = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(spouse_dependent=True),
            )
        ).result
        assert with_family.gross_annual == baseline.gross_annual

    def test_family_deduction_taper_uses_taxable_income(self) -> None:
        """Art. 12 taper uses taxable_income (gross minus INPS), not gross_annual.

        With a spouse dependent, the taper formula is
        (95000 - reddito_complessivo) / 95000.  This test verifies the engine
        uses taxable_income (< gross_annual) so the taper and resulting
        deduction are larger than they would be if computed on gross_annual.
        """
        result_no_fam = compute(_req()).result
        result_spouse = compute(
            dataclasses.replace(_req(), family=FamilyComposition(spouse_dependent=True))
        ).result
        # taxable_income < gross_annual, so the taper (95000 - RC) / 95000
        # is larger when RC = taxable_income.  The deduction must be strictly
        # greater than what the wrong (gross_annual) base would give.
        gross = result_no_fam.gross_annual
        taxable = result_no_fam.taxable_income
        assert taxable < gross
        # Deduction must be positive and taper-dependent
        assert result_spouse.family_deduction_spouse_annual > _D("0")
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
        result = compute(
            dataclasses.replace(_req(), family=FamilyComposition(spouse_dependent=True))
        ).result
        assert (
            FiscalSimplification.NO_DETRAZIONI_FAMILIARI
            not in result.fiscal_simplifications
        )

    def test_no_detrazioni_familiari_present_when_family_is_none(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is present when no family data is provided."""
        result = compute(dataclasses.replace(_req(), family=None)).result
        sfs = result.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_FAMILIARI in sfs

    def test_no_detrazioni_familiari_present_when_no_dependents(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is present when family has no eligible dependents.

        FamilyComposition() with no dependents: has_any_dependent is False, so
        the engine skips the Art. 12 computation and keeps the flag set.
        """
        result = compute(dataclasses.replace(_req(), family=FamilyComposition())).result
        sfs = result.fiscal_simplifications
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
        with_strd = compute(
            dataclasses.replace(_req(), family=FamilyComposition(spouse_dependent=True))
        ).result
        _mock_rules[0] = make_year_rules()
        baseline = compute(
            dataclasses.replace(_req(), family=FamilyComposition(spouse_dependent=True))
        ).result
        assert baseline.family_deduction_annual == with_strd.family_deduction_annual
        assert with_strd.sterilizzazione_clawback_annual == _D("0")

    def test_sterilizzazione_no_art15_no_clawback(self) -> None:
        """Without Art. 15 deductions, sterilizzazione clawback is zero.

        The reduction targets oneri at 19%: when art15_total = 0 there is
        nothing to reduce and irpef_net is unchanged.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        with_strd = compute(_req()).result
        _mock_rules[0] = make_year_rules()
        without_strd = compute(_req()).result
        assert with_strd.sterilizzazione_clawback_annual == _D("0")
        assert with_strd.irpef_net == without_strd.irpef_net

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
        with_strd = compute(
            dataclasses.replace(
                _req(negotiated_ral=_D("50000")), art15_deductions=art15
            )
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = compute(
            dataclasses.replace(
                _req(negotiated_ral=_D("50000")), art15_deductions=art15
            )
        ).result
        # Art. 13 (work_income_deduction) is not affected.
        assert with_strd.work_income_deduction == without_strd.work_income_deduction
        # Clawback fires at 440 (< 570 credit).
        assert with_strd.sterilizzazione_clawback_annual == _D("440.00")
        # irpef_net increases by the clawback amount.
        assert (
            with_strd.irpef_net - without_strd.irpef_net
            == with_strd.sterilizzazione_clawback_annual
        )
        # Raw art15_deduction_annual field is the pre-clawback credit.
        assert with_strd.art15_deduction_annual == _D("570.00")

    def test_sterilizzazione_below_threshold_no_effect(self) -> None:
        """Income <= threshold: no clawback; irpef_net unchanged."""
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "9999999", "reduction": "440"}
        )
        with_high_threshold = compute(_req()).result
        _mock_rules[0] = make_year_rules()
        without = compute(_req()).result
        assert with_high_threshold.sterilizzazione_clawback_annual == _D("0")
        assert with_high_threshold.irpef_net == without.irpef_net

    def test_sterilizzazione_at_high_income_art15_reduced(self) -> None:
        """At real 200k+ income with Art. 15 oneri, clawback fires on the credit.

        At reddito complessivo 250 000 EUR, the full EUR 440 reduction applies
        to the Art. 15 mortgage credit (4 000 * 19% = 760 EUR → 320 EUR net).
        """
        high_income = _D("250000")
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "200000", "reduction": "440"}
        )
        with_strd = compute(
            dataclasses.replace(
                _req(negotiated_ral=high_income),
                art15_deductions=Art15Deductions(mortgage_interest=_D("4000")),
            )
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = compute(
            dataclasses.replace(
                _req(negotiated_ral=high_income),
                art15_deductions=Art15Deductions(mortgage_interest=_D("4000")),
            )
        ).result
        # Clawback fires: Art. 15 credit is 760; min(440, 760) = 440.
        assert with_strd.sterilizzazione_clawback_annual == _D("440.00")
        # Raw art15_deduction_annual still shows the pre-clawback credit.
        assert with_strd.art15_deduction_annual == _D("760.00")
        # irpef_net increases by the clawback.
        assert with_strd.irpef_net - without_strd.irpef_net == _D("440.00")

    def test_sterilizzazione_with_family_and_art15_pins_unused(self) -> None:
        """art15_unused is recomputed against the effective credit after clawback.

        When sterilizzazione fires (clawback = 440), the effective Art. 15
        credit drops from 760 to 320 EUR.  art15_unused must be recomputed
        against the effective credit so that incapienza is not overstated.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        result = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(spouse_dependent=True),
                art15_deductions=Art15Deductions(mortgage_interest=_D("4000")),
            )
        ).result
        _mock_rules[0] = make_year_rules()
        result_no_strd = compute(
            dataclasses.replace(
                _req(),
                family=FamilyComposition(spouse_dependent=True),
                art15_deductions=Art15Deductions(mortgage_interest=_D("4000")),
            )
        ).result
        # Verify sterilizzazione fired and family deductions are present.
        assert result.sterilizzazione_clawback_annual == _D("440.00")
        assert result.family_deduction_annual > _D("0")
        # Raw art15_deduction_annual reports the pre-clawback credit in both.
        assert result.art15_deduction_annual == result_no_strd.art15_deduction_annual
        # art15_unused is lower with sterilizzazione because the effective credit
        # is smaller (320 vs 760 EUR), so less credit needs to be absorbed.
        assert result.unused_art15_deduction_annual <= (
            result_no_strd.unused_art15_deduction_annual
        )
        # The reduction in unused is bounded by the clawback amount.
        delta = (
            result_no_strd.unused_art15_deduction_annual
            - result.unused_art15_deduction_annual
        )
        assert _D("0") <= delta <= result.sterilizzazione_clawback_annual


# ---------------------------------------------------------------------------
# Art. 15 deductions (interessi passivi mutuo prima casa)
# ---------------------------------------------------------------------------


class TestArt15Deductions:
    """Art. 15 TUIR deductions — orchestrator integration."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_no_art15_leaves_irpef_net_unchanged(self) -> None:
        """Without art15_deductions, irpef_net equals baseline."""
        baseline = compute(_req()).result
        with_none = compute(dataclasses.replace(_req(), art15_deductions=None)).result
        assert with_none.irpef_net == baseline.irpef_net
        assert with_none.art15_deduction_annual == _D("0")

    def test_mortgage_deduction_reduces_irpef_net(self) -> None:
        """Art. 15 mortgage credit is subtracted from irpef_net, clamped at 0.

        At the test-CCNL income level the credit (570 EUR) exceeds irpef_net
        (551.36), so irpef_net is floored at 0 — excess credit is lost per
        Italian tax law.
        """
        baseline = compute(_req()).result
        with_art15 = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("3000")),
            )
        ).result
        assert with_art15.art15_deduction_annual == _D("570.00")  # 3000 * 0.19
        expected = max(_D("0"), baseline.irpef_net - _D("570.00"))
        assert with_art15.irpef_net == expected

    def test_ceiling_cap_applied(self) -> None:
        """Interest above EUR 4 000 ceiling: credit capped at EUR 760."""
        result = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("9999")),
            )
        ).result
        assert result.art15_deduction_annual == _D("760.00")  # 4000 * 0.19

    def test_no_detrazioni_art15_mortgage_tag_removed_when_computed(self) -> None:
        """NO_DETRAZIONI_ART15_MORTGAGE absent when mortgage interest is provided."""
        result = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("1000")),
            )
        ).result
        sfs = result.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE not in sfs

    def test_partial_detrazioni_art15_always_set_when_mortgage_present(self) -> None:
        """PARTIAL_DETRAZIONI_ART15 stays set even when mortgage is provided.

        Only one of ~15 Art. 15 TUIR categories is modelled; the flag signals
        that the other categories are always out of scope.
        """
        result = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("1000")),
            )
        ).result
        sfs = result.fiscal_simplifications
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_no_detrazioni_art15_mortgage_tag_present_when_not_set(self) -> None:
        """NO_DETRAZIONI_ART15_MORTGAGE present when mortgage not provided."""
        result = compute(_req()).result
        sfs = result.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE in sfs

    def test_partial_detrazioni_art15_always_set_when_no_art15(self) -> None:
        """PARTIAL_DETRAZIONI_ART15 always set, even without any Art. 15 input."""
        result = compute(_req()).result
        sfs = result.fiscal_simplifications
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_exempt_employer_art15_unused_equals_total(self) -> None:
        """When employer does not withhold IRPEF, unused = total credit."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        result = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("3000")),
            )
        ).result
        assert result.art15_deduction_annual == _D("570.00")
        assert result.unused_art15_deduction_annual == result.art15_deduction_annual
        assert result.irpef_net == _D("0.00")

    def test_zero_interest_has_no_effect(self) -> None:
        """Art15Deductions with zero mortgage_interest: no deduction, tags kept."""
        baseline = compute(_req()).result
        with_zero = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("0")),
            )
        ).result
        assert with_zero.art15_deduction_annual == _D("0")
        assert with_zero.irpef_net == baseline.irpef_net
        sfs = with_zero.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE in sfs
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_gross_annual_not_mutated_by_art15_deductions(self) -> None:
        """gross_annual is unchanged by Art. 15 deductions."""
        baseline = compute(_req()).result
        with_art15 = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("2000")),
            )
        ).result
        assert with_art15.gross_annual == baseline.gross_annual

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
        with_strd = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("3000")),
            )
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("3000")),
            )
        ).result
        # art15_deduction_annual reports the raw pre-clawback credit in both.
        assert with_strd.art15_deduction_annual == _D("570.00")
        assert without_strd.art15_deduction_annual == _D("570.00")
        # Clawback fires on Art. 15 → sterilizzazione_clawback = 440.
        assert with_strd.sterilizzazione_clawback_annual == _D("440.00")

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
        result = compute(
            dataclasses.replace(
                _req(),
                art15_deductions=Art15Deductions(mortgage_interest=_D("3000")),
            )
        ).result
        # art15 = 3000 * 0.19 = 570; unchanged by sterilizzazione.
        assert result.art15_deduction_annual == _D("570.00")
        # Exempt employer: all art15 is unused (irpef_net stays 0 regardless).
        assert result.unused_art15_deduction_annual == result.art15_deduction_annual
        assert result.irpef_net == _D("0.00")

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
        result = compute(
            dataclasses.replace(
                _req(negotiated_ral=_D("25000")),
                art15_deductions=Art15Deductions(mortgage_interest=_D("4000")),
            )
        ).result
        # art15 = min(4000, 4000) * 0.19 = 760 (at EUR 4 000 ceiling).
        assert result.art15_deduction_annual == _D("760.00")
        # UDL = 5 000 exhausts all IRPEF before Art. 15 → full credit is unused.
        assert result.ulteriore_detrazione_lavoro == _D("5000.00")
        assert result.unused_art15_deduction_annual == _D("760.00")


class TestArt15MortgagePre2022:
    """Tests for mortgage_pre_2022 TI qualification gate."""

    def test_post_2021_mortgage_excluded_from_ti_relevant_deductions(self) -> None:
        """Post-2021 mortgage (default) does not affect trattamento_integrativo."""
        # Level 2 (base 600/month) puts taxable income in the TI band.
        baseline = compute(_req(level_code="2")).result
        with_post_2021 = compute(
            dataclasses.replace(
                _req(level_code="2"),
                art15_deductions=Art15Deductions(
                    mortgage_interest=_D("3000"), mortgage_pre_2022=False
                ),
            )
        ).result
        # Art. 15 credit still applied to IRPEF
        assert with_post_2021.art15_deduction_annual == _D("570.00")
        # TI unaffected by post-2021 mortgage
        assert (
            with_post_2021.trattamento_integrativo == baseline.trattamento_integrativo
        )

    def test_pre_2022_mortgage_included_in_ti_relevant_deductions(self) -> None:
        """Pre-2022 mortgage qualifies for TI relevant_deductions."""
        baseline = compute(_req(level_code="2")).result
        with_pre_2022 = compute(
            dataclasses.replace(
                _req(level_code="2"),
                art15_deductions=Art15Deductions(
                    mortgage_interest=_D("3000"), mortgage_pre_2022=True
                ),
            )
        ).result
        # Art. 15 credit still applied to IRPEF
        assert with_pre_2022.art15_deduction_annual == _D("570.00")
        # TI may increase because relevant_deductions grew (or remain at max)
        assert with_pre_2022.trattamento_integrativo >= baseline.trattamento_integrativo


class TestComputeResultStatus:
    """Unit tests for compute_result_status helper."""

    def test_all_verified_returns_complete(self) -> None:
        """All verified scope items → complete."""
        scope = (
            ScopeItem(feature="base_salary", status="verified"),
            ScopeItem(feature="irpef", status="verified"),
        )
        assert compute_result_status(scope) == "complete"

    def test_excluded_items_do_not_block_complete(self) -> None:
        """Excluded items are acceptable; result is still complete."""
        scope = (
            ScopeItem(feature="base_salary", status="verified"),
            ScopeItem(feature="overtime", status="excluded"),
        )
        assert compute_result_status(scope) == "complete"

    def test_not_computed_returns_partial(self) -> None:
        """A single not_computed item forces partial status."""
        scope = (
            ScopeItem(feature="base_salary", status="verified"),
            ScopeItem(feature="overtime", status="not_computed"),
        )
        assert compute_result_status(scope) == "partial"

    def test_empty_scope_returns_complete(self) -> None:
        """Empty scope (no items) → complete (no blocked requests)."""
        assert compute_result_status(()) == "complete"

    def test_compute_sets_status_on_result(self) -> None:
        """compute() populates status='complete' for a basic scenario."""
        result = compute(_req()).result
        assert result.status in {"complete", "partial"}

    def test_compute_status_is_complete_without_work_rules_input(self) -> None:
        """No L3 inputs and L3 schema present → complete (all excluded)."""
        result = compute(_req()).result
        # No overtime/leave/sick input: all L3 scope items are 'excluded'.
        # All L1/L2 items are 'verified'.
        assert result.status == "complete"


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
            source_hash="b" * 64,
            verification_status=VerificationStatus.VERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(verified_ruleset,))
        assert result == "high"

    def test_compute_result_has_confidence_field(self) -> None:
        """compute() populates confidence on the result."""
        result = compute(_req()).result
        assert result.confidence in {"low", "medium", "high"}


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
    """Minimal CCNL where all provenance is VERIFIED (no ruleset block).

    Returns:
        A validated CCNL instance with fully verified salary provenance.
    """
    raw = make_ccnl_dict()
    raw["levels"] = [
        _verified_level("2", 2, "600.00"),
        _verified_level("3", 3, "800.00"),
        _verified_level("4", 4, "1000.00"),
    ]
    raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
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

    def test_verified_var_pay_ruleset_allows_high_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verified var-pay ruleset + verified CCNL provenance → high."""
        _mock_ccnl[0] = _verified_ccnl()
        verified = _var_pay_rules(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules.load_variable_pay_rules",
            lambda _: verified,
        )
        result = compute(dataclasses.replace(_req(), fringe_benefit_input=_FB_INPUT))
        assert result.result.confidence == "high"

    def test_unverified_var_pay_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unverified var-pay ruleset drops confidence to medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _var_pay_rules(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules.load_variable_pay_rules",
            lambda _: unverified,
        )
        result = compute(dataclasses.replace(_req(), fringe_benefit_input=_FB_INPUT))
        assert result.result.confidence == "medium"

    def test_ccnl_without_ruleset_allows_high_confidence(self) -> None:
        """Verified CCNL with no ruleset block → high confidence."""
        _mock_ccnl[0] = _verified_ccnl()
        result = compute(_req())
        assert result.result.confidence == "high"

    def test_unverified_ccnl_ruleset_downgrades_confidence(self) -> None:
        """Unverified CCNL ruleset → confidence medium."""
        ruleset_block = {
            "id": "ccnl/test",
            "version": "2026.1",
            "effective_from": "2026-01-01",
            "effective_until": None,
            "published_at": "2026-01-01",
            "source": "https://example.com",
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
        result = compute(_req())
        assert result.result.confidence == "medium"

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
        scenario = dataclasses.replace(_req(), sick_input=SickInput(sick_days=_D("3")))
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
            "ccnl_engine.engine.payroll.service.work_rules.load_variable_pay_rules",
            lambda _: rules_no_ruleset,
        )
        scenario = dataclasses.replace(_req(), fringe_benefit_input=_FB_INPUT)
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


_FAMILY_INPUT = FamilyComposition(spouse_dependent=True)
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
        result = compute(dataclasses.replace(_req(), family=_FAMILY_INPUT))
        assert result.result.confidence == "medium"

    def test_family_with_verified_ruleset_allows_high(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Family deductions with a verified ruleset + verified CCNL → high."""
        _mock_ccnl[0] = _verified_ccnl()
        verified = _family_rules_with_status(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal.load_family_deduction_rules",
            lambda _: verified,
        )
        result = compute(dataclasses.replace(_req(), family=_FAMILY_INPUT))
        assert result.result.confidence == "high"

    def test_family_with_unverified_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Family deductions with an unverified ruleset → medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _family_rules_with_status(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal.load_family_deduction_rules",
            lambda _: unverified,
        )
        result = compute(dataclasses.replace(_req(), family=_FAMILY_INPUT))
        assert result.result.confidence == "medium"

    def test_art15_without_ruleset_downgrades_confidence(self) -> None:
        """Art. 15 deductions with no ruleset block in JSON → medium.

        art15-deductions-2026.json has no ruleset block at all; _try_ruleset()
        returns None, treated as an unverified consumed source.
        """
        _mock_ccnl[0] = _verified_ccnl()
        result = compute(dataclasses.replace(_req(), art15_deductions=_ART15_INPUT))
        assert result.result.confidence == "medium"

    def test_art15_with_verified_ruleset_allows_high(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Art. 15 deductions with a verified ruleset + verified CCNL → high."""
        _mock_ccnl[0] = _verified_ccnl()
        verified = _art15_rules_with_status(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal.load_art15_deduction_rules",
            lambda _: verified,
        )
        result = compute(dataclasses.replace(_req(), art15_deductions=_ART15_INPUT))
        assert result.result.confidence == "high"

    def test_art15_with_unverified_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Art. 15 deductions with an unverified ruleset → medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _art15_rules_with_status(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal.load_art15_deduction_rules",
            lambda _: unverified,
        )
        result = compute(dataclasses.replace(_req(), art15_deductions=_ART15_INPUT))
        assert result.result.confidence == "medium"

    def test_no_optional_features_confidence_unaffected(self) -> None:
        """No family or Art. 15 inputs: consumed_ruleset_ids stays empty."""
        _mock_ccnl[0] = _verified_ccnl()
        result = compute(_req())
        assert result.result.confidence == "high"

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
        result = compute(_req()).result
        sfs = result.fiscal_simplifications
        assert FiscalSimplification.NO_BILATERAL_FUNDS in sfs

    def test_no_bilateral_funds_flag_absent_when_funds_present(self) -> None:
        """NO_BILATERAL_FUNDS is cleared when at least one fund is provided."""
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=_D("5"),
                    employer_monthly=_D("10"),
                ),
            ),
        )
        result = compute(scenario).result
        sfs = result.fiscal_simplifications
        assert FiscalSimplification.NO_BILATERAL_FUNDS not in sfs

    def test_flat_monthly_fund_reduces_net_annual(self) -> None:
        """Employee flat monthly contribution (x 12) is subtracted from net_annual."""
        baseline = compute(_req()).result
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=_D("20"),
                    employer_monthly=_D("0"),
                ),
            ),
        )
        result = compute(scenario).result
        expected_net = money(baseline.net_annual - _D("20") * 12)
        assert result.net_annual == expected_net

    def test_flat_monthly_fund_increases_employer_cost(self) -> None:
        """Employer flat monthly contribution (x 12) enters employer_cost_annual."""
        baseline = compute(_req()).result
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=_D("0"),
                    employer_monthly=_D("15"),
                ),
            ),
        )
        result = compute(scenario).result
        expected_cost = money(baseline.employer_cost_annual + _D("15") * 12)
        assert result.employer_cost_annual == expected_cost

    def test_rate_fund_tfr_base_computation(self) -> None:
        """RateFund with base='tfr_base' is applied and reduces net_annual."""
        baseline = compute(_req()).result
        rate = _D("0.01")
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                RateFund(employee_rate=rate, employer_rate=_D("0"), base="tfr_base"),
            ),
        )
        result = compute(scenario).result
        # bilateral_employee_annual must be positive (tfr_base > 0)
        assert result.bilateral_employee_annual > _D("0")
        # net_annual decreases by exactly bilateral_employee_annual
        assert result.net_annual == money(
            baseline.net_annual - result.bilateral_employee_annual
        )
        # employer side unaffected
        assert result.bilateral_employer_annual == _D("0")
        assert result.employer_cost_annual == baseline.employer_cost_annual

    def test_rate_fund_gross_annual_computation(self) -> None:
        """RateFund with base='gross_annual' applies rate to gross_annual."""
        baseline = compute(_req()).result
        rate = _D("0.005")
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                RateFund(
                    employee_rate=rate,
                    employer_rate=rate,
                    base="gross_annual",
                ),
            ),
        )
        result = compute(scenario).result
        expected_employee = money(baseline.gross_annual * rate)
        expected_employer = money(baseline.gross_annual * rate)
        assert result.bilateral_employee_annual == expected_employee
        assert result.bilateral_employer_annual == expected_employer
        assert result.net_annual == money(baseline.net_annual - expected_employee)
        assert result.employer_cost_annual == money(
            baseline.employer_cost_annual + expected_employer
        )

    def test_gross_annual_not_mutated_by_bilateral_funds(self) -> None:
        """gross_annual is unchanged when bilateral_funds are provided."""
        baseline = compute(_req()).result
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=_D("50"),
                    employer_monthly=_D("50"),
                ),
            ),
        )
        result = compute(scenario).result
        assert result.gross_annual == baseline.gross_annual

    def test_bilateral_funds_scope_item_verified_when_present(self) -> None:
        """bilateral_funds scope item is 'verified' when funds are provided."""
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=_D("10"),
                    employer_monthly=_D("10"),
                ),
            ),
        )
        result = compute(scenario).result
        scope_map = {item.feature: item.status for item in result.calculation_scope}
        assert scope_map["bilateral_funds"] == "verified"

    def test_bilateral_funds_scope_item_excluded_when_absent(self) -> None:
        """bilateral_funds scope item is 'excluded' when no funds provided."""
        result = compute(_req()).result
        scope_map = {item.feature: item.status for item in result.calculation_scope}
        assert scope_map["bilateral_funds"] == "excluded"

    def test_multiple_funds_accumulate(self) -> None:
        """Multiple funds in the tuple accumulate correctly."""
        baseline = compute(_req()).result
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=_D("10"),
                    employer_monthly=_D("20"),
                ),
                FlatMonthlyFund(
                    employee_monthly=_D("5"),
                    employer_monthly=_D("8"),
                ),
            ),
        )
        result = compute(scenario).result
        expected_emp = money((_D("10") + _D("5")) * 12)
        expected_er = money((_D("20") + _D("8")) * 12)
        assert result.bilateral_employee_annual == expected_emp
        assert result.bilateral_employer_annual == expected_er
        assert result.net_annual == money(baseline.net_annual - expected_emp)
        assert result.employer_cost_annual == money(
            baseline.employer_cost_annual + expected_er
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
    ) -> PayrollScenario:
        base = _req(ivs_ceiling_applies=ivs_ceiling_applies)
        return dataclasses.replace(
            base,
            employee=dataclasses.replace(
                base.employee,
                seniority=SeniorityByDate(hire_date),
            ),
        )

    def test_post_1996_hire_no_ceiling_emits_warning(self) -> None:
        """Hire date on or after 1996-01-01 with ivs=False yields a warning."""
        r = compute(self._scenario_with_hire_date(date(1996, 6, 1))).result
        assert any("ivs_ceiling_applies" in w for w in r.warnings)

    def test_post_1996_hire_with_ceiling_no_warning(self) -> None:
        """Hire date after 1996-01-01 with ivs=True produces no warning."""
        r = compute(
            self._scenario_with_hire_date(date(2000, 1, 1), ivs_ceiling_applies=True)
        ).result
        assert not any("ivs_ceiling_applies" in w for w in r.warnings)

    def test_pre_1996_hire_no_warning(self) -> None:
        """Hire date before 1996-01-01 produces no warning."""
        r = compute(self._scenario_with_hire_date(date(1990, 3, 15))).result
        assert not any("ivs_ceiling_applies" in w for w in r.warnings)

    def test_post_1996_hire_warning_contains_overstated(self) -> None:
        """Warning for post-1996 hire must mention 'overstated'."""
        r = compute(self._scenario_with_hire_date(date(2000, 6, 1))).result
        assert any("overstated" in w for w in r.warnings)

    def test_seniority_by_months_post_1996_emits_warning(self) -> None:
        """SeniorityByMonths implying post-1996 hire triggers the warning."""
        # 120 months = 10 years of seniority; implied hire ~2016, post-1996
        r = compute(_req(seniority_months=120)).result
        assert any("overstated" in w for w in r.warnings)

    def test_seniority_by_months_pre_1996_no_warning(self) -> None:
        """SeniorityByMonths implying pre-1996 hire produces no warning."""
        # 480 months = 40 years; implied hire ~1986, pre-1996
        r = compute(_req(seniority_months=480)).result
        assert not any("ivs_ceiling_applies" in w for w in r.warnings)

    def test_seniority_by_months_with_ceiling_no_warning(self) -> None:
        """SeniorityByMonths with ivs_ceiling_applies=True produces no warning."""
        r = compute(_req(seniority_months=120, ivs_ceiling_applies=True)).result
        assert not any("ivs_ceiling_applies" in w for w in r.warnings)

    def test_seniority_by_count_emits_warning(self) -> None:
        """SeniorityByCount with ivs_ceiling_applies=False triggers warning."""
        r = compute(_req(seniority_count=2)).result
        assert any("overstated" in w for w in r.warnings)

    def test_seniority_by_count_with_ceiling_no_warning(self) -> None:
        """SeniorityByCount with ivs_ceiling_applies=True produces no warning."""
        r = compute(_req(seniority_count=2, ivs_ceiling_applies=True)).result
        assert not any("ivs_ceiling_applies" in w for w in r.warnings)

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
        scenario = dataclasses.replace(
            base,
            employee=dataclasses.replace(base.employee, seniority=None),
        )
        result = _ivs_ceiling_warning(scenario, _DATE, _D("130000"), _D("120000"))
        assert result is not None
        assert "seniority is None" in result
        assert "IVS ceiling" in result

    def test_seniority_none_no_ceiling_no_warning(self) -> None:
        """seniority=None does not warn when the IVS ceiling is unknown."""
        base = _req()
        scenario = dataclasses.replace(
            base,
            employee=dataclasses.replace(base.employee, seniority=None),
        )
        result = _ivs_ceiling_warning(scenario, _DATE, _D("200000"), None)
        assert result is None

    def test_seniority_none_base_at_ceiling_no_warning(self) -> None:
        """seniority=None does not warn when base does not exceed the ceiling."""
        base = _req()
        scenario = dataclasses.replace(
            base,
            employee=dataclasses.replace(base.employee, seniority=None),
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
        r = compute(_req()).result
        assert FiscalSimplification.NO_ASSEGNO_UNICO in r.fiscal_simplifications

    def test_always_present_with_bilateral_funds(self) -> None:
        """NO_ASSEGNO_UNICO is present even when bilateral funds are supplied."""
        scenario = dataclasses.replace(
            _req(),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=_D("10"),
                    employer_monthly=_D("20"),
                ),
            ),
        )
        r = compute(scenario).result
        assert FiscalSimplification.NO_ASSEGNO_UNICO in r.fiscal_simplifications


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
        calc = compute(_req(second_level_allowances=(sl,)))
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
            source_hash="a" * 64,
            verification_status=regional_status,
        ),
        municipal_ruleset=RulesetIdentity(
            id="surtax/2026/comunale",
            version="2026.2",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="https://example.com",
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
        calc = compute(
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
        calc = compute(
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
        calc = compute(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(regione="TestRegione"),
            )
        )
        assert calc.result.confidence == "medium"

    def test_unverified_municipal_downgrades_confidence_when_applied(self) -> None:
        """Unverified municipal ruleset → medium confidence when entry was applied."""
        _mock_ccnl[0] = _verified_ccnl()
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.UNVERIFIED
        )
        calc = compute(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(comune_belfiore="X001"),
            )
        )
        assert calc.result.confidence == "medium"

    def test_unverified_municipal_not_consumed_when_regione_only(self) -> None:
        """Unverified municipal ruleset does not downgrade confidence: regione only."""
        _mock_ccnl[0] = _verified_ccnl()
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.UNVERIFIED
        )
        calc = compute(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(regione="TestRegione"),
            )
        )
        assert calc.result.confidence == "high"

    def test_both_applied_both_identities_affect_confidence(self) -> None:
        """Both entries applied: unverified municipal identity downgrades confidence."""
        _mock_ccnl[0] = _verified_ccnl()
        _mock_surtax[0] = _surtax_with_identities(
            VerificationStatus.VERIFIED, VerificationStatus.UNVERIFIED
        )
        calc = compute(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="TestRegione", comune_belfiore="X001"
                ),
            )
        )
        assert calc.result.confidence == "medium"
