"""Unit tests for render_breakdown and AnnualBreakdown.

Verifies that the breakdown correctly projects PayrollResult fields
in payslip order, handles degenerate inputs (zero gross), and round-trips
to/from JSON.
"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.bilateral_funds import FlatMonthlyFund
from ccnl_engine.engine.payroll.domain.scenario import AnnualEstimateInput
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual
from ccnl_engine.engine.payroll.service.render import render_breakdown
from tests.helpers import make_minimal_ccnl, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import _req

compute = estimate_annual

_DEFAULT_CCNL = make_minimal_ccnl()
_DEFAULT_RULES = make_year_rules()

_mock_ccnl: list[object] = [_DEFAULT_CCNL]
_mock_rules: list[object] = [_DEFAULT_RULES]


class _MockRepo:
    """Minimal KnowledgeRepository stub used by the autouse _patch_loaders fixture."""

    def load_ccnl(self, filename: str) -> object:
        return _mock_ccnl[0]

    def load_year_rules(self, year: int, sector: object, num_employees: int) -> object:
        return _mock_rules[0]

    def load_surtax_rules(self, year: int) -> None:
        return


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the repository in orchestrator and reset mock state."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_DEFAULT_RULES]
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.pipeline._default_repo",
        _MockRepo(),
    )


_ZERO = Decimal(0)


class TestAnnualBreakdownFields:
    """render_breakdown maps PayrollResult fields to AnnualBreakdown."""

    def test_ulteriore_detrazione_lavoro(self) -> None:
        """ulteriore_detrazione_lavoro matches result.taxes field."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert (
            bd.ulteriore_detrazione_lavoro
            == calc.result.taxes.ulteriore_detrazione_lavoro
        )

    def test_somma_esente_zero_when_rules_absent(self) -> None:
        """somma_esente is zero when year rules carry no somma_esente config."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.somma_esente == _ZERO

    def test_bilateral_employee_zero_when_no_funds(self) -> None:
        """bilateral_employee_annual is zero when no bilateral funds were supplied."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.bilateral_employee_annual == _ZERO

    def test_bilateral_employer_zero_when_no_funds(self) -> None:
        """bilateral_employer_annual is zero when no bilateral funds were supplied."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.bilateral_employer_annual == _ZERO

    def test_gross_annual(self) -> None:
        """gross_annual matches result.earnings.gross_annual."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.gross_annual == calc.result.earnings.gross_annual

    def test_inps_employee_annual(self) -> None:
        """inps_employee_annual matches result.contributions.inps_employee_annual."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.inps_employee_annual == calc.result.contributions.inps_employee_annual

    def test_taxable_income(self) -> None:
        """taxable_income matches result.taxes.taxable_income."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.taxable_income == calc.result.taxes.taxable_income

    def test_irpef_gross(self) -> None:
        """irpef_gross matches result.taxes.irpef_gross."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.irpef_gross == calc.result.taxes.irpef_gross

    def test_irpef_net(self) -> None:
        """irpef_net matches result.taxes.irpef_net."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.irpef_net == calc.result.taxes.irpef_net

    def test_net_annual(self) -> None:
        """net_annual matches result.net_annual."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.net_annual == calc.result.net_annual

    def test_employer_cost_annual(self) -> None:
        """employer_cost_annual matches result.employer_cost.employer_cost_annual."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.employer_cost_annual == calc.result.employer_cost.employer_cost_annual

    def test_family_deduction_zero_when_absent(self) -> None:
        """family_deduction_annual is zero when no family was supplied."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.family_deduction_annual == _ZERO

    def test_art15_deduction_zero_when_absent(self) -> None:
        """art15_deduction_annual is zero when no Art. 15 input was supplied."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.art15_deduction_annual == _ZERO

    def test_employer_withholds_irpef(self) -> None:
        """employer_withholds_irpef matches result.taxes.employer_withholds_irpef."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.employer_withholds_irpef == calc.result.taxes.employer_withholds_irpef


class TestAnnualBreakdownNetMonthlyApprox:
    """net_monthly_approx is derived from additional_months."""

    def test_net_monthly_approx_nonzero(self) -> None:
        """net_monthly_approx is non-zero for a standard full-time scenario."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.net_monthly_approx > _ZERO

    def test_net_monthly_approx_equals_result_net_monthly(self) -> None:
        """net_monthly_approx equals result.net_monthly (from orchestrator)."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.net_monthly_approx == calc.result.net_monthly


class TestAnnualBreakdownSerialisation:
    """AnnualBreakdown serialises and round-trips via to_dict / to_json."""

    def test_to_dict_has_gross_annual(self) -> None:
        """to_dict includes gross_annual as a string."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        d = bd.to_dict()
        assert "gross_annual" in d
        assert isinstance(d["gross_annual"], str)

    def test_to_dict_has_net_annual(self) -> None:
        """to_dict includes net_annual as a string."""
        calc = estimate_annual(_req())
        d = render_breakdown(calc.result).to_dict()
        assert "net_annual" in d

    def test_to_json_is_valid_json(self) -> None:
        """to_json returns parseable JSON."""
        calc = estimate_annual(_req())
        raw = render_breakdown(calc.result).to_json()
        parsed = json.loads(raw)
        assert "net_annual" in parsed


