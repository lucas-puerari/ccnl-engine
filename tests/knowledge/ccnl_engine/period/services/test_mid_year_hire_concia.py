"""A Concia D2 hired on 1 July 2026: credits and conguaglio against an oracle.

The full-year payslip of :mod:`test_full_payslip_concia` earns too much for
any credit.  Hired on 1 July, the same worker has six months and a
tredicesima of six twelfths, an income below 15,000 EUR and a year of 184
days: the IRPEF deduction is proportioned to the days, and the trattamento
integrativo (D.L. 3/2020 art. 1) and the somma esente (L. 207/2024 art. 1
cc. 4-5) are both due.  The expected figures come from
:data:`~tests.knowledge.ccnl_engine.period.oracles.CONCIA_D2_JULY_HIRE_2026`,
computed from the statutes without the engine; the case combines the taxable
income, the employee contributions, the IRPEF, the credits and the
conguaglio that settles them.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    PeriodResult,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SurtaxComponent,
    WorkerCategory,
)
from tests.knowledge.ccnl_engine.period.oracles import (
    CONCIA_D2_JULY_HIRE_2026 as ORACLE,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_ZERO = Decimal(0)
_HIRED_ON = date(2026, 7, 1)


@cache
def _year() -> CompetenceYearResult:
    return _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug="concia-unic.json",
                level_code="D2",
                category=WorkerCategory.OPERAIO,
                seniority=new_hire(),
                employment_period=EmploymentPeriod(_HIRED_ON),
                tfr_treasury_fund=False,
                pension_fund=NoPensionFund(),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            default_facts=PeriodFacts(
                regione="IT-88",
                comune_belfiore="A192",
                family_composition=FamilyComposition(),
            ),
            # Above the 33,000 EUR of L. 199/2025 art. 1 c. 7: the renewal
            # regime stays out of the case, as in the full-year scenario.
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40_000)),
            current_year=CurrentYearTaxFacts.employment_only(2026, _HIRED_ON),
        )
    )


def _runs() -> tuple[PeriodResult, ...]:
    return _year().period_results


def _posted(result: PeriodResult, account: str) -> Decimal:
    return sum((e.amount for e in result.ledger_entries if e.account == account), _ZERO)


def _year_total(account: str) -> Decimal:
    return sum((_posted(r, account) for r in _runs()), _ZERO)


def test_the_year_has_six_months_and_a_partial_tredicesima() -> None:
    """July to December and the tredicesima of six twelfths."""
    runs = _runs()

    assert len(runs) == ORACLE.payments
    assert [r.period_gross for r in runs[:-1]] == [ORACLE.monthly_gross] * 6
    assert runs[-1].period_gross == ORACLE.thirteenth_gross


def test_employee_contributions_of_each_payment() -> None:
    """IVS 9.19% and CIGS 0.30% of the whole-euro base of each payment."""
    inps = [_posted(r, "employee_contributions") for r in _runs()]

    assert inps == [ORACLE.monthly_inps] * 6 + [ORACLE.thirteenth_inps]


def test_taxable_income_of_the_year() -> None:
    """Gross less employee INPS, as the closing state holds it."""
    earnings = _runs()[-1].closing_state.cash.earnings

    assert (earnings.gross, earnings.inps_employee, earnings.taxable) == (
        ORACLE.gross,
        ORACLE.inps,
        ORACLE.taxable,
    )


def test_irpef_of_the_year_takes_the_deduction_of_184_days() -> None:
    """The withheld IRPEF is the net IRPEF of the oracle for 184 days."""
    assert _year_total("ordinary_tax") == ORACLE.irpef
    assert _runs()[-1].closing_state.cash.tax.irpef == ORACLE.irpef


def test_the_conguaglio_recognises_both_credits() -> None:
    """Trattamento integrativo and somma esente of the year are the oracle's."""
    cash = _runs()[-1].closing_state.cash

    assert cash.trattamento.recognized == ORACLE.trattamento
    assert cash.somma_esente.recognized == ORACLE.somma_esente
    assert _year_total("credits") == ORACLE.trattamento + ORACLE.somma_esente


def test_net_pay_of_the_year_includes_the_credits() -> None:
    """Gross less INPS less IRPEF plus the two credits."""
    assert sum((r.period_net for r in _runs()), _ZERO) == ORACLE.net


@pytest.mark.parametrize(
    ("component", "amount"),
    [
        (SurtaxComponent.REGIONAL_BALANCE, ORACLE.regional),
        (SurtaxComponent.MUNICIPAL_BALANCE, ORACLE.municipal),
    ],
)
def test_surtax_left_for_2027(component: SurtaxComponent, amount: Decimal) -> None:
    """The conguaglio determines the 2026 surtaxes on the taxable income."""
    (obligation,) = (
        o
        for o in _runs()[-1].closing_state.cash.obligations.surtax
        if o.component is component
    )

    assert obligation.plan.original_amount == amount


def test_every_run_is_payable() -> None:
    """Nothing the case reads blocks it in simulation mode."""
    assert all(r.is_payable for r in _runs())
