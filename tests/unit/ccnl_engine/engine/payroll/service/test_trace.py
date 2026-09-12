"""Unit tests for build_fiscal_trace.

Verifies that the fiscal chain is emitted correctly, that the NET step
matches the expected derivation, that zero-amount steps are always present,
and that the employer_withholds_irpef fork labels steps correctly.

Also verifies that each step carries the expected structured metadata
(formula, source, rounding) and that the fiscal closure invariant holds:
    net = gross - inps_employee - irpef_net
          - addizionale_regionale - addizionale_comunale
          + trattamento_integrativo
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
        "contribution_base": Decimal("19136.00"),
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
            TraceCategory.CONTRIBUTION_BASE,
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

    def test_contribution_base_step_amount(self) -> None:
        """CONTRIBUTION_BASE step amount matches the supplied contribution_base."""
        steps = _build(contribution_base=Decimal("18000.00"))
        cb = _step_by(steps, TraceCategory.CONTRIBUTION_BASE)
        assert cb.amount == Decimal("18000.00")


class TestFiscalStepMetadata:
    """Structured metadata (formula, source, rounding) on fiscal steps."""

    def test_inps_employee_source(self) -> None:
        """INPS_EMPLOYEE step carries the statutory INPS source reference."""
        steps = _build()
        emp = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        assert emp.source is not None
        assert "335" in emp.source  # L. 335/1995

    def test_inps_employee_formula_default(self) -> None:
        """INPS_EMPLOYEE step formula describes the percentage model by default."""
        steps = _build()
        emp = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        assert emp.formula is not None
        assert "aliquota" in emp.formula

    def test_inps_employee_formula_override_via_inps_formula(self) -> None:
        """inps_formula kwarg overrides the default INPS_EMPLOYEE formula."""
        steps = _build(inps_formula="tariffa_oraria_INPS * ore_annuali_contratto")
        emp = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        assert emp.formula == "tariffa_oraria_INPS * ore_annuali_contratto"

    def test_inps_formula_none_uses_default(self) -> None:
        """When inps_formula is None the default formula is applied."""
        steps = _build(inps_formula=None)
        emp = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        assert emp.formula is not None  # default from _STEP_META

    def test_irpef_gross_source(self) -> None:
        """IRPEF_GROSS step carries Art. 11 TUIR as source."""
        steps = _build()
        irpef = _step_by(steps, TraceCategory.IRPEF_GROSS)
        assert irpef.source == "Art. 11 TUIR"

    def test_irpef_gross_rounding(self) -> None:
        """IRPEF_GROSS step has rounding set (rate computation involved)."""
        steps = _build()
        irpef = _step_by(steps, TraceCategory.IRPEF_GROSS)
        assert irpef.rounding is not None

    def test_taxable_income_formula(self) -> None:
        """TAXABLE_INCOME step formula describes the derivation."""
        steps = _build()
        ti = _step_by(steps, TraceCategory.TAXABLE_INCOME)
        assert ti.formula is not None
        assert "INPS" in ti.formula

    def test_taxable_income_no_rounding(self) -> None:
        """TAXABLE_INCOME is a pure subtraction; rounding is not set."""
        steps = _build()
        ti = _step_by(steps, TraceCategory.TAXABLE_INCOME)
        assert ti.rounding is None

    def test_net_formula(self) -> None:
        """NET step formula covers the full derivation from gross to net."""
        steps = _build()
        net = _step_by(steps, TraceCategory.NET)
        assert net.formula is not None
        assert "lordo" in net.formula.lower() or "gross" in net.formula.lower()

    def test_net_no_rounding(self) -> None:
        """NET is a pure derivation; rounding is not set."""
        steps = _build()
        net = _step_by(steps, TraceCategory.NET)
        assert net.rounding is None

    def test_tfr_source(self) -> None:
        """TFR step carries Art. 2120 c.c. as source."""
        steps = _build()
        tfr = _step_by(steps, TraceCategory.TFR)
        assert tfr.source == "Art. 2120 c.c."

    def test_tfr_rounding(self) -> None:
        """TFR step has rounding set (rate computation involved)."""
        steps = _build()
        tfr = _step_by(steps, TraceCategory.TFR)
        assert tfr.rounding is not None

    def test_addizionale_regionale_source(self) -> None:
        """ADDIZIONALE_REGIONALE step carries Art. 50 TUIR as source."""
        steps = _build()
        reg = _step_by(steps, TraceCategory.ADDIZIONALE_REGIONALE)
        assert reg.source == "Art. 50 TUIR"

    def test_addizionale_comunale_source(self) -> None:
        """ADDIZIONALE_COMUNALE step carries D.Lgs. 360/1998 as source."""
        steps = _build()
        com = _step_by(steps, TraceCategory.ADDIZIONALE_COMUNALE)
        assert com.source is not None
        assert "360" in com.source

    def test_trattamento_integrativo_source(self) -> None:
        """TRATTAMENTO_INTEGRATIVO step carries Art. 1 D.L. 3/2020 as source."""
        steps = _build()
        ti_step = _step_by(steps, TraceCategory.TRATTAMENTO_INTEGRATIVO)
        assert ti_step.source is not None
        assert "3/2020" in ti_step.source

    def test_work_deduction_source(self) -> None:
        """WORK_DEDUCTION step carries Art. 13 TUIR as source."""
        steps = _build()
        wd = _step_by(steps, TraceCategory.WORK_DEDUCTION)
        assert wd.source == "Art. 13 TUIR"

    def test_gross_no_formula_no_rounding(self) -> None:
        """GROSS step has no formula and no rounding (it is the anchor)."""
        steps = _build()
        gross = _step_by(steps, TraceCategory.GROSS)
        assert gross.formula is None
        assert gross.rounding is None


class TestFiscalClosureInvariant:
    """Fiscal closure: net = gross - inps - irpef - add_reg - add_com + ti."""

    def test_fiscal_closure_basic(self) -> None:
        """Closure holds for the reference acconciatura-estetica scenario."""
        steps = _build()
        gross = _step_by(steps, TraceCategory.GROSS).amount
        inps = _step_by(steps, TraceCategory.INPS_EMPLOYEE).amount
        irpef = _step_by(steps, TraceCategory.IRPEF_NET).amount
        add_reg = _step_by(steps, TraceCategory.ADDIZIONALE_REGIONALE).amount
        add_com = _step_by(steps, TraceCategory.ADDIZIONALE_COMUNALE).amount
        ti = _step_by(steps, TraceCategory.TRATTAMENTO_INTEGRATIVO).amount
        net = _step_by(steps, TraceCategory.NET).amount
        expected = gross - inps - irpef - add_reg - add_com + ti
        assert net == expected, f"fiscal closure violated: {net} != {expected}"

    def test_fiscal_closure_with_addizionali(self) -> None:
        """Closure holds when addizionali are non-zero."""
        steps = _build(
            addizionale_regionale_annual=Decimal("200.00"),
            addizionale_comunale_annual=Decimal("50.00"),
            net_annual=Decimal("15219.30"),
        )
        gross = _step_by(steps, TraceCategory.GROSS).amount
        inps = _step_by(steps, TraceCategory.INPS_EMPLOYEE).amount
        irpef = _step_by(steps, TraceCategory.IRPEF_NET).amount
        add_reg = _step_by(steps, TraceCategory.ADDIZIONALE_REGIONALE).amount
        add_com = _step_by(steps, TraceCategory.ADDIZIONALE_COMUNALE).amount
        ti = _step_by(steps, TraceCategory.TRATTAMENTO_INTEGRATIVO).amount
        net = _step_by(steps, TraceCategory.NET).amount
        assert net == gross - inps - irpef - add_reg - add_com + ti


class TestR25DynamicFormulas:
    """R25: dynamic trace formulas for TFR divisor, IVS ceiling, IRPEF incapienza."""

    def test_tfr_formula_contains_default_divisor(self) -> None:
        """Default TFR formula embeds 13.5 as the divisor."""
        steps = _build()
        tfr = _step_by(steps, TraceCategory.TFR)
        assert tfr.formula is not None
        assert "13.5" in tfr.formula

    def test_tfr_formula_uses_custom_divisor(self) -> None:
        """R25: custom TFR divisor is embedded in the formula."""
        steps = _build(tfr_divisor=Decimal(14))
        tfr = _step_by(steps, TraceCategory.TFR)
        assert tfr.formula is not None
        assert "14" in tfr.formula

    def test_ivs_ceiling_formula_when_applies(self) -> None:
        """R25: when IVS ceiling applies, INPS formula reflects the split."""
        steps = _build(
            ivs_ceiling_applies=True,
            ivs_ceiling=Decimal(120000),
        )
        inps = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        assert inps.formula is not None
        assert "min" in inps.formula
        assert "120000" in inps.formula

    def test_ivs_ceiling_formula_not_set_when_not_applies(self) -> None:
        """When IVS ceiling does not apply, INPS formula stays at default."""
        steps = _build(ivs_ceiling_applies=False, ivs_ceiling=Decimal(120000))
        inps = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        # Default INPS meta formula is "base_imponibile_INPS * aliquota_dipendente"
        assert inps.formula is not None
        assert "min" not in inps.formula

    def test_ivs_ceiling_none_ignores_applies_flag(self) -> None:
        """IVS ceiling formula override requires both flag and ceiling value."""
        steps = _build(ivs_ceiling_applies=True, ivs_ceiling=None)
        inps = _step_by(steps, TraceCategory.INPS_EMPLOYEE)
        assert inps.formula is not None
        assert "min" not in inps.formula

    def test_irpef_incapienza_formula_when_floored(self) -> None:
        """R25: IRPEF net floored at 0 by deductions — formula notes incapienza."""
        # irpef_gross=100, work_deduction=200 → irpef_net floored to 0
        steps = _build(
            irpef_gross=Decimal(100),
            work_income_deduction=Decimal(200),
            irpef_net=Decimal(0),
        )
        irpef_net_step = _step_by(steps, TraceCategory.IRPEF_NET)
        assert irpef_net_step.formula is not None
        assert "incapienza" in irpef_net_step.formula

    def test_irpef_formula_none_when_not_incapiente(self) -> None:
        """When IRPEF net is positive, no incapienza formula override is used."""
        steps = _build()
        irpef_net_step = _step_by(steps, TraceCategory.IRPEF_NET)
        # Default IRPEF_NET formula from _STEP_META is used when not incapiente
        assert irpef_net_step.formula is not None
        assert "incapienza" not in irpef_net_step.formula

    def test_irpef_formula_none_when_irpef_gross_is_zero(self) -> None:
        """When IRPEF gross is 0 and net is 0, incapienza formula does not apply."""
        steps = _build(irpef_gross=Decimal(0), irpef_net=Decimal(0))
        irpef_net_step = _step_by(steps, TraceCategory.IRPEF_NET)
        assert irpef_net_step.formula is not None
        assert "incapienza" not in irpef_net_step.formula
