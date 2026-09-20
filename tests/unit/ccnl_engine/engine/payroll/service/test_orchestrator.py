"""Tests for engine/compute/orchestrator — compute() and helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    SupplementaryAllowance,
    TaxSector,
)
from ccnl_engine.engine.metadata.domain.rules import (
    VerificationStatus,
)
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
    SeniorityByCount,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    AnnualEstimateInput,
    Employee,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.payroll.service.rounding import money
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
from tests.helpers import (
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
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.surtax.domain.rules import (
        SurtaxRules,
    )
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules as SurtaxRulesT
    from ccnl_engine.engine.tax.domain.rules import YearRules
_TEST_TAX_PERIOD = TaxPeriod(
    start=_DATE,
    end=date(2026, 12, 31),
    eligible_work_days=(date(2026, 12, 31) - _DATE).days + 1,
)


def compute(
    scenario: AnnualEstimateInput,
    period: PeriodPayrollInput | None = None,
) -> Calculation:
    """Route to estimate_period_effects or estimate_annual.

    When calling with a period that has no tax_period set, a test-default
    TaxPeriod covering the remainder of 2026 from _DATE is injected.

    Returns:
        Calculation from the appropriate estimator.
    """
    if period is not None:
        if period.tax_period is None:
            period = period.model_copy(update={"tax_period": _TEST_TAX_PERIOD})
        return estimate_period_effects(scenario, period, repo=_REPO)
    return estimate_annual(scenario, repo=_REPO)


_DEFAULT_CCNL = _build_ccnl()
_DEFAULT_CCNL_UC = _build_ccnl("under_classification")

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[YearRules] = [_RULES]
_mock_surtax: list[SurtaxRulesT | None] = [None]


class _MockRepo:
    """KnowledgeRepository stub for the autouse _reset_mock_state fixture."""

    def load_ccnl(self, filename: str) -> CCNL:
        return _mock_ccnl[0]

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        return _mock_rules[0]

    def load_surtax_rules(self, year: int) -> SurtaxRules | None:
        return _mock_surtax[0]

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:
        return CapabilityCatalog(year=year, capabilities=())


_REPO = _MockRepo()


@pytest.fixture(autouse=True)
def _reset_mock_state() -> None:
    """Reset mutable mock state before each test."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_RULES]
    _mock_surtax[:] = [None]


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
            estimate_annual(_req(level_code="NOPE"), repo=_REPO)

    def test_seniority_count_above_maximum_raises(self) -> None:
        """SeniorityByCount above the level maximum must raise ValueError."""
        with pytest.raises(ValueError, match="exceeds the maximum of 10"):
            estimate_annual(_req(seniority_count=11), repo=_REPO)

    def test_second_level_with_ral_override_raises(self) -> None:
        """second_level_allowances cannot be combined with a RAL override."""
        sl = SupplementaryAllowance(code="X", description="X", monthly=_D("100"))
        with pytest.raises(ValueError, match="RAL override"):
            estimate_annual(
                _req(negotiated_ral=_D("20000"), second_level_allowances=(sl,)),
                repo=_REPO,
            )

    def test_negotiated_destination_ral_on_non_apprentice_raises(self) -> None:
        """DestinationRalOverride with a non-Apprentice contract raises."""
        with pytest.raises(ValueError, match="only valid for Apprentice"):
            estimate_annual(_req(negotiated_destination_ral=_D("20000.00")), repo=_REPO)


# ---------------------------------------------------------------------------
# Permanent employment
# ---------------------------------------------------------------------------


