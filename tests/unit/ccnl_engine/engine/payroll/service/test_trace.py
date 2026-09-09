"""Unit tests for build_fiscal_trace.

Verifies that the fiscal chain is emitted correctly, that the NET step
matches the expected derivation, that zero-amount steps are always present,
and that the employer_withholds_irpef fork labels steps correctly.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.calculation import TraceCategory, TraceStep
from ccnl_engine.engine.payroll.service.trace import build_fiscal_trace

_ZERO = Decimal(0)


def _base_kwargs() -> dict[str, object]:
    """Return a minimal set of kwargs for build_fiscal_trace.

    Returns:
        A dict with all required keyword arguments, matching the
        acconciatura-estetica reference scenario.
    """
    return {
        "gross_annual": Decimal("19136.00"),
        "inps_employee_annual": Decimal("1758.60"),
        "inps_employer_annual": Decimal("5153.32"),
        "employer_funds_annual": Decimal("0.00"),
        "tfr_annual": Decimal("1417.48"),
        "taxable_income": Decimal("17377.40"),
        "irpef_gross": Decimal("3996.80"),
        "work_income_deduction": Decimal("1270.48"),
        "family_deduction_annual": Decimal("0.00"),
        "art15_deduction_annual": Decimal("0.00"),
        "irpef_net": Decimal("2726.32"),
        "addizionale_regionale_annual": Decimal("0.00"),
        "addizionale_comunale_annual": Decimal("0.00"),
        "trattamento_integrativo": Decimal("818.22"),
        "net_annual": Decimal("15469.30"),
        "employer_withholds_irpef": True,
    }


def _build(**overrides: object) -> tuple[TraceStep, ...]:
    kwargs = {**_base_kwargs(), **overrides}
    return build_fiscal_trace(**kwargs)  # type: ignore[arg-type]


def _step_by(
    steps: tuple[TraceStep, ...],
    category: TraceCategory,
) -> TraceStep:
    """Return the first step with the given category.

    Returns:
        The first :class:`TraceStep` whose category matches *category*.

    Raises:
        KeyError: If no step with *category* is found.
    """
    for s in steps:
        if s.category == category:
            return s
    raise KeyError(category)


class TestBuildFiscalTrace:
    """build_fiscal_trace output structure and content."""

    def test_returns_non_empty_tuple(self) -> None:
        """build_fiscal_trace returns at least one step."""
        steps = _build()
        assert len(steps) > 0

    def test_all_steps_are_annual(self) -> None:
        """Every step has period='annual'."""
        steps = _build()
        for step in steps:
            assert step.period == "annual", (
                f"step {step.category} has period={step.period!r}"
            )

    def test_gross_step_amount(self) -> None:
        """GROSS step amount matches gross_annual."""
        steps = _build()
        gross = _step_by(steps, TraceCategory.GROSS)
        assert gross.amount == Decimal("19136.00")

    def test_net_step_amount(self) -> None:
        """NET step amount matches net_annual."""
        steps = _build()
        net = _step_by(steps, TraceCategory.NET)
        assert net.amount == Decimal("15469.30")

    def test_taxable_income_step(self) -> None:
        """TAXABLE_INCOME step amount matches taxable_income."""
        steps = _build()
        ti = _step_by(steps, TraceCategory.TAXABLE_INCOME)
        assert ti.amount == Decimal("17377.40")

    def test_zero_family_deduction_emitted(self) -> None:
        """FAMILY_DEDUCTION step is always present, even when zero."""
        steps = _build(family_deduction_annual=_ZERO)
        fam = _step_by(steps, TraceCategory.FAMILY_DEDUCTION)
        assert fam.amount == _ZERO

    def test_zero_art15_deduction_emitted(self) -> None:
        """ART15_DEDUCTION step is always present, even when zero."""
        steps = _build(art15_deduction_annual=_ZERO)
        art15 = _step_by(steps, TraceCategory.ART15_DEDUCTION)
        assert art15.amount == _ZERO

    def test_zero_addizionali_emitted(self) -> None:
        """Addizionale steps are present even when zero."""
        steps = _build(
            addizionale_regionale_annual=_ZERO,
            addizionale_comunale_annual=_ZERO,
        )
        _step_by(steps, TraceCategory.ADDIZIONALE_REGIONALE)
        _step_by(steps, TraceCategory.ADDIZIONALE_COMUNALE)

    def test_employer_side_steps_present(self) -> None:
        """Employer-side steps (INPS, TFR, funds) are always emitted."""
        steps = _build()
        _step_by(steps, TraceCategory.INPS_EMPLOYER)
        _step_by(steps, TraceCategory.TFR)
        _step_by(steps, TraceCategory.EMPLOYER_FUNDS)

    def test_irpef_withholds_true_label(self) -> None:
        """When employer_withholds_irpef=True, labels have no informativo suffix."""
        steps = _build(employer_withholds_irpef=True)
        irpef_step = _step_by(steps, TraceCategory.IRPEF_NET)
        assert "informativo" not in irpef_step.label

    def test_irpef_withholds_false_label(self) -> None:
        """When employer_withholds_irpef=False, IRPEF labels include informativo."""
        steps = _build(employer_withholds_irpef=False)
        irpef_gross_step = _step_by(steps, TraceCategory.IRPEF_GROSS)
        assert "informativo" in irpef_gross_step.label

    def test_inps_employee_amount(self) -> None:
        """INPS_EMPLOYEE step amount matches inps_employee_annual."""
        steps = _build()
        emp = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        assert emp.amount == Decimal("1758.60")

    def test_trattamento_integrativo_step(self) -> None:
        """TRATTAMENTO_INTEGRATIVO step amount matches trattamento_integrativo."""
        steps = _build()
        ti = _step_by(steps, TraceCategory.TRATTAMENTO_INTEGRATIVO)
        assert ti.amount == Decimal("818.22")

    def test_non_zero_family_deduction(self) -> None:
        """FAMILY_DEDUCTION step carries the supplied amount when non-zero."""
        steps = _build(family_deduction_annual=Decimal("500.00"))
        fam = _step_by(steps, TraceCategory.FAMILY_DEDUCTION)
        assert fam.amount == Decimal("500.00")

    def test_mandatory_categories_all_present(self) -> None:
        """All required fiscal categories appear in the trace."""
        required = {
            TraceCategory.GROSS,
            TraceCategory.INPS_EMPLOYEE,
            TraceCategory.TAXABLE_INCOME,
            TraceCategory.IRPEF_GROSS,
            TraceCategory.WORK_DEDUCTION,
            TraceCategory.FAMILY_DEDUCTION,
            TraceCategory.ART15_DEDUCTION,
            TraceCategory.IRPEF_NET,
            TraceCategory.ADDIZIONALE_REGIONALE,
            TraceCategory.ADDIZIONALE_COMUNALE,
            TraceCategory.TRATTAMENTO_INTEGRATIVO,
            TraceCategory.NET,
            TraceCategory.INPS_EMPLOYER,
            TraceCategory.TFR,
            TraceCategory.EMPLOYER_FUNDS,
        }
        steps = _build()
        present = {s.category for s in steps}
        missing = required - present
        assert not missing, f"Missing categories: {missing}"

    @pytest.mark.parametrize(
        "cat",
        [
            TraceCategory.FAMILY_DEDUCTION,
            TraceCategory.ART15_DEDUCTION,
            TraceCategory.ADDIZIONALE_REGIONALE,
            TraceCategory.ADDIZIONALE_COMUNALE,
            TraceCategory.TRATTAMENTO_INTEGRATIVO,
        ],
    )
    def test_zero_steps_emitted_unconditionally(self, cat: TraceCategory) -> None:
        """Zero-amount steps are always emitted (stable skeleton)."""
        steps = _build()
        present = {s.category for s in steps}
        assert cat in present
