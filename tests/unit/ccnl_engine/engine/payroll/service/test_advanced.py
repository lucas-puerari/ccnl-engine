"""Advanced integration: bilateral funds, surtax identities, caller scope."""

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
    RulesetIdentity,
    SourceType,
    VerificationStatus,
)
from ccnl_engine.engine.payroll.domain.bilateral_funds import (
    FlatMonthlyFund,
    RateFund,
)
from ccnl_engine.engine.payroll.domain.employee import (
    SeniorityByDate,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Jurisdiction,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    _ivs_ceiling_warning,
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.payroll.service.rounding import money
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
from tests.helpers import (
    TEST_PROV,
    TEST_RULESET_VERIFIED,
    make_ccnl_dict,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
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
    raw = make_ccnl_dict()
    raw["levels"] = [
        _verified_level("2", 2, "600.00"),
        _verified_level("3", 3, "800.00"),
        _verified_level("4", 4, "1000.00"),
    ]
    raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
    raw["ruleset"] = TEST_RULESET_VERIFIED
    return CCNL.model_validate(raw)


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
        result = estimate_annual(_req(), repo=_REPO).result
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
        baseline = estimate_annual(_req(), repo=_REPO).result
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
        baseline = estimate_annual(_req(), repo=_REPO).result
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
        baseline = estimate_annual(_req(), repo=_REPO).result
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
        baseline = estimate_annual(_req(), repo=_REPO).result
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
        baseline = estimate_annual(_req(), repo=_REPO).result
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
        result = estimate_annual(_req(), repo=_REPO).result
        scope_map = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope_map["bilateral_funds"] == "excluded"

    def test_multiple_funds_accumulate(self) -> None:
        """Multiple funds in the tuple accumulate correctly."""
        baseline = estimate_annual(_req(), repo=_REPO).result
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
        r = estimate_annual(_req(seniority_months=120), repo=_REPO).result
        assert any("overstated" in w for w in r.coverage.warnings)

    def test_seniority_by_months_pre_1996_no_warning(self) -> None:
        """SeniorityByMonths implying pre-1996 hire produces no warning."""
        # 480 months = 40 years; implied hire ~1986, pre-1996
        r = estimate_annual(_req(seniority_months=480), repo=_REPO).result
        assert not any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_seniority_by_months_with_ceiling_no_warning(self) -> None:
        """SeniorityByMonths with ivs_ceiling_applies=True produces no warning."""
        r = estimate_annual(
            _req(seniority_months=120, ivs_ceiling_applies=True), repo=_REPO
        ).result
        assert not any("ivs_ceiling_applies" in w for w in r.coverage.warnings)

    def test_seniority_by_count_emits_warning(self) -> None:
        """SeniorityByCount with ivs_ceiling_applies=False triggers warning."""
        r = estimate_annual(_req(seniority_count=2), repo=_REPO).result
        assert any("overstated" in w for w in r.coverage.warnings)

    def test_seniority_by_count_with_ceiling_no_warning(self) -> None:
        """SeniorityByCount with ivs_ceiling_applies=True produces no warning."""
        r = estimate_annual(
            _req(seniority_count=2, ivs_ceiling_applies=True), repo=_REPO
        ).result
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
        r = estimate_annual(_req(), repo=_REPO).result
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
        calc = estimate_annual(_req(second_level_allowances=(sl,)), repo=_REPO)
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
            ),
            repo=_REPO,
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
            ),
            repo=_REPO,
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
            ),
            repo=_REPO,
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
            ),
            repo=_REPO,
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
            ),
            repo=_REPO,
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
            ),
            repo=_REPO,
        )
        assert calc.result.coverage.confidence == "medium"


class TestCallerDeclaredScope:
    """Caller-declared optional fields appear as caller_declared scope items."""

    def test_inail_rate_produces_caller_declared_scope_item(self) -> None:
        """Setting inail_rate yields a caller_declared inail scope item."""
        calc = estimate_annual(_req(inail_rate=_D("0.015")), repo=_REPO)
        scope = {item.feature: item for item in calc.result.coverage.calculation_scope}
        assert scope["inail"].eligibility_status == "caller_declared"

    def test_no_inail_rate_produces_excluded_scope_item(self) -> None:
        """Omitting inail_rate yields an excluded inail scope item."""
        calc = estimate_annual(_req(), repo=_REPO)
        scope = {item.feature: item for item in calc.result.coverage.calculation_scope}
        assert scope["inail"].calculation_status == "excluded"


class TestContractEffectiveDate:
    """contract_effective_date reflects the resolved salary tranche, not as_of."""

    def test_uses_tranche_valid_from_not_as_of(self) -> None:
        """contract_effective_date is the tranche valid_from, not as_of itself."""
        r = estimate_annual(_req(as_of=_DATE), repo=_REPO).result
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
        r = estimate_annual(_req(as_of=date(2026, 6, 1)), repo=_REPO).result
        assert r.contract_effective_date == date(2026, 4, 1)
