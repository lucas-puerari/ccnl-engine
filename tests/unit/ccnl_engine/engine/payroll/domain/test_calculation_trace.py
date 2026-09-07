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

from ccnl_engine.engine.contract.domain.ccnl import SupplementaryAllowance, TaxSector
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    TraceCategory,
    TraceStep,
)
from ccnl_engine.engine.payroll.domain.employee import (
    ContractPosition,
    Employee,
    RalOverride,
    SalaryOverrides,
    SeniorityByCount,
    TaxProfile,
    WorkArrangement,
)
from ccnl_engine.engine.payroll.domain.employer import Employer
from ccnl_engine.engine.payroll.domain.employment import Apprentice, Permanent
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.engine.tax.service.loaders import load_year_rules
from tests.helpers import make_minimal_ccnl, make_year_rules

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


def _employee(*, level_code: str = "4", seniority: int = 2) -> Employee:
    return Employee(
        position=ContractPosition(
            level_code=level_code,
            as_of=date(2026, 6, 1),
            employment=Permanent(),
        ),
        arrangement=WorkArrangement(seniority=SeniorityByCount(seniority)),
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
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        assert len(calc.trace.steps) > 0

    def test_trace_ends_with_gross(self) -> None:
        """The last trace step is always the GROSS summary."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        assert calc.trace.steps[-1].category == TraceCategory.GROSS

    def test_trace_gross_amount_matches_result(self) -> None:
        """The GROSS trace step amount equals result.gross_monthly."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        gross_step = calc.trace.steps[-1]
        assert gross_step.amount == calc.result.gross_monthly

    def test_trace_base_salary_detail_contains_level(self) -> None:
        """BASE_SALARY detail contains the level code."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        base_step = next(
            s for s in calc.trace.steps if s.category == TraceCategory.BASE_SALARY
        )
        assert "4" in (base_step.detail or "")

    def test_calculation_to_dict_from_dict_roundtrip(self) -> None:
        """Calculation.to_dict/from_dict preserves the trace."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        restored = Calculation.from_dict(calc.to_dict())
        assert restored.trace == calc.trace

    def test_calculation_to_json_from_json_roundtrip(self) -> None:
        """Calculation.to_json/from_json preserves the trace."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        restored = Calculation.from_json(calc.to_json())
        assert restored.trace == calc.trace

    def test_backward_compat_from_dict_without_trace(self) -> None:
        """from_dict with no 'trace' key yields an empty CalculationTrace."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        d = calc.to_dict()
        d.pop("trace")
        restored = Calculation.from_dict(d)
        assert restored.trace == CalculationTrace(steps=())

    def test_trace_dict_has_steps_key(self) -> None:
        """to_dict includes a 'trace' key with a 'steps' list."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
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
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee())
        self._assert_invariant(calc)

    def test_invariant_part_time(self) -> None:
        """Invariant holds for a 50% part-time employee."""
        employee = Employee(
            position=ContractPosition(
                level_code="4",
                as_of=date(2026, 6, 1),
                employment=Permanent(),
            ),
            arrangement=WorkArrangement(
                part_time_pct=Decimal("0.5"),
                seniority=SeniorityByCount(3),
            ),
        )
        calc = compute(make_minimal_ccnl(), make_year_rules(), employee)
        self._assert_invariant(calc)

    def test_invariant_apprentice(self) -> None:
        """Invariant holds for a percentage-based apprentice."""
        employee = Employee(
            position=ContractPosition(
                level_code="4",
                as_of=date(2026, 6, 1),
                employment=Apprentice(months_elapsed=12),
            ),
            arrangement=WorkArrangement(seniority=None),
        )
        calc = compute(make_minimal_ccnl(), make_year_rules(), employee)
        self._assert_invariant(calc)

    def test_invariant_ral_override(self) -> None:
        """Invariant holds even when a negotiated RAL overrides the gross."""
        employee = Employee(
            position=ContractPosition(
                level_code="4",
                as_of=date(2026, 6, 1),
                employment=Permanent(),
            ),
            arrangement=WorkArrangement(seniority=SeniorityByCount(0)),
            agreement=SalaryOverrides(ral_override=RalOverride(Decimal("15000.00"))),
        )
        calc = compute(make_minimal_ccnl(), make_year_rules(), employee)
        # RAL override → a RAL_OVERRIDE step bridges the delta
        has_ral_step = any(
            s.category == TraceCategory.RAL_OVERRIDE for s in calc.trace.steps
        )
        assert has_ral_step
        self._assert_invariant(calc)

    def test_invariant_zero_seniority(self) -> None:
        """Invariant holds when seniority count is zero (no scatti)."""
        calc = compute(make_minimal_ccnl(), make_year_rules(), _employee(seniority=0))
        self._assert_invariant(calc)

    def test_invariant_zero_second_level_skipped(self) -> None:
        """A zero-amount second-level allowance is not emitted as a step."""
        employer = Employer(
            second_level_allowances=(
                SupplementaryAllowance(
                    code="bonus",
                    description="Bonus aziendale",
                    monthly=Decimal("0.00"),
                ),
            )
        )
        calc = compute(
            make_minimal_ccnl(), make_year_rules(), _employee(), employer=employer
        )
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

        ccnl = load_ccnl(inputs["ccnl_file"])
        rules = load_year_rules(
            inputs["year"],
            TaxSector(inputs["tax_sector"]),
            int(inputs["num_employees"]),
        )

        emp_type = inputs["employment_type"]
        if emp_type == "permanent":
            employment: Permanent | Apprentice = Permanent()
        else:
            employment = Apprentice(months_elapsed=int(inputs["months_elapsed"]))

        seniority_count = int(inputs["seniority_count"])
        weekly_hours_raw = inputs.get("weekly_hours")
        arrangement = WorkArrangement(
            part_time_pct=Decimal(inputs["part_time_pct"]),
            seniority=SeniorityByCount(seniority_count) if seniority_count else None,
            weekly_hours=(
                Decimal(str(weekly_hours_raw)) if weekly_hours_raw is not None else None
            ),
        )

        regione = inputs.get("regione")
        comune = inputs.get("comune_belfiore")
        surtax = load_surtax_rules(inputs["year"]) if regione or comune else None
        tax = (
            TaxProfile(regione=regione, comune_belfiore=comune)
            if regione or comune
            else None
        )

        negotiated_ral = inputs.get("negotiated_ral")
        agreement = (
            SalaryOverrides(ral_override=RalOverride(Decimal(negotiated_ral)))
            if negotiated_ral is not None
            else None
        )

        calc = compute(
            ccnl,
            rules,
            Employee(
                position=ContractPosition(
                    level_code=inputs["level_code"],
                    as_of=date.fromisoformat(inputs["as_of"]),
                    employment=employment,
                    category=inputs.get("category"),
                ),
                arrangement=arrangement,
                tax=tax,
                agreement=agreement,
            ),
            surtax=surtax,
        )
        self._assert_invariant(calc)