class TestComputePermanent:
    """Permanent contract paths in compute()."""

    def test_full_time_no_seniority(self) -> None:
        """Permanent, full-time, no seniority: standard salary chain."""
        r = estimate_annual(_req(), repo=_REPO).result

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
        r = estimate_annual(_req(seniority_count=2), repo=_REPO).result

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
        r = estimate_annual(_req(seniority_months=months), repo=_REPO).result
        assert r.earnings.seniority_count == expected

    @pytest.mark.parametrize(
        ("months", "expected"), [(47, 0), (48, 1), (83, 1), (84, 2), (120, 3)]
    )
    def test_seniority_first_cadence(self, months: int, expected: int) -> None:
        """First increment after first_cadence_months, then every cadence_months."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months": 48
        })
        r = estimate_annual(_req(seniority_months=months), repo=_REPO).result
        assert r.earnings.seniority_count == expected

    def test_seniority_first_cadence_by_level(self) -> None:
        """Per-level first cadence (e.g. operai lump step at 48 months)."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.first_cadence_months_by_level": {"4": 48}
        })
        r47 = estimate_annual(_req(seniority_months=47), repo=_REPO).result
        r48 = estimate_annual(_req(seniority_months=48), repo=_REPO).result
        assert r47.earnings.seniority_count == 0
        assert r48.earnings.seniority_count == 1
        res = estimate_annual(
            _req(level_code="3", seniority_months=36), repo=_REPO
        ).result
        assert res.earnings.seniority_count == 1

    def test_seniority_per_level_maximum(self) -> None:
        """maximum_count_by_level overrides maximum_count for that level."""
        _mock_ccnl[0] = _build_ccnl(**{
            "parameters.seniority_increments.maximum_count_by_level": {"4": 1}
        })
        r = estimate_annual(_req(seniority_months=360), repo=_REPO).result
        assert r.earnings.seniority_count == 1
        assert r.earnings.seniority_monthly == _D("20.00")
        with pytest.raises(ValueError, match="exceeds the maximum of 1"):
            estimate_annual(_req(seniority_count=2), repo=_REPO)

    def test_part_time_scales_all_components(self) -> None:
        """part_time_ratio=0.5 halves every component; components sum to gross."""
        _mock_ccnl[0] = _build_ccnl(**{
            "levels.2.fixed_allowances": [_allowance("edr", "10.33")]
        })
        r = estimate_annual(
            _req(part_time_ratio=_D("0.50"), seniority_count=1), repo=_REPO
        ).result

        assert r.earnings.base_monthly == _D("500.00")
        assert r.earnings.seniority_monthly == _D("10.00")
        assert r.earnings.allowances_monthly == _D("5.17")
        assert r.earnings.gross_monthly == _D("515.17")
        assert r.earnings.gross_annual == _D("6182.04")

    def test_negotiated_ral(self) -> None:
        """RalOverride overrides gross_annual; gross_monthly stays consistent."""
        ral = _D("20000.00")
        r = estimate_annual(_req(negotiated_ral=ral), repo=_REPO).result

        assert r.earnings.gross_annual == ral
        assert r.earnings.gross_monthly == _D("1666.67")

    def test_level_without_seniority_entry(self) -> None:
        """Level '3' has no seniority in amount_by_level — seniority stays zero."""
        r = estimate_annual(_req(level_code="3", seniority_count=5), repo=_REPO).result

        assert r.earnings.seniority_monthly == _D("0.00")
        assert r.earnings.base_monthly == _D("800.00")
        assert r.earnings.gross_annual == _D("9600.00")

    def test_ad_personam_added_unscaled(self) -> None:
        """ad_personam_monthly is added as given, even under part-time."""
        r = estimate_annual(
            _req(part_time_ratio=_D("0.50"), ad_personam_monthly=_D("30.00")),
            repo=_REPO,
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
        plain = estimate_annual(_req(), repo=_REPO).result
        quadro = estimate_annual(_req(roles=frozenset({"quadro"})), repo=_REPO).result
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
        r = estimate_annual(_req(), repo=_REPO).result
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
        r = estimate_annual(_req(), repo=_REPO).result
        # Re-fetch base with default CCNL
        _mock_ccnl[0] = _DEFAULT_CCNL
        base = estimate_annual(_req(), repo=_REPO).result
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
        r = estimate_annual(_req(), repo=_REPO).result
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
        r_with_exclusion = estimate_annual(_req(negotiated_ral=ral), repo=_REPO).result
        _mock_ccnl[0] = _DEFAULT_CCNL
        r_clean = estimate_annual(_req(negotiated_ral=ral), repo=_REPO).result

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
        operaio = estimate_annual(_req(), repo=_REPO).result
        impiegato = estimate_annual(_req(level_code="3"), repo=_REPO).result
        uncategorised = estimate_annual(_req(level_code="2"), repo=_REPO).result
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
        r = estimate_annual(_req(level_code="3"), repo=_REPO).result
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
        impiegato = estimate_annual(_req(level_code="3"), repo=_REPO).result
        operaio = estimate_annual(_req(), repo=_REPO).result
        assert impiegato.contributions.inps_employer_annual == _D("1920.00")  # 9600*0.2
        assert operaio.contributions.inps_employer_annual == _D("3600.00")  # 12000*0.30


# ---------------------------------------------------------------------------
# Fixed-term employment
# ---------------------------------------------------------------------------


class TestComputeFixedTerm:
    """Fixed-term contract adds NASpI addizionale to employer INPS."""

    def test_fixed_term_naspi_addizionale(self) -> None:
        """Employer INPS for fixed-term must exceed permanent by 1.4% of gross."""
        r_fixed = estimate_annual(_req(contract=_FIXED_TERM), repo=_REPO).result
        r_perm = estimate_annual(_req(), repo=_REPO).result

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
