"""Deductions the trattamento integrativo compares with the gross tax.

D.L. 3/2020 art. 1 c. 1, second and third periods (Normattiva, in force on
6 October 2026,
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2020-02-05;3~art1!vig=2026-10-06):
above 15,000 and up to 28,000 EUR the credit is due "a
condizione che la somma delle detrazioni di cui agli articoli 12 e 13, comma
1, [...] sia di ammontare superiore all'imposta lorda", and equals "la
differenza tra la somma delle detrazioni ivi elencate e l'imposta lorda",
"comunque non superiore a 1.200 euro".  The ulteriore detrazione of L.
207/2024 art. 1 c. 6 is not in the list.

Reddito complessivo 20,000 EUR, full year 2026:

- imposta lorda (art. 11 TUIR, 23% up to 28,000): 20,000 x 0.23 = 4,600.00;
- art. 13 c. 1 lett. b TUIR (Normattiva, in force on 6 October 2026,
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art13!vig=2026-10-06):
  1,910 + 1,190 x (28,000 - 20,000) / 13,000,
  the ratio truncated to 0.6153 (c. 6): 1,910 + 732.21 = 2,642.21.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun, RecoveryPlan
from ccnl_engine.payroll.service.irpef_credits import CreditOutcome
from ccnl_engine.payroll.service.irpef_net import NetIrpef
from ccnl_engine.payroll.service.trattamento_credit import resolve_trattamento
from ccnl_engine.tax.domain.credit_rules import TrattamentoIntegrativoRules
from tests.helpers import make_year_rules

_D = Decimal
_INCOME = _D(20_000)
_GROSS = _D("4600.00")
_ART13 = _D("2642.21")
_RULES = make_year_rules().model_copy(
    update={
        "trattamento_integrativo": TrattamentoIntegrativoRules(
            threshold_mid=_D(15_000), threshold_upper=_D(28_000), max_amount=_D(1200)
        )
    }
)


def _annual(family: Decimal, ulteriore: Decimal) -> NetIrpef:
    return NetIrpef(
        gross=_GROSS,
        work_deduction=_ART13,
        family_deductions=family,
        ulteriore=CreditOutcome(ulteriore, "full_amount"),
    )


@pytest.mark.parametrize(
    ("family", "ulteriore", "expected", "reason"),
    [
        # 2,642.21 alone does not exceed 4,600.00.
        (_D(0), _D(0), _D("0.00"), "deductions_not_above_irpef"),
        # 2,642.21 + 2,500.00 - 4,600.00 = 542.21.
        (_D(2500), _D(0), _D("542.21"), "deductions_above_irpef"),
        # 2,642.21 + 3,500.00 - 4,600.00 = 1,542.21, capped at 1,200.
        (_D(3500), _D(0), _D("1200.00"), "deductions_above_irpef"),
        # 2,642.21 + 1,500.00 = 4,142.21 <= 4,600.00: the 1,000 ulteriore
        # detrazione, not in the list, does not make the credit due.
        (_D(1500), _D(1000), _D("0.00"), "deductions_not_above_irpef"),
    ],
)
def test_family_deductions_enter_the_sum_and_ulteriore_does_not(
    family: Decimal, ulteriore: Decimal, expected: Decimal, reason: str
) -> None:
    """The annual credit is art. 12 + art. 13 c. 1 less the gross tax."""
    _, _, _, decisions = resolve_trattamento(
        _INCOME, _annual(family, ulteriore), _RULES, _D(0), 12, run=InstallmentRun()
    )
    decision = decisions[0]

    assert decision.amount == expected
    assert decision.reason_code == reason
    assert decision.inputs["relevant_deductions"] == _ART13 + family


def test_component_carries_the_annual_credit_only_when_due() -> None:
    """A credit of 542.21 is traced; no credit leaves no component."""
    _, due, _, decisions = resolve_trattamento(
        _INCOME, _annual(_D(2500), _D(0)), _RULES, _D(0), 12, run=InstallmentRun()
    )
    _, none, _, _ = resolve_trattamento(
        _INCOME, _annual(_D(0), _D(0)), _RULES, _D(0), 12, run=InstallmentRun()
    )

    assert due is not None
    assert due.amount == _D("542.21")
    assert due.rule_id
    assert none is None
    assert decisions[0].inputs["taxable_income"] == _INCOME


def test_a_plan_in_force_takes_its_installment_not_the_balance() -> None:
    """A recovery of 240.00 in eight installments posts 30.00 on the run.

    The annual credit due (542.21) would otherwise be paid over the slots:
    the plan in force decides the run, not the balance (D.L. 3/2020 art. 1
    c. 3, eight installments above 60 EUR).
    """
    plan = RecoveryPlan(
        kind="trattamento_integrativo",
        original_amount=_D("240.00"),
        installment_amount=_D("30.00"),
        installments_total=8,
        installments_posted=2,
    )
    period, _, next_plan, decisions = resolve_trattamento(
        _INCOME,
        _annual(_D(2500), _D(0)),
        _RULES,
        _D(0),
        12,
        plan,
        run=InstallmentRun(),
    )

    assert period == _D("-30.00")
    assert next_plan is not None
    assert next_plan.installments_posted == 3
    assert decisions[0].inputs["recovery_in_progress"] == "true"


def test_the_credit_up_to_15000_follows_the_days_of_the_year() -> None:
    """Up to 15,000 EUR the 1,200 EUR are rapportati al periodo di lavoro.

    D.L. 3/2020 art. 1 c. 1, first period: income 10,000, gross tax
    10,000 x 0.23 = 2,300.00 above the art. 13 deduction less 75: the
    credit is due in full over a year and in proportion over half of it.
    """
    annual = NetIrpef(
        gross=_D("2300.00"),
        work_deduction=_D("1955.00"),
        family_deductions=_D(0),
        ulteriore=CreditOutcome(_D(0), "full_amount"),
    )
    full = resolve_trattamento(
        _D(10_000), annual, _RULES, _D(0), 1, run=InstallmentRun()
    )[3][0].amount
    half = resolve_trattamento(
        _D(10_000), annual, _RULES, _D(0), 1, None, 182, run=InstallmentRun()
    )[3][0].amount

    assert full == _D("1200.00")
    assert half is not None
    assert _D(0) < half < _D("1200.00")
