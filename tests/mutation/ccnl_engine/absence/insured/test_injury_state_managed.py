"""A work injury of an employee of the State insured per conto dello Stato.

INAIL pays no temporary indemnity to them: the employer pays the whole
pay of the days of the inability, the waiting days included.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.models import InjuryRules
from ccnl_engine.absence.insured.rules import MonthPay, injury_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance
from ccnl_engine.sickness.term.rules import DailyQuota

_PAY = MonthPay(
    chain=MonthlyPayChain(base=Decimal(3000), seniority=Decimal(0), allowances=()),
    quota=DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
    extra_months=1,
    employee_rate=Decimal("0.0919"),
)


def _rules(*, insured: bool) -> InjuryRules:
    return InjuryRules(
        carenza_rate=Decimal(1),
        integration_rate=Decimal(1),
        inail_indemnity=insured,
        provenance=RuleProvenance(status=ProvenanceStatus.MISSING),
    )


def _paid(*, insured: bool) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    paid = injury_pay(
        date(2026, 1, 1),
        date(2026, 1, 31),
        date(2026, 1, 1),
        _PAY,
        Decimal(156),
        Decimal(36),
        load_insured_absence_rates().injury,
        _rules(insured=insured),
    )
    return paid.deduction, paid.carenza, paid.indemnity, paid.integration


def test_the_employer_pays_the_whole_month_without_inail() -> None:
    """2,900 deducted (29 days of 100): 300 of waiting days, 2,600 paid back."""
    deduction, carenza, indemnity, integration = _paid(insured=False)

    assert (deduction, carenza, indemnity, integration) == (
        Decimal("2900.00"),
        Decimal("300.00"),
        Decimal(0),
        Decimal("2600.00"),
    )


def test_an_insured_worker_takes_the_inail_share() -> None:
    """The same rules with INAIL: the indemnity takes a share of the 2,600."""
    _, _, indemnity, integration = _paid(insured=True)

    assert (indemnity, integration) == (Decimal("1869.23"), Decimal("730.77"))
