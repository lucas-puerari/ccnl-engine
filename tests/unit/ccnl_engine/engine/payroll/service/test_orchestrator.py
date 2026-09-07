"""Tests for engine/compute/orchestrator — compute() and helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    Allowance,
    SupplementaryAllowance,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.metadata.domain.rules import VerificationStatus
from ccnl_engine.engine.payroll.domain.employee import (
    ContractPosition,
    DestinationRalOverride,
    Employee,
    RalOverride,
    SalaryOverrides,
    SeniorityByCount,
    SeniorityByMonths,
    TaxProfile,
    WorkArrangement,
)
from ccnl_engine.engine.payroll.domain.employer import Employer
from ccnl_engine.engine.payroll.domain.employment import Employment, Permanent
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.service.orchestrator import _collect_provenance, compute
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.types import MonthlyPayChain
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import (
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
from tests.helpers import make_ccnl_dict, make_domestic_year_rules, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _FIXED_TERM,
    _PERMANENT,
    _RULES,
    _allowance,
    _build_ccnl,
    _req,
    _series,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
    from ccnl_engine.engine.tax.domain.rules import YearRules

_DEFAULT_CCNL = _build_ccnl()
_DEFAULT_CCNL_UC = _build_ccnl("under_classification")


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
# Input model validation (employee.py)
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
        """WorkArrangement with part_time_pct outside (0, 1] must raise."""
        with pytest.raises(ValueError, match="part_time_pct"):
            WorkArrangement(part_time_pct=Decimal(0))

    @pytest.mark.parametrize("pct", ["-0.1", "1.01"])
    def test_part_time_pct_boundary(self, pct: str) -> None:
        """part_time_pct outside (0, 1] must raise at any invalid value."""
        with pytest.raises(ValueError, match="part_time_pct"):
            WorkArrangement(part_time_pct=_D(pct))

    def test_weekly_hours_zero_raises(self) -> None:
        """WorkArrangement with weekly_hours <= 0 must raise at construction."""
        with pytest.raises(ValueError, match="weekly_hours"):
            WorkArrangement(weekly_hours=Decimal(0))

    def test_ad_personam_negative_raises(self) -> None:
        """SalaryOverrides with ad_personam_monthly < 0 must raise."""
        with pytest.raises(ValueError, match="ad_personam_monthly"):
            SalaryOverrides(ad_personam_monthly=_D(-1))

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
            compute(_DEFAULT_CCNL, _RULES, _req(level_code="NOPE"))

    def test_seniority_count_above_maximum_raises(self) -> None:
        """SeniorityByCount above the level maximum must raise ValueError."""
        with pytest.raises(ValueError, match="exceeds the maximum of 10"):
            compute(_DEFAULT_CCNL, _RULES, _req(seniority_count=11))

    def test_second_level_with_ral_override_raises(self) -> None:
        """second_level_allowances cannot be combined with a RAL override."""
        sl = SupplementaryAllowance(code="X", description="X", monthly=_D("100"))
        with pytest.raises(ValueError, match="RAL override"):
            compute(
                _DEFAULT_CCNL,
                _RULES,
                _req(negotiated_ral=_D("20000")),
                employer=Employer(second_level_allowances=(sl,)),
            )

    def test_negotiated_destination_ral_on_non_apprentice_raises(self) -> None:
        """DestinationRalOverride with a non-Apprentice employment raises."""
        with pytest.raises(ValueError, match="only valid for Apprentice"):
            compute(
                _DEFAULT_CCNL,
                _RULES,
                _req(negotiated_destination_ral=_D("20000.00")),
            )


# ---------------------------------------------------------------------------
# Permanent employment
# ---------------------------------------------------------------------------


class TestComputePermanent:
    """Permanent contract paths in compute()."""

    def test_full_time_no_seniority(self) -> None:
        """Permanent, full-time, no seniority: standard salary chain."""
        r = compute(_DEFAULT_CCNL, _RULES, _req())

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
        r = compute(_DEFAULT_CCNL, _RULES, _req(seniority_count=2))

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
        r = compute(_DEFAULT_CCNL, _RULES, _req(seniority_months=months))
        assert r.seniority_count == expected

    @pytest.mark.parametrize(
        ("months", "expected"), [(47, 0), (48, 1), (83, 1), (84, 2), (120, 3)]
    )
    def test_seniority_first_cadence(self, months: int, expected: int) -> None:
        """First increment after first_cadence_months, then every cadence_months."""
        ccnl = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months": 48
        })
        r = compute(ccnl, _RULES, _req(seniority_months=months))
        assert r.seniority_count == expected

    def test_seniority_first_cadence_by_level(self) -> None:
        """Per-level first cadence (e.g. operai lump step at 48 months)."""
        ccnl = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months_by_level": {"4": 48}
        })
        r47 = compute(ccnl, _RULES, _req(seniority_months=47))
        r48 = compute(ccnl, _RULES, _req(seniority_months=48))
        assert r47.seniority_count == 0
        assert r48.seniority_count == 1
        assert (
            compute(
                ccnl, _RULES, _req(level_code="3", seniority_months=36)
            ).seniority_count
            == 1
        )

    def test_seniority_per_level_maximum(self) -> None:
        """maximum_count_by_level overrides maximum_count for that level."""
        ccnl = _build_ccnl(**{
            "parameters.seniority_increments.maximum_count_by_level": {"4": 1}
        })
        r = compute(ccnl, _RULES, _req(seniority_months=360))
        assert r.seniority_count == 1
        assert r.seniority_monthly == _D("20.00")
        with pytest.raises(ValueError, match="exceeds the maximum of 1"):
            compute(ccnl, _RULES, _req(seniority_count=2))

    def test_part_time_scales_all_components(self) -> None:
        """part_time_pct=0.5 halves every component; components sum to gross."""
        ccnl = _build_ccnl(**{
            "levels.2.fixed_allowances": [_allowance("edr", "10.33")]
        })
        r = compute(
            ccnl,
            _RULES,
            _req(part_time_pct=_D("0.50"), seniority_count=1),
        )

        assert r.base_monthly == _D("500.00")
        assert r.seniority_monthly == _D("10.00")
        assert r.allowances_monthly == _D("5.17")
        assert r.gross_monthly == _D("515.17")
        assert r.gross_annual == _D("6182.04")

    def test_negotiated_ral(self) -> None:
        """RalOverride overrides gross_annual; gross_monthly stays consistent."""
        ral = _D("20000.00")
        r = compute(_DEFAULT_CCNL, _RULES, _req(negotiated_ral=ral))

        assert r.gross_annual == ral
        assert r.gross_monthly == _D("1666.67")

    def test_level_without_seniority_entry(self) -> None:
        """Level '3' has no seniority in amount_by_level — seniority stays zero."""
        r = compute(_DEFAULT_CCNL, _RULES, _req(level_code="3", seniority_count=5))

        assert r.seniority_monthly == _D("0.00")
        assert r.base_monthly == _D("800.00")
        assert r.gross_annual == _D("9600.00")

    def test_ad_personam_added_unscaled(self) -> None:
        """ad_personam_monthly is added as given, even under part-time."""
        r = compute(
            _DEFAULT_CCNL,
            _RULES,
            _req(part_time_pct=_D("0.50"), ad_personam_monthly=_D("30.00")),
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
        ccnl = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance("edr", "10.00"),
                _allowance("quadro", "100.00", role="quadro"),
            ]
        })
        plain = compute(ccnl, _RULES, _req())
        quadro = compute(ccnl, _RULES, _req(roles=frozenset({"quadro"})))
        assert plain.allowances_monthly == _D("10.00")
        assert quadro.allowances_monthly == _D("110.00")

    def test_months_per_year(self) -> None:
        """An allowance paid 12 times contributes 12 x monthly to gross_annual."""
        ccnl = _build_ccnl(**{
            "parameters.additional_months": _series("14"),
            "levels.2.fixed_allowances": [
                _allowance("ind", "50.00", months_per_year=12)
            ],
        })
        r = compute(ccnl, _RULES, _req())
        assert r.gross_monthly == _D("1050.00")
        assert r.gross_annual == _D("14600.00")  # 1000*14 + 50*12

    def test_relevance_flags(self) -> None:
        """Non-relevant allowances are excluded from the INPS and TFR bases."""
        ccnl = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance(
                    "edr",
                    "100.00",
                    tfr_relevant=False,
                    contribution_relevant=False,
                )
            ]
        })
        r = compute(ccnl, _RULES, _req())
        base = compute(_DEFAULT_CCNL, _RULES, _req())
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
        ccnl = _build_ccnl(**{
            "levels.2.fixed_allowances": [
                _allowance(
                    "edr", "100.00", contribution_relevant=False, tfr_relevant=False
                )
            ]
        })
        ral = _D("12000.00")
        r_with_exclusion = compute(ccnl, _RULES, _req(negotiated_ral=ral))
        r_clean = compute(_DEFAULT_CCNL, _RULES, _req(negotiated_ral=ral))

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
        ccnl = _build_ccnl(**{
            "parameters.employer_funds": [self._FUND],
            "levels.2.category": "operaio",
            "levels.1.category": "impiegato",
        })
        operaio = compute(ccnl, _RULES, _req())
        impiegato = compute(ccnl, _RULES, _req(level_code="3"))
        uncategorised = compute(ccnl, _RULES, _req(level_code="2"))
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
        ccnl = _build_ccnl(**{"parameters.employer_funds": [fund]})
        r = compute(ccnl, _RULES, _req(level_code="3"))
        assert r.employer_funds_annual == _D("960.00")

    def test_employer_rate_by_category(self) -> None:
        """Employer rate override applies to matching categories only."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.30",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
                "employer_rate_by_category": {"impiegato": "0.20"},
            }
        )
        ccnl = _build_ccnl(**{
            "levels.1.category": "impiegato",
            "levels.2.category": "operaio",
        })
        impiegato = compute(ccnl, rules, _req(level_code="3"))
        operaio = compute(ccnl, rules, _req())
        assert impiegato.inps_employer_annual == _D("1920.00")  # 9600 * 0.20
        assert operaio.inps_employer_annual == _D("3600.00")  # 12000 * 0.30


