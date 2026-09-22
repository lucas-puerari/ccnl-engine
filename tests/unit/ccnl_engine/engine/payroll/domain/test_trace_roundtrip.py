"""Roundtrip tests for CalculationTrace: fiscal_steps, supplement_steps, strict dict."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    TaxSector,
)
from ccnl_engine.engine.contract.service.loaders import load_ccnl as _real_load_ccnl
from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    TraceCategory,
    TraceStep,
)
from ccnl_engine.engine.payroll.domain.employee import RalOverride, SeniorityByCount
from ccnl_engine.engine.payroll.domain.employment import Apprentice, Permanent
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
)
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual
from ccnl_engine.engine.payroll.service.pipeline import compute
from ccnl_engine.engine.surtax.service.loaders import (
    load_surtax_rules as _real_load_surtax,
)
from ccnl_engine.engine.tax.service.loaders import (
    load_year_rules as _real_load_year_rules,
)
from tests.helpers import make_minimal_ccnl, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_CASES_DIR = Path(__file__).parents[5] / "integration" / "cases"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_DEFAULT_CCNL = make_minimal_ccnl()
_DEFAULT_RULES = make_year_rules()

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[YearRules] = [_DEFAULT_RULES]
_mock_surtax: list[SurtaxRules | None] = [None]


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
    _mock_rules[:] = [_DEFAULT_RULES]
    _mock_surtax[:] = [None]


class TestFiscalStepsRoundtrip:
    """CalculationTrace.fiscal_steps serialises and round-trips correctly."""

    def _make_fiscal_step(
        self,
        category: TraceCategory = TraceCategory.NET,
        amount: str = "15000.00",
    ) -> TraceStep:
        return TraceStep(
            category=category,
            label="step",
            amount=Decimal(amount),
            period="annual",
        )

    def test_to_dict_emits_fiscal_steps_when_non_empty(self) -> None:
        """fiscal_steps key appears in to_dict output when non-empty."""
        trace = CalculationTrace(
            steps=(TraceStep(TraceCategory.GROSS, "Lordo", Decimal("2000.00")),),
            fiscal_steps=(self._make_fiscal_step(),),
        )
        d = trace.to_dict()
        assert "fiscal_steps" in d
        assert len(d["fiscal_steps"]) == 1  # type: ignore[arg-type]

    def test_to_dict_omits_fiscal_steps_when_empty(self) -> None:
        """fiscal_steps key is absent when tuple is empty."""
        trace = CalculationTrace(
            steps=(TraceStep(TraceCategory.GROSS, "Lordo", Decimal("2000.00")),),
        )
        d = trace.to_dict()
        assert "fiscal_steps" not in d

    def test_from_dict_restores_fiscal_steps(self) -> None:
        """from_dict reconstructs fiscal_steps from a serialised dict."""
        step = self._make_fiscal_step(TraceCategory.IRPEF_NET, "3000.00")
        trace = CalculationTrace(
            steps=(TraceStep(TraceCategory.GROSS, "Lordo", Decimal("20000.00")),),
            fiscal_steps=(step,),
        )
        restored = CalculationTrace.from_dict(trace.to_dict())
        assert restored.fiscal_steps == trace.fiscal_steps

    def test_from_dict_fiscal_steps_absent_when_empty(self) -> None:
        """fiscal_steps key is absent in to_dict and restores to () in from_dict."""
        trace = CalculationTrace(
            steps=(TraceStep(TraceCategory.GROSS, "Lordo", Decimal("2000.00")),),
        )
        d = trace.to_dict()
        assert "fiscal_steps" not in d
        restored = CalculationTrace.from_dict(d)
        assert restored.fiscal_steps == ()

    def test_compute_produces_fiscal_steps(self) -> None:
        """compute() returns a Calculation with non-empty fiscal_steps."""
        calc = estimate_annual(_req(), repo=_REPO)
        assert len(calc.trace.fiscal_steps) > 0

    def test_fiscal_steps_all_annual(self) -> None:
        """Every fiscal step has period='annual'."""
        calc = estimate_annual(_req(), repo=_REPO)
        for step in calc.trace.fiscal_steps:
            assert step.period == "annual", (
                f"step {step.category} has period={step.period!r}"
            )

    def test_fiscal_trace_contains_net_step(self) -> None:
        """Fiscal steps include a NET step matching result.net_annual."""
        calc = estimate_annual(_req(), repo=_REPO)
        net_step = next(
            s for s in calc.trace.fiscal_steps if s.category == TraceCategory.NET
        )
        assert net_step.amount == calc.result.net_annual

    def test_fiscal_trace_contains_gross_step(self) -> None:
        """Fiscal steps include a GROSS step matching result.earnings.gross_annual."""
        calc = estimate_annual(_req(), repo=_REPO)
        gross_step = next(
            s for s in calc.trace.fiscal_steps if s.category == TraceCategory.GROSS
        )
        assert gross_step.amount == calc.result.earnings.gross_annual

    def test_fiscal_steps_roundtrip(self) -> None:
        """Calculation.to_dict/from_dict preserves fiscal_steps."""
        calc = estimate_annual(_req(), repo=_REPO)
        restored = Calculation.from_dict(calc.to_dict())
        assert restored.trace.fiscal_steps == calc.trace.fiscal_steps

    def test_fiscal_steps_json_roundtrip(self) -> None:
        """Calculation.to_json/from_json preserves fiscal_steps."""
        calc = estimate_annual(_req(), repo=_REPO)
        restored = Calculation.from_json(calc.to_json())
        assert restored.trace.fiscal_steps == calc.trace.fiscal_steps

    def test_fiscal_steps_carry_formula_and_source(self) -> None:
        """compute() produces fiscal steps with formula/source populated."""
        calc = estimate_annual(_req(), repo=_REPO)
        by_cat = {s.category: s for s in calc.trace.fiscal_steps}
        # INPS step must have both formula and source
        inps = by_cat[TraceCategory.INPS_EMPLOYEE]
        assert inps.formula is not None
        assert inps.source is not None
        # NET step must have formula
        net = by_cat[TraceCategory.NET]
        assert net.formula is not None
        # TFR step must have source
        tfr = by_cat[TraceCategory.TFR]
        assert tfr.source is not None

    def test_contribution_base_step_present(self) -> None:
        """compute() emits a CONTRIBUTION_BASE fiscal step."""
        calc = estimate_annual(_req(), repo=_REPO)
        cats = {s.category for s in calc.trace.fiscal_steps}
        assert TraceCategory.CONTRIBUTION_BASE in cats

    @pytest.mark.parametrize("case_file", _CASE_FILES, ids=lambda p: p.stem)
    def test_fiscal_closure_integration_cases(self, case_file: Path) -> None:
        """Fiscal closure invariant holds for every integration case.

        net = gross - inps_employee - irpef_net
              - addizionale_regionale - addizionale_comunale
              + trattamento_integrativo
        """
        case = json.loads(case_file.read_text(encoding="utf-8"))
        inputs = case["inputs"]

        ccnl = _real_load_ccnl(inputs["ccnl_file"])
        num_employees = int(inputs["num_employees"])
        rules = _real_load_year_rules(
            inputs["year"],
            TaxSector(inputs["tax_sector"]),
            num_employees,
        )
        _mock_ccnl[0] = ccnl
        _mock_rules[0] = rules

        regione = inputs.get("regione")
        comune = inputs.get("comune_belfiore")
        if regione or comune:
            _mock_surtax[0] = _real_load_surtax(inputs["year"])

        emp_type = inputs["employment_type"]
        if emp_type == "permanent":
            contract: Permanent | Apprentice = Permanent()
        else:
            contract = Apprentice(months_elapsed=int(inputs["months_elapsed"]))

        seniority_count = int(inputs["seniority_count"])
        weekly_hours_raw = inputs.get("weekly_hours")
        negotiated_ral_raw = inputs.get("negotiated_ral")
        ivs_ceiling_applies = bool(inputs.get("ivs_ceiling_applies", False))
        has_jurisdiction = (
            regione is not None or comune is not None or ivs_ceiling_applies
        )

        scenario = _InternalScenario(
            employee=Employee(
                level_code=inputs["level_code"],
                seniority=(
                    SeniorityByCount(value=seniority_count) if seniority_count else None
                ),
                part_time_ratio=Decimal(inputs["part_time_ratio"]),
                weekly_hours=(
                    Decimal(str(weekly_hours_raw))
                    if weekly_hours_raw is not None
                    else None
                ),
                category=inputs.get("category"),
                ivs_ceiling_applies=ivs_ceiling_applies,
                jurisdiction=(
                    Jurisdiction(regione=regione, comune_belfiore=comune)
                    if has_jurisdiction
                    else None
                ),
                agreement=(
                    Agreement(
                        ral_override=RalOverride(value=Decimal(negotiated_ral_raw))
                    )
                    if negotiated_ral_raw is not None
                    else None
                ),
            ),
            employment=Employment(
                ccnl=inputs["ccnl_file"],
                contract=contract,
                employer=Employer(num_employees=num_employees),
                as_of=date.fromisoformat(inputs["as_of"]),
            ),
        )
        calc = compute(scenario)

        by_cat = {s.category: s for s in calc.trace.fiscal_steps}
        gross = by_cat[TraceCategory.GROSS].amount
        inps = by_cat[TraceCategory.INPS_EMPLOYEE].amount
        irpef = by_cat[TraceCategory.IRPEF_NET].amount
        add_reg = by_cat[TraceCategory.ADDIZIONALE_REGIONALE].amount
        add_com = by_cat[TraceCategory.ADDIZIONALE_COMUNALE].amount
        ti = by_cat[TraceCategory.TRATTAMENTO_INTEGRATIVO].amount
        se = by_cat[TraceCategory.SOMMA_ESENTE].amount
        net = by_cat[TraceCategory.NET].amount
        expected = gross - inps - irpef - add_reg - add_com + ti + se
        assert net == expected, (
            f"{case_file.stem}: fiscal closure violated: {net} != {expected}"
        )


class TestSupplementStepsRoundtrip:
    """CalculationTrace.supplement_steps serialises and round-trips correctly."""

    def test_to_dict_emits_supplement_steps_when_non_empty(self) -> None:
        """supplement_steps key appears in to_dict output only when non-empty."""
        supp_step = TraceStep(
            category=TraceCategory.TIME_SUPPLEMENT,
            label="OT diurno",
            amount=Decimal("17.90"),
            detail="OT_DIURNO/weekday",
        )
        total_step = TraceStep(
            category=TraceCategory.SUPPLEMENT_TOTAL,
            label="Totale maggiorazioni",
            amount=Decimal("17.90"),
        )
        trace = CalculationTrace(
            steps=(
                TraceStep(TraceCategory.BASE_SALARY, "Base", Decimal("2064.88")),
                TraceStep(TraceCategory.GROSS, "Lordo mensile", Decimal("2064.88")),
            ),
            supplement_steps=(supp_step, total_step),
        )
        d = trace.to_dict()
        assert "supplement_steps" in d
        assert len(d["supplement_steps"]) == 2  # type: ignore[arg-type]

    def test_to_dict_omits_supplement_steps_when_empty(self) -> None:
        """supplement_steps key is absent when tuple is empty."""
        trace = CalculationTrace(
            steps=(TraceStep(TraceCategory.GROSS, "Lordo", Decimal(1000)),),
        )
        d = trace.to_dict()
        assert "supplement_steps" not in d

    def test_from_dict_restores_supplement_steps(self) -> None:
        """from_dict reconstructs supplement_steps from a serialised dict."""
        supp = TraceStep(
            category=TraceCategory.TIME_SUPPLEMENT,
            label="OT notte",
            amount=Decimal("11.94"),
        )
        total = TraceStep(
            category=TraceCategory.SUPPLEMENT_TOTAL,
            label="Totale",
            amount=Decimal("11.94"),
        )
        trace = CalculationTrace(
            steps=(TraceStep(TraceCategory.GROSS, "Lordo", Decimal("2064.88")),),
            supplement_steps=(supp, total),
        )
        restored = CalculationTrace.from_dict(trace.to_dict())
        assert restored.supplement_steps == trace.supplement_steps

    def test_from_dict_backward_compat_no_supplement_steps(self) -> None:
        """from_dict with no supplement_steps key yields an empty tuple."""
        trace = CalculationTrace(
            steps=(TraceStep(TraceCategory.GROSS, "Lordo", Decimal("2064.88")),),
        )
        d = trace.to_dict()
        assert "supplement_steps" not in d
        restored = CalculationTrace.from_dict(d)
        assert restored.supplement_steps == ()


class TestTraceStepFromDictStrict:
    """TraceStep.from_dict rejects non-str label and invalid period."""

    def _base(self) -> dict[str, object]:
        step = TraceStep(
            category=TraceCategory.BASE_SALARY,
            label="Base retributiva",
            amount=Decimal("1500.00"),
        )
        return step.to_dict()

    def test_label_int_rejected(self) -> None:
        """Integer label raises TypeError."""
        d = self._base()
        d["label"] = 42
        with pytest.raises(TypeError, match="label must be str"):
            TraceStep.from_dict(d)

    def test_period_invalid_raises(self) -> None:
        """An unrecognised period value raises ValueError."""
        d = self._base()
        d["period"] = "weekly"
        with pytest.raises(ValueError, match="period must be"):
            TraceStep.from_dict(d)
