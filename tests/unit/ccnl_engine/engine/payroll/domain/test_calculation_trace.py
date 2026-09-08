"""Tests for CalculationTrace: step construction, round-trip, and invariant.

The key property asserted here is the gross-chain invariant:
    sum(s.amount for non-GROSS steps) == gross step amount

This must hold for every compute() call, including part-time, apprentice, and
RAL-override scenarios.  The invariant is enforced by construction inside
``_build_trace`` via the ``RAL_OVERRIDE`` adjustment step.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    SupplementaryAllowance,
    TaxSector,
)
from ccnl_engine.engine.contract.service.loaders import load_ccnl as _real_load_ccnl
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
    PayrollScenario,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.surtax.service.loaders import (
    load_surtax_rules as _real_load_surtax,
)
from ccnl_engine.engine.tax.service.loaders import (
    load_year_rules as _real_load_year_rules,
)
from tests.helpers import make_minimal_ccnl, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _req,
)

_CASES_DIR = Path(__file__).parents[5] / "integration" / "cases"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))

_GROSS_CONTRIBUTOR_CATS = {
    TraceCategory.BASE_SALARY,
    TraceCategory.SENIORITY,
    TraceCategory.ALLOWANCE,
    TraceCategory.AD_PERSONAM,
    TraceCategory.SECOND_LEVEL,
    TraceCategory.RAL_OVERRIDE,
}

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_DEFAULT_CCNL = make_minimal_ccnl()
_DEFAULT_RULES = make_year_rules()

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[object] = [_DEFAULT_RULES]
_mock_surtax: list[object] = [None]


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the three loaders in orchestrator and reset mock state."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_DEFAULT_RULES]
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


class TestTraceStep:
    """TraceStep construction and round-trip serialisation."""

    def test_required_fields(self) -> None:
        """TraceStep can be built with just category, label, and amount."""
        step = TraceStep(
            category=TraceCategory.BASE_SALARY,
            label="Base retributiva",
            amount=Decimal("1000.00"),
        )
        assert step.detail is None

    def test_with_detail(self) -> None:
        """TraceStep stores optional detail string."""
        step = TraceStep(
            category=TraceCategory.ALLOWANCE,
            label="EDR",
            amount=Decimal("10.33"),
            detail="edr",
        )
        assert step.detail == "edr"

    def test_to_dict(self) -> None:
        """to_dict produces a JSON-native dict with str amount."""
        step = TraceStep(
            category=TraceCategory.SENIORITY,
            label="Scatti di anzianità",
            amount=Decimal("82.64"),
            detail="scatti=3",
        )
        d = step.to_dict()
        assert d["category"] == "seniority"
        assert d["label"] == "Scatti di anzianità"
        assert d["amount"] == "82.64"
        assert d["detail"] == "scatti=3"

    def test_roundtrip_no_detail(self) -> None:
        """to_dict/from_dict round-trips a step without detail."""
        step = TraceStep(
            category=TraceCategory.GROSS,
            label="Lordo mensile",
            amount=Decimal("1082.64"),
        )
        assert TraceStep.from_dict(step.to_dict()) == step

    def test_roundtrip_with_detail(self) -> None:
        """to_dict/from_dict round-trips a step with detail."""
        step = TraceStep(
            category=TraceCategory.ALLOWANCE,
            label="Contingenza",
            amount=Decimal("517.51"),
            detail="contingenza",
        )
        assert TraceStep.from_dict(step.to_dict()) == step

    def test_amount_preserved_as_decimal(self) -> None:
        """from_dict restores amount as Decimal, not float."""
        step = TraceStep(
            category=TraceCategory.BASE_SALARY,
            label="Base",
            amount=Decimal("1234.56"),
        )
        restored = TraceStep.from_dict(step.to_dict())
        assert type(restored.amount) is Decimal


class TestCalculationTrace:
    """CalculationTrace construction and round-trip serialisation."""

    def test_empty_trace(self) -> None:
        """CalculationTrace accepts an empty steps tuple."""
        trace = CalculationTrace(steps=())
        assert trace.steps == ()

    def test_to_dict_from_dict_roundtrip(self) -> None:
        """to_dict/from_dict restores the full trace."""
        trace = CalculationTrace(
            steps=(
                TraceStep(TraceCategory.BASE_SALARY, "Base", Decimal("1000.00")),
                TraceStep(TraceCategory.GROSS, "Lordo mensile", Decimal("1000.00")),
            )
        )
        assert CalculationTrace.from_dict(trace.to_dict()) == trace

    def test_from_dict_empty_steps_key_missing(self) -> None:
        """from_dict tolerates a missing 'steps' key (returns empty trace)."""
        trace = CalculationTrace.from_dict({})
        assert trace.steps == ()


class TestTraceOnCalculation:
    """Calculation.trace is emitted by compute() and round-trips correctly."""

    def test_compute_produces_trace(self) -> None:
        """compute() returns a Calculation with a non-empty trace."""
        calc = compute(_req())
        assert len(calc.trace.steps) > 0

    def test_trace_ends_with_gross(self) -> None:
        """The last trace step is always the GROSS summary."""
        calc = compute(_req())
        assert calc.trace.steps[-1].category == TraceCategory.GROSS

    def test_trace_gross_amount_matches_result(self) -> None:
        """The GROSS trace step amount equals result.gross_monthly."""
        calc = compute(_req())
        gross_step = calc.trace.steps[-1]
        assert gross_step.amount == calc.result.gross_monthly

    def test_trace_base_salary_detail_contains_level(self) -> None:
        """BASE_SALARY detail contains the level code."""
        calc = compute(_req())
        base_step = next(
            s for s in calc.trace.steps if s.category == TraceCategory.BASE_SALARY
        )
        assert "4" in (base_step.detail or "")

    def test_calculation_to_dict_from_dict_roundtrip(self) -> None:
        """Calculation.to_dict/from_dict preserves the trace."""
        calc = compute(_req())
        restored = Calculation.from_dict(calc.to_dict())
        assert restored.trace == calc.trace

    def test_calculation_to_json_from_json_roundtrip(self) -> None:
        """Calculation.to_json/from_json preserves the trace."""
        calc = compute(_req())
        restored = Calculation.from_json(calc.to_json())
        assert restored.trace == calc.trace

    def test_backward_compat_from_dict_without_trace(self) -> None:
        """from_dict with no 'trace' key yields an empty CalculationTrace."""
        calc = compute(_req())
        d = calc.to_dict()
        d.pop("trace")
        restored = Calculation.from_dict(d)
        assert restored.trace == CalculationTrace(steps=())

    def test_trace_dict_has_steps_key(self) -> None:
        """to_dict includes a 'trace' key with a 'steps' list."""
        calc = compute(_req())
        d = calc.to_dict()
        assert "trace" in d
        assert isinstance(d["trace"], dict)
        trace_dict = d["trace"]
        assert isinstance(trace_dict, dict)
        assert isinstance(trace_dict["steps"], list)


class TestTraceInvariant:
    """Gross-chain invariant: sum(non-GROSS steps) == GROSS step amount."""

    def _assert_invariant(self, calc: Calculation) -> None:
        """Assert the invariant on a Calculation."""
        steps = calc.trace.steps
        assert len(steps) >= 2, "trace must have at least BASE_SALARY + GROSS"
        gross_step = steps[-1]
        assert gross_step.category == TraceCategory.GROSS
        component_sum = sum(
            (s.amount for s in steps if s.category in _GROSS_CONTRIBUTOR_CATS),
            Decimal(0),
        )
        assert component_sum == gross_step.amount, (
            f"component sum {component_sum} != GROSS step {gross_step.amount}"
        )

    def test_invariant_basic(self) -> None:
        """Invariant holds for a standard full-time employee (no allowances)."""
        calc = compute(_req())
        self._assert_invariant(calc)

    def test_invariant_part_time(self) -> None:
        """Invariant holds for a 50% part-time employee."""
        calc = compute(_req(part_time_pct=_D("0.5"), seniority_count=3))
        self._assert_invariant(calc)

    def test_invariant_apprentice(self) -> None:
        """Invariant holds for a percentage-based apprentice."""
        calc = compute(_req(contract=Apprentice(months_elapsed=12)))
        self._assert_invariant(calc)

    def test_invariant_ral_override(self) -> None:
        """Invariant holds even when a negotiated RAL overrides the gross."""
        calc = compute(_req(negotiated_ral=_D("15000.00")))
        # RAL override → a RAL_OVERRIDE step bridges the delta
        has_ral_step = any(
            s.category == TraceCategory.RAL_OVERRIDE for s in calc.trace.steps
        )
        assert has_ral_step
        self._assert_invariant(calc)

    def test_invariant_zero_seniority(self) -> None:
        """Invariant holds when seniority count is zero (no scatti)."""
        calc = compute(_req(seniority_count=0))
        self._assert_invariant(calc)

    def test_invariant_zero_second_level_skipped(self) -> None:
        """A zero-amount second-level allowance is not emitted as a step."""
        sl = SupplementaryAllowance(
            code="bonus",
            description="Bonus aziendale",
            monthly=Decimal("0.00"),
        )
        calc = compute(_req(second_level_allowances=(sl,)))
        second_level_steps = [
            s for s in calc.trace.steps if s.category == TraceCategory.SECOND_LEVEL
        ]
        assert second_level_steps == []
        self._assert_invariant(calc)

    @pytest.mark.parametrize("case_file", _CASE_FILES, ids=lambda p: p.stem)
    def test_invariant_integration_cases(self, case_file: Path) -> None:
        """Invariant holds for every real integration case."""
        case = json.loads(case_file.read_text(encoding="utf-8"))
        inputs = case["inputs"]

        # Load real CCNL and rules and inject into the module-level mocks
        # so compute(scenario) picks them up via the patched loader.
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

        scenario = PayrollScenario(
            employee=Employee(
                level_code=inputs["level_code"],
                seniority=(
                    SeniorityByCount(seniority_count) if seniority_count else None
                ),
                part_time_pct=Decimal(inputs["part_time_pct"]),
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
                    Agreement(ral_override=RalOverride(Decimal(negotiated_ral_raw)))
                    if negotiated_ral_raw is not None
                    else None
                ),
            ),
            employment=Employment(
                ccnl=inputs["ccnl_file"],
                contract=contract,
                employer=Employer(num_employees=num_employees),
                date=date.fromisoformat(inputs["as_of"]),
            ),
        )
        calc = compute(scenario)
        self._assert_invariant(calc)


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