# ---------------------------------------------------------------------------
# Fixed-term employment
# ---------------------------------------------------------------------------


class TestComputeFixedTerm:
    """Fixed-term contract adds NASpI addizionale to employer INPS."""

    def test_fixed_term_naspi_addizionale(self) -> None:
        """Employer INPS for fixed-term must exceed permanent by 1.4% of gross."""
        r_fixed = compute(_DEFAULT_CCNL, _RULES, _req(employment=_FIXED_TERM))
        r_perm = compute(_DEFAULT_CCNL, _RULES, _req())

        expected_diff = r_fixed.gross_annual * _D("0.014")
        actual_diff = r_fixed.inps_employer_annual - r_perm.inps_employer_annual
        assert abs(actual_diff - expected_diff) <= _D("0.01")
        assert r_fixed.employment_type == "fixed_term"


# ---------------------------------------------------------------------------
# IVS ceiling split — end-to-end
# ---------------------------------------------------------------------------


class TestComputeIvsCeilingSplit:
    """compute() with TaxProfile.ivs_ceiling_applies=True and RAL above massimale."""

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

    def _employee(self, ral: Decimal, *, ivs_ceiling_applies: bool) -> Employee:
        return Employee(
            position=ContractPosition(
                level_code="4", as_of=_DATE, employment=_PERMANENT
            ),
            arrangement=WorkArrangement(),
            tax=TaxProfile(ivs_ceiling_applies=ivs_ceiling_applies),
            agreement=SalaryOverrides(ral_override=RalOverride(ral)),
        )

    def test_below_ceiling_unchanged(self) -> None:
        """RAL below the massimale: ceiling split equals flat rate."""
        ral = _D("80000.00")
        rules = self._rules_with_ceiling()
        r_capped = compute(
            _DEFAULT_CCNL, rules, self._employee(ral, ivs_ceiling_applies=True)
        )
        r_flat = compute(
            _DEFAULT_CCNL, rules, self._employee(ral, ivs_ceiling_applies=False)
        )
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

        r = compute(
            _DEFAULT_CCNL,
            self._rules_with_ceiling(),
            self._employee(ral, ivs_ceiling_applies=True),
        )
        assert r.inps_employee_annual == expected_employee
        assert r.inps_employer_annual == expected_employer

    def test_ceiling_flag_false_skips_split(self) -> None:
        """ivs_ceiling_applies=False: flat rate even when ceiling is configured."""
        ral = _D("150000.00")
        r = compute(
            _DEFAULT_CCNL,
            self._rules_with_ceiling(),
            self._employee(ral, ivs_ceiling_applies=False),
        )
        assert r.inps_employee_annual == _D("150000.00") * _D("0.0919")
        assert r.inps_employer_annual == _D("150000.00") * _D("0.2898")


