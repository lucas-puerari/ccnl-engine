"""Provenance-chain tests: rule origin, apprentice, trace, R7 identities."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    Allowance,
    TaxSector,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.metadata.domain.rules import (
    VerificationStatus,
)
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.calculation import Calculation, TraceCategory
from ccnl_engine.engine.payroll.domain.employment import Apprentice
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    BonusInput,
    FringeBenefitInput,
)
from ccnl_engine.engine.payroll.service.assembly import _collect_provenance
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
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
from tests.helpers import (
    make_ccnl_dict,
    make_year_rules,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
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


_CHILD_DEP = Dependent(
    relationship=DependentRelationship.CHILD, birth_date=date(2000, 1, 1)
)


class TestProvenanceChain:
    """The PayrollResult carries the provenance of the rules it consumed."""

    def test_provenance_always_present(self) -> None:
        """All CCNLs carry provenance; minimal dict yields a non-empty tuple."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        _mock_ccnl[0] = ccnl
        _mock_rules[0] = make_year_rules()
        result = estimate_annual(_req(), repo=_REPO).result
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
        result = estimate_annual(_req(), repo=_REPO).result
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
        result = estimate_annual(_req(), repo=_REPO).result
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
        calc = estimate_annual(_req(level_code="4"), repo=_REPO)
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
        calc = estimate_annual(_req(), repo=_REPO)
        assert "sick_pay" not in calc.ruleset_version
        assert "variable_pay" not in calc.ruleset_version

    def test_variable_pay_ruleset_present_with_fringe_benefit_input(self) -> None:
        """R7: fringe benefit input causes variable_pay to appear in ruleset_version."""
        calc = compute(
            _req(),
            PeriodPayrollInput(
                fringe_benefit_input=FringeBenefitInput(annual_amount=_D("500"))
            ),
        )
        assert "variable_pay" in calc.ruleset_version

    def test_variable_pay_ruleset_present_with_bonus_input(self) -> None:
        """R7: bonus input causes variable_pay to appear in ruleset_version."""
        calc = compute(
            _req(),
            PeriodPayrollInput(
                bonus_input=BonusInput(annual_amount=_D("1000"), eligible_for_pdr=False)
            ),
        )
        assert "variable_pay" in calc.ruleset_version

    def test_family_deductions_ruleset_present_when_dependents(self) -> None:
        """family_deductions appears in ruleset_version when scenario.family is set."""
        calc = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_CHILD_DEP,))}
            ),
            repo=_REPO,
        )
        assert "family_deductions" in calc.ruleset_version, (
            f"Expected family_deductions in ruleset_version,"
            f" got: {calc.ruleset_version}"
        )

    def test_family_deductions_ruleset_absent_without_dependents(self) -> None:
        """family_deductions absent when no dependents in the scenario."""
        calc = estimate_annual(_req(), repo=_REPO)
        assert "family_deductions" not in calc.ruleset_version

    def test_art15_deductions_ruleset_present_when_oneri_set(self) -> None:
        """art15_deductions appears in ruleset_version when art15_deductions is set."""
        calc = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("2000"))
                }
            ),
            repo=_REPO,
        )
        assert "art15_deductions" in calc.ruleset_version, (
            f"Expected art15_deductions in ruleset_version, got: {calc.ruleset_version}"
        )

    def test_art15_deductions_ruleset_absent_without_oneri(self) -> None:
        """art15_deductions absent when art15_deductions is None."""
        calc = estimate_annual(_req(), repo=_REPO)
        assert "art15_deductions" not in calc.ruleset_version