class TestNetReconciliation:
    """net_annual arithmetic identity holds in AnnualBreakdown."""

    def test_net_annual_reconciles(self) -> None:
        """net_annual equals gross minus INPS minus IRPEF plus bonuses."""
        calc = estimate_annual(_req())
        r = calc.result
        bd = render_breakdown(r)
        expected = (
            bd.gross_annual
            - bd.inps_employee_annual
            - bd.irpef_net
            - bd.addizionale_regionale_annual
            - bd.addizionale_comunale_annual
            + bd.trattamento_integrativo
            + bd.somma_esente
            - bd.bilateral_employee_annual
        )
        assert bd.net_annual == expected

    def test_employer_cost_reconciles(self) -> None:
        """employer_cost_annual equals gross plus employer charges."""
        calc = estimate_annual(_req())
        r = calc.result
        bd = render_breakdown(r)
        expected = (
            bd.gross_annual
            + bd.inps_employer_annual
            + bd.employer_funds_annual
            + bd.bilateral_employer_annual
            + bd.tfr_annual
        )
        assert bd.employer_cost_annual == expected


class TestBilateralFunds:
    """bilateral fund amounts are propagated by render_breakdown."""

    def test_bilateral_employee_annual_exposed(self) -> None:
        """bilateral_employee_annual is non-zero when a fund is supplied."""
        fund = FlatMonthlyFund(
            employee_monthly=Decimal(5),
            employer_monthly=Decimal(3),
        )
        scenario = AnnualEstimateInput(
            employee=_req().employee,
            employment=_req().employment,
            bilateral_funds=(fund,),
        )
        calc = compute(scenario)
        bd = render_breakdown(calc.result)
        assert bd.bilateral_employee_annual == Decimal(60)

    def test_bilateral_employer_annual_exposed(self) -> None:
        """bilateral_employer_annual is non-zero when a fund is supplied."""
        fund = FlatMonthlyFund(
            employee_monthly=Decimal(5),
            employer_monthly=Decimal(3),
        )
        scenario = AnnualEstimateInput(
            employee=_req().employee,
            employment=_req().employment,
            bilateral_funds=(fund,),
        )
        calc = compute(scenario)
        bd = render_breakdown(calc.result)
        assert bd.bilateral_employer_annual == Decimal(36)


_STRD_RULES = {"threshold": "200000", "reduction": "440"}
_HIGH_RAL = Decimal(250000)


class TestSterilizzazioneClawbackField:
    """sterilizzazione_clawback_annual is exposed by render_breakdown."""

    def test_zero_without_threshold_rules(self) -> None:
        """Field is zero in a default (low-income, no threshold) scenario."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        assert bd.sterilizzazione_clawback_annual == _ZERO

    def test_matches_result_field(self) -> None:
        """sterilizzazione_clawback_annual mirrors the result field."""
        calc = estimate_annual(_req())
        bd = render_breakdown(calc.result)
        expected = calc.result.taxes.sterilizzazione_clawback_annual
        assert bd.sterilizzazione_clawback_annual == expected

    def test_exposed_in_to_dict(self) -> None:
        """sterilizzazione_clawback_annual appears in to_dict as a string."""
        calc = estimate_annual(_req())
        d = render_breakdown(calc.result).to_dict()
        assert "sterilizzazione_clawback_annual" in d
        assert isinstance(d["sterilizzazione_clawback_annual"], str)

    def test_nonzero_above_threshold(self) -> None:
        """Clawback > 0 at high income with Art. 15 and threshold rules."""
        rules = make_year_rules(sterilizzazione_detrazioni=_STRD_RULES)
        _mock_rules[0] = rules
        scenario = _req(negotiated_ral=_HIGH_RAL).model_copy(
            update={
                "art15_deductions": Art15Deductions(mortgage_interest=Decimal(4000))
            }
        )
        calc = compute(scenario)
        bd = render_breakdown(calc.result)
        assert bd.sterilizzazione_clawback_annual > _ZERO
        result_clawback = calc.result.taxes.sterilizzazione_clawback_annual
        assert bd.sterilizzazione_clawback_annual == result_clawback


class TestIrpefIdentityAboveClawbackThreshold:
    """irpef_net = max(0, irpef_gross - deductions + clawback) at high income."""

    def test_irpef_identity_with_clawback(self) -> None:
        """irpef_net equals the statutory formula including the clawback."""
        rules = make_year_rules(sterilizzazione_detrazioni=_STRD_RULES)
        _mock_rules[0] = rules
        scenario = _req(negotiated_ral=_HIGH_RAL).model_copy(
            update={
                "art15_deductions": Art15Deductions(mortgage_interest=Decimal(4000))
            }
        )
        bd = render_breakdown(compute(scenario).result)
        expected = max(
            _ZERO,
            bd.irpef_gross
            - bd.work_income_deduction
            - bd.family_deduction_annual
            + bd.sterilizzazione_clawback_annual
            - bd.art15_deduction_annual
            - bd.ulteriore_detrazione_lavoro,
        )
        assert bd.irpef_net == expected

    def test_clawback_increases_irpef_net(self) -> None:
        """With sterilizzazione active, irpef_net is higher than without."""
        rules_with = make_year_rules(sterilizzazione_detrazioni=_STRD_RULES)
        rules_without = make_year_rules()
        scenario = _req(negotiated_ral=_HIGH_RAL).model_copy(
            update={
                "art15_deductions": Art15Deductions(mortgage_interest=Decimal(4000))
            }
        )
        _mock_rules[0] = rules_with
        bd_with = render_breakdown(compute(scenario).result)
        _mock_rules[0] = rules_without
        bd_without = render_breakdown(compute(scenario).result)
        assert bd_with.irpef_net > bd_without.irpef_net
        delta = bd_with.irpef_net - bd_without.irpef_net
        assert delta == bd_with.sterilizzazione_clawback_annual