# ---------------------------------------------------------------------------
# IRPEF floor
# ---------------------------------------------------------------------------


class TestComputeIrpefFloor:
    """Net = gross - inps when deduction exceeds gross IRPEF."""

    def test_irpef_net_floored_at_zero(self) -> None:
        """Low income: deduction > irpef_gross → irpef_net == 0."""
        r = compute(_DEFAULT_CCNL, _RULES, _req(negotiated_ral=_D("5000.00")))

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
        r = compute(self._EXEMPT_CCNL, _RULES, _req())

        assert r.irpef_net == _D("0.00")

    def test_employer_withholds_irpef_flag_false(self) -> None:
        """Exempt employer: employer_withholds_irpef must be False."""
        r = compute(self._EXEMPT_CCNL, _RULES, _req())

        assert r.employer_withholds_irpef is False

    def test_net_annual_excludes_irpef(self) -> None:
        """Net = gross - INPS employee; IRPEF not deducted by employer."""
        r = compute(self._EXEMPT_CCNL, _RULES, _req())

        assert r.net_annual == r.gross_annual - r.inps_employee_annual

    def test_irpef_informational_fields_nonzero(self) -> None:
        """irpef_gross and work_income_deduction remain as informational."""
        r = compute(self._EXEMPT_CCNL, _RULES, _req())

        assert r.irpef_gross > _D("0.00")
        assert r.work_income_deduction >= _D("0.00")

    def test_standard_ccnl_withholds_irpef(self) -> None:
        """Standard CCNL: employer_withholds_irpef must be True."""
        r = compute(_DEFAULT_CCNL, _RULES, _req())

        assert r.employer_withholds_irpef is True


