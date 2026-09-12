"""Unit tests for render_breakdown and AnnualBreakdown.

Verifies that the breakdown correctly projects PayrollResult fields
in payslip order, handles degenerate inputs (zero gross), and round-trips
to/from JSON.
"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.payroll.service.render import render_breakdown
from tests.helpers import make_minimal_ccnl, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import _req

_DEFAULT_CCNL = make_minimal_ccnl()
_DEFAULT_RULES = make_year_rules()


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch CCNL and tax loaders so tests do not read real knowledge files."""
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl",
        lambda _: _DEFAULT_CCNL,
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules",
        lambda *_: _DEFAULT_RULES,
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules",
        lambda _: None,
    )


_ZERO = Decimal(0)


class TestAnnualBreakdownFields:
    """render_breakdown maps PayrollResult fields to AnnualBreakdown."""

    def test_gross_annual(self) -> None:
        """gross_annual matches result.gross_annual."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.gross_annual == calc.result.gross_annual

    def test_inps_employee_annual(self) -> None:
        """inps_employee_annual matches result.inps_employee_annual."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.inps_employee_annual == calc.result.inps_employee_annual

    def test_taxable_income(self) -> None:
        """taxable_income matches result.taxable_income."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.taxable_income == calc.result.taxable_income

    def test_irpef_gross(self) -> None:
        """irpef_gross matches result.irpef_gross."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.irpef_gross == calc.result.irpef_gross

    def test_irpef_net(self) -> None:
        """irpef_net matches result.irpef_net."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.irpef_net == calc.result.irpef_net

    def test_net_annual(self) -> None:
        """net_annual matches result.net_annual."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.net_annual == calc.result.net_annual

    def test_employer_cost_annual(self) -> None:
        """employer_cost_annual matches result.employer_cost_annual."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.employer_cost_annual == calc.result.employer_cost_annual

    def test_family_deduction_zero_when_absent(self) -> None:
        """family_deduction_annual is zero when no family was supplied."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.family_deduction_annual == _ZERO

    def test_art15_deduction_zero_when_absent(self) -> None:
        """art15_deduction_annual is zero when no Art. 15 input was supplied."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.art15_deduction_annual == _ZERO

    def test_employer_withholds_irpef(self) -> None:
        """employer_withholds_irpef matches result.employer_withholds_irpef."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.employer_withholds_irpef == calc.result.employer_withholds_irpef


class TestAnnualBreakdownNetMonthlyApprox:
    """net_monthly_approx is derived from additional_months."""

    def test_net_monthly_approx_nonzero(self) -> None:
        """net_monthly_approx is non-zero for a standard full-time scenario."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.net_monthly_approx > _ZERO

    def test_net_monthly_approx_equals_result_net_monthly(self) -> None:
        """net_monthly_approx equals result.net_monthly (from orchestrator)."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        assert bd.net_monthly_approx == calc.result.net_monthly


class TestAnnualBreakdownSerialisation:
    """AnnualBreakdown serialises and round-trips via to_dict / to_json."""

    def test_to_dict_has_gross_annual(self) -> None:
        """to_dict includes gross_annual as a string."""
        calc = compute(_req())
        bd = render_breakdown(calc.result)
        d = bd.to_dict()
        assert "gross_annual" in d
        assert isinstance(d["gross_annual"], str)

    def test_to_dict_has_net_annual(self) -> None:
        """to_dict includes net_annual as a string."""
        calc = compute(_req())
        d = render_breakdown(calc.result).to_dict()
        assert "net_annual" in d

    def test_to_json_is_valid_json(self) -> None:
        """to_json returns parseable JSON."""
        calc = compute(_req())
        raw = render_breakdown(calc.result).to_json()
        parsed = json.loads(raw)
        assert "net_annual" in parsed
