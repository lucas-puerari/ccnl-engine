"""IRPEF credit outcomes and the decisions the tax computation records."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.tax.domain.credit_rules import (
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from ccnl_engine.engine.tax.service.loaders import load_year_rules
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.service.irpef_credits import (
    CreditOutcome,
    trattamento_integrativo_outcome,
    ulteriore_detrazione_outcome,
)
from ccnl_engine.payroll.service.tax_computation import (
    compute_tax,
    resolve_tax_computation,
)
from tests.helpers import make_year_rules

_D = Decimal
_TI = TrattamentoIntegrativoRules(
    threshold_mid=_D(15000), threshold_upper=_D(28000), max_amount=_D(1200)
)
_UD = UlterioreDetrazioneRules(
    threshold_low=_D(20000),
    threshold_mid=_D(32000),
    threshold_high=_D(40000),
    max_amount=_D(1000),
)
_UD_RAW = {
    "threshold_low": "20000",
    "threshold_mid": "32000",
    "threshold_high": "40000",
    "max_amount": "1000",
}
_RULES = load_year_rules(2026, TaxSector.TERZIARIO, 50)
_SCHEDULE = WithholdingSchedule.from_calendar(WorkCalendar(year=2026))


class TestTrattamentoOutcome:
    """Each branch of the trattamento integrativo has its own reason."""

    @pytest.mark.parametrize(
        ("income", "irpef", "deductions", "expected"),
        [
            (
                _D(30000),
                _D(6900),
                _D(1500),
                CreditOutcome(_D(0), "income_above_upper_threshold"),
            ),
            (_D(12000), _D(2760), _D(1955), CreditOutcome(_D(1200), "full_amount")),
            (
                _D(8000),
                _D(1840),
                _D(1955),
                CreditOutcome(_D(0), "irpef_not_above_work_deduction"),
            ),
            (
                _D(20000),
                _D(4600),
                _D(5000),
                CreditOutcome(_D(400), "deductions_above_irpef"),
            ),
            (
                _D(20000),
                _D(4600),
                _D(4000),
                CreditOutcome(_D(0), "deductions_not_above_irpef"),
            ),
        ],
    )
    def test_reason_matches_amount(
        self,
        income: Decimal,
        irpef: Decimal,
        deductions: Decimal,
        expected: CreditOutcome,
    ) -> None:
        """The outcome pairs the amount with the branch that produced it."""
        outcome = trattamento_integrativo_outcome(
            income, irpef, deductions, deductions, _TI
        )
        assert outcome == expected


class TestUlterioreOutcome:
    """Each zone of the ulteriore detrazione has its own reason."""

    @pytest.mark.parametrize(
        ("income", "expected"),
        [
            (_D(15000), CreditOutcome(_D(0), "income_not_above_lower_threshold")),
            (_D(45000), CreditOutcome(_D(0), "income_above_upper_threshold")),
            (_D(25000), CreditOutcome(_D(1000), "full_amount")),
            (_D(36000), CreditOutcome(_D(500), "tapered_amount")),
        ],
    )
    def test_reason_matches_amount(
        self, income: Decimal, expected: CreditOutcome
    ) -> None:
        """The outcome pairs the amount with the zone of the income."""
        assert ulteriore_detrazione_outcome(income, _UD) == expected

    def test_part_year_keeps_reason(self) -> None:
        """Proportioning to the days worked keeps the zone reason."""
        outcome = ulteriore_detrazione_outcome(_D(25000), _UD, 182)
        assert outcome == CreditOutcome(_D("498.6"), "full_amount")


class TestComputeTaxDecisions:
    """compute_tax records one decision per credit in force."""

    def test_low_income_decisions(self) -> None:
        """A low income gets the trattamento and no ulteriore detrazione."""
        tax = compute_tax(_D(12000), _RULES, withholding_schedule=_SCHEDULE)
        ulteriore, trattamento = tax.decisions
        assert ulteriore.capability == "ulteriore_detrazione_lavoro"
        assert ulteriore.reason_code == "income_not_above_lower_threshold"
        assert ulteriore.amount == _D(0)
        assert ulteriore.rule == "l207-2024-art1-c6"
        assert trattamento.capability == "trattamento_integrativo"
        assert trattamento.reason_code == "full_amount"
        assert trattamento.amount == _D(1200)
        assert trattamento.inputs["period_amount"] == _D(100)
        assert trattamento.inputs["recovery_in_progress"] == "false"
        assert all(d.status is CalculationStatus.FINAL for d in tax.decisions)
        assert {d.rule_version for d in tax.decisions} == {"2026.1"}

    def test_income_above_thresholds_is_decided_not_omitted(self) -> None:
        """A credit not due is a zero decision with its reason."""
        tax = compute_tax(_D(50000), _RULES, withholding_schedule=_SCHEDULE)
        assert [(d.reason_code, d.amount) for d in tax.decisions] == [
            ("income_above_upper_threshold", _D(0)),
            ("income_above_upper_threshold", _D(0)),
        ]

    def test_recovery_in_progress_is_recorded(self) -> None:
        """An installment recovery records the negative period amount."""
        plan = RecoveryPlan.create("trattamento_integrativo", _D(80), 8)
        tax = compute_tax(
            _D(50000), _RULES, withholding_schedule=_SCHEDULE, recovery_plan=plan
        )
        trattamento = tax.decisions[-1]
        assert trattamento.inputs["recovery_in_progress"] == "true"
        assert trattamento.inputs["period_amount"] == _D(-10)
        assert trattamento.amount == _D(0)

    def test_credits_not_in_force_take_no_decision(self) -> None:
        """Rules without the credits record no decision."""
        tax = compute_tax(_D(12000), make_year_rules(), withholding_schedule=_SCHEDULE)
        assert tax.decisions == ()

    def test_rule_version_falls_back_to_year(self) -> None:
        """Rules without a ruleset identity are versioned by their year."""
        rules = make_year_rules(ulteriore_detrazione=_UD_RAW, ruleset=None)
        (ulteriore,) = compute_tax(
            _D(25000), rules, withholding_schedule=_SCHEDULE
        ).decisions
        assert ulteriore.rule_version == "2026"
        assert ulteriore.reason_code == "full_amount"

    def test_resolve_tax_computation_matches(self) -> None:
        """resolve_tax_computation returns the same computation and plan."""
        tax = compute_tax(_D(12000), _RULES, withholding_schedule=_SCHEDULE)
        assert resolve_tax_computation(
            _D(12000), _RULES, withholding_schedule=_SCHEDULE
        ) == (tax.computation, tax.recovery_plan)
