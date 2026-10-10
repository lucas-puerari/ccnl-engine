"""IRPEF credit outcomes and the decisions the tax computation records."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.taxation.rules_irpef_credit import (
    CreditOutcome,
    trattamento_integrativo_outcome,
    ulteriore_detrazione_outcome,
)
from ccnl_engine.payroll.taxation.services_tax_computation import (
    compute_tax,
)
from ccnl_engine.payroll.withholding.models_recovery_plan import (
    InstallmentRun,
    RecoveryPlan,
)
from ccnl_engine.tax.annual.loaders import load_year_rules
from ccnl_engine.tax.income.models_credit import (
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from tests.unit.ccnl_engine.builders import make_year_rules

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
        # money(1 000 * 182 / 365) = money(498.6301...) = 498.63
        assert outcome == CreditOutcome(_D("498.63"), "full_amount")


class TestComputeTaxDecisions:
    """compute_tax records one decision per credit in force."""

    def test_low_income_decisions(self) -> None:
        """A low income gets the trattamento and no ulteriore detrazione."""
        tax = compute_tax(_D(12000), _RULES, remaining_slots=12)
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
        tax = compute_tax(_D(50000), _RULES, remaining_slots=12)
        assert [(d.reason_code, d.amount) for d in tax.decisions] == [
            ("income_above_upper_threshold", _D(0)),
            ("income_above_upper_threshold", _D(0)),
        ]

    def test_recovery_in_progress_is_recorded(self) -> None:
        """An installment recovery records the negative period amount."""
        plan = RecoveryPlan.create("trattamento_integrativo", _D(80), 8)
        tax = compute_tax(_D(50000), _RULES, remaining_slots=12, recovery_plan=plan)
        trattamento, recovery = tax.decisions[-2:]
        assert trattamento.inputs["recovery_in_progress"] == "true"
        assert trattamento.inputs["period_amount"] == _D(-10)
        assert trattamento.amount == _D(0)
        assert recovery.capability == "trattamento_integrativo_recovery"
        assert recovery.reason_code == "installment_posted"
        assert recovery.amount == _D(-10)
        assert recovery.inputs["residual_after"] == _D(70)

    def test_credits_not_in_force_take_no_decision(self) -> None:
        """Rules without the credits record no decision."""
        tax = compute_tax(_D(12000), make_year_rules(), remaining_slots=12)
        assert tax.decisions == ()

    def test_rule_version_falls_back_to_year(self) -> None:
        """Rules without a ruleset identity are versioned by their year."""
        rules = make_year_rules(ulteriore_detrazione=_UD_RAW, ruleset=None)
        (ulteriore,) = compute_tax(_D(25000), rules, remaining_slots=12).decisions
        assert ulteriore.rule_version == "2026"
        assert ulteriore.reason_code == "full_amount"


class TestTrattamentoRecovery:
    """The recovery of the trattamento integrativo (D.L. 3/2020 art. 1 c. 3).

    At 50,000 EUR nothing is due, so what was paid is an excess.
    """

    @pytest.mark.parametrize(
        ("paid", "run", "amount", "reason"),
        [
            # 40 EUR: recovered at once.
            ("40", InstallmentRun(), "-40", "overpayment_recovered"),
            # 200 EUR: first of eight installments of 25.
            ("200", InstallmentRun(), "-25", "overpayment_recovery_opened"),
            # 200 EUR on the last run of the employment: all of it.
            (
                "200",
                InstallmentRun(final=True),
                "-200",
                "overpayment_recovered_at_termination",
            ),
        ],
    )
    def test_excess_found_by_the_run(
        self, paid: str, run: InstallmentRun, amount: str, reason: str
    ) -> None:
        """The excess is recovered in full, or its first installment."""
        tax = compute_tax(
            _D(50000),
            _RULES,
            opening_tratt_ytd=_D(paid),
            remaining_slots=12,
            run=run,
        )
        recovery = tax.decisions[-1]
        assert recovery.capability == "trattamento_integrativo_recovery"
        assert recovery.reason_code == reason
        assert recovery.amount == _D(amount)
        assert tax.computation.trattamento_integrativo == _D(amount)

    def test_running_plan_is_settled_on_the_last_run(self) -> None:
        """80 EUR in eight installments of 10, none posted: 80 at once."""
        plan = RecoveryPlan.create("trattamento_integrativo", _D(80), 8)
        tax = compute_tax(
            _D(50000),
            _RULES,
            remaining_slots=12,
            recovery_plan=plan,
            run=InstallmentRun(final=True),
        )
        recovery = tax.decisions[-1]
        assert recovery.reason_code == "settled_at_termination"
        assert recovery.amount == _D(-80)
        assert tax.recovery_plan is None