# ---------------------------------------------------------------------------
# Domestic flat-hour INPS model
# ---------------------------------------------------------------------------


_DOMESTIC_RULES = make_domestic_year_rules()
_DOMESTIC_CCNL = _build_ccnl()
_DEFAULT_WEEKLY_HOURS: Decimal = _D("40")


def _req_domestic(
    weekly_hours: Decimal | None = _DEFAULT_WEEKLY_HOURS,
    employment: Employment = _PERMANENT,
) -> Employee:
    """Build an Employee for the domestic INPS path.

    Returns:
        An Employee with weekly_hours set (required for domestic model).
    """
    return Employee(
        position=ContractPosition(
            level_code="4",
            as_of=_DATE,
            employment=employment,
        ),
        arrangement=WorkArrangement(weekly_hours=weekly_hours),
    )


class TestComputeDomesticInps:
    """Flat per-hour INPS model (rules.domestic_contributions is not None)."""

    def test_missing_weekly_hours_raises(self) -> None:
        """domestic_contributions set but weekly_hours=None must raise."""
        with pytest.raises(ValueError, match="weekly_hours is required"):
            compute(_DOMESTIC_CCNL, _DOMESTIC_RULES, _req_domestic(weekly_hours=None))

    def test_hours_bracket_permanent(self) -> None:
        """weekly_hours > 24 → hours bracket; permanent uses base employer rate."""
        r = compute(
            _DOMESTIC_CCNL, _DOMESTIC_RULES, _req_domestic(weekly_hours=_D("40"))
        )

        annual_hours = _D("40") * _D("52")
        assert r.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.inps_employer_annual == money(_D("0.93") * annual_hours)

    def test_hours_bracket_fixed_term(self) -> None:
        """weekly_hours > 24 + FixedTerm → hours bracket fixed-term rate."""
        r = compute(
            _DOMESTIC_CCNL, _DOMESTIC_RULES, _req_domestic(employment=_FIXED_TERM)
        )

        annual_hours = _D("40") * _D("52")
        assert r.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.inps_employer_annual == money(_D("1.01") * annual_hours)

    def test_wage_bracket_low(self) -> None:
        """weekly_hours <= 24 + low hourly rate → lowest wage bracket."""
        # Hourly rate for level 4 (1000/168 ≈ 5.95) → below 9.61 bracket
        r = compute(
            _DOMESTIC_CCNL, _DOMESTIC_RULES, _req_domestic(weekly_hours=_D("20"))
        )

        annual_hours = _D("20") * _D("52")
        assert r.inps_employee_annual == money(_D("0.43") * annual_hours)
        assert r.inps_employer_annual == money(_D("1.27") * annual_hours)

    def test_net_is_gross_minus_inps_minus_irpef(self) -> None:
        """Net = gross - INPS employee - irpef_net for domestic path."""
        r = compute(_DOMESTIC_CCNL, _DOMESTIC_RULES, _req_domestic())

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
                    brackets=[SurtaxBracket(up_to=None, rate=Decimal("0.0123"))]
                )
            },
            comunale={
                "X001": ComunaleEntry(
                    nome="Test",
                    brackets=[SurtaxBracket(up_to=None, rate=Decimal("0.008"))],
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
        ccnl = CCNL.model_validate(make_ccnl_dict())
        rules = make_year_rules()
        tax = (
            TaxProfile(regione=regione, comune_belfiore=comune_belfiore)
            if regione is not None or comune_belfiore is not None
            else None
        )
        agreement = (
            SalaryOverrides(ral_override=RalOverride(negotiated_ral))
            if negotiated_ral is not None
            else None
        )
        return compute(
            ccnl,
            rules,
            Employee(
                position=ContractPosition(
                    level_code="4",
                    as_of=date(2026, 1, 1),
                    employment=Permanent(),
                ),
                arrangement=WorkArrangement(),
                tax=tax,
                agreement=agreement,
            ),
            surtax=self._surtax_rules(),
        ).result

    def test_without_surtax_parameter_both_zero(self) -> None:
        """When surtax=None (default), both addizionali are zero."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        rules = make_year_rules()
        r = compute(
            ccnl,
            rules,
            Employee(
                position=ContractPosition(
                    level_code="4",
                    as_of=date(2026, 1, 1),
                    employment=Permanent(),
                ),
                arrangement=WorkArrangement(),
            ),
        )
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
        """Unknown belfiore code → addizionale comunale zero, no flag."""
        r = self._result(comune_belfiore="Z999")
        assert r.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.fiscal_simplifications

    def test_soglia_exempts_low_income(self) -> None:
        """Income below the soglia yields zero comunal surtax."""
        tiny_ral = Decimal(9000)  # well below X001's soglia of 10000

        ccnl = CCNL.model_validate(make_ccnl_dict())
        rules = make_year_rules()
        surtax = SurtaxRules(
            year=2026,
            regionale={},
            comunale={
                "X001": ComunaleEntry(
                    nome="Test",
                    brackets=[SurtaxBracket(up_to=None, rate=Decimal("0.008"))],
                    exemption_threshold=Decimal(10000),
                )
            },
        )
        r = compute(
            ccnl,
            rules,
            Employee(
                position=ContractPosition(
                    level_code="4",
                    as_of=date(2026, 1, 1),
                    employment=Permanent(),
                ),
                arrangement=WorkArrangement(),
                tax=TaxProfile(comune_belfiore="X001"),
                agreement=SalaryOverrides(ral_override=RalOverride(tiny_ral)),
            ),
            surtax=surtax,
        )
        assert r.addizionale_comunale_annual == Decimal("0.00")


class TestProvenanceChain:
    """The PayrollResult carries the provenance of the rules it consumed."""

    def test_default_no_provenance(self) -> None:
        """A CCNL without provenance yields an empty provenance tuple."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        result = compute(ccnl, make_year_rules(), _req())
        assert result.provenance == ()

    def test_level_and_period_provenance_collected(self) -> None:
        """Level and per-period base-salary provenance are collected in order."""
        prov_level = _rule_provenance("level")
        prov_period = _rule_provenance("period")
        ccnl = CCNL.model_validate(make_ccnl_dict())
        level = ccnl.level_by_code("4")
        level.provenance = prov_level
        level.base_salary.periods[0].provenance = prov_period
        result = compute(ccnl, make_year_rules(), _req())
        assert result.provenance == (prov_level, prov_period)

    def test_allowance_and_seniority_provenance_collected(self) -> None:
        """Allowance and seniority-increment provenance are collected."""
        prov_allowance = _rule_provenance("allowance")
        prov_seniority = _rule_provenance("seniority")
        ccnl = CCNL.model_validate(make_ccnl_dict())
        level = ccnl.level_by_code("4")
        level.fixed_allowances = [
            Allowance(
                code="a",
                description="a",
                monthly=TimeSeries(
                    periods=[
                        ValidityPeriod(
                            valid_from=date(2020, 1, 1),
                            valid_until=None,
                            value=Decimal("10.00"),
                        )
                    ]
                ),
            )
        ]
        level.fixed_allowances[0].provenance = prov_allowance
        ccnl.parameters.seniority_increments.provenance = prov_seniority
        result = compute(ccnl, make_year_rules(), _req())
        assert prov_allowance in result.provenance
        assert prov_seniority in result.provenance

    def test_no_matching_period_skips_period_provenance(self) -> None:
        """When no salary period covers as_of, no period provenance is added."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        level = ccnl.level_by_code("4")
        prov_level = _rule_provenance("level")
        prov_period = _rule_provenance("period")
        level.provenance = prov_level
        level.base_salary.periods[0].valid_from = date(2025, 1, 1)
        level.base_salary.periods[0].provenance = prov_period
        # Calling _collect_provenance directly with a date before the period.
        result = _collect_provenance(
            level,
            date(2024, 6, 1),
            MonthlyPayChain(base=_D(0), seniority=_D(0), allowances=()),
            ccnl.parameters.seniority_increments,
        )
        assert result == (prov_level,)
