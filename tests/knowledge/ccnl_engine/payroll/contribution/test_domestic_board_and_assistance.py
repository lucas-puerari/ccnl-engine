"""Domestic payslips: Cas.Sa.Colf contribution and board and lodging in kind.

Sources, CCNL sulla disciplina del rapporto di lavoro domestico of 28
October 2025 (https://lavorodomestico.assindatcolf.it/wp-content/uploads/
2026/04/CCNL.pdf) and its Tabella minimi retributivi 2026:

- art. 54 c. 2: contributi di assistenza contrattuale of 0.06 EUR per paid
  hour, of which 0.02 charged to the worker (so 0.04 to the employer);
- art. 36 c. 3 and Tabella F: board and lodging of a convivente are valued
  at 2.33 + 2.33 + 2.00 = 6.66 EUR a day, a month being 30 days:
  6.66 x 30 = 199.80;
- art. 39 c. 1 and chiarimento a verbale 5: the tredicesima is the
  retribuzione globale di fatto, the indennità sostitutiva of board and
  lodging included;
- art. 41 c. 1: the TFR base is the pay of the year with the valore
  convenzionale of board and lodging, divided by 13.5.

Convivente level CS, Tabella A: 1,193.84 a month.  54 weekly hours and 216
contributable hours, the case of the Workledger payslip of 5 July 2026
(INPS 216 x 0.31 = 66.96, Cassa Colf 216 x 0.02 = 4.32, net 1,122.56).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    Permanent,
    WeeklyHours,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_CONVIVENTE = "lavoro-domestico-convivente.json"
_NON_CONVIVENTE = "lavoro-domestico-non-convivente.json"
_HOUSEHOLD = EmployerProfile(headcount=Headcount(1))
_ZERO = Decimal(0)


def _employment(slug: str = _CONVIVENTE, weekly: int = 54) -> Employment:
    return Employment(
        ccnl_slug=slug,
        level_code="CS",
        seniority=new_hire(),
        weekly_hours=WeeklyHours(weekly),
        full_time_weekly_hours=WeeklyHours(54 if slug == _CONVIVENTE else 40),
        contract_type=Permanent(),
    )


def _facts(hours: int) -> PeriodFacts:
    return PeriodFacts(contributable_hours=ContributableHours(Decimal(hours)))


def _run(
    run: PayrollRun, hours: int, employment: Employment | None = None
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(run.year, run.month, 20),
            employment=employment or _employment(),
            employer=_HOUSEHOLD,
            facts=_facts(hours),
        )
    )


def _account(result: PeriodResult, account: str) -> Decimal:
    return sum((e.amount for e in result.ledger_entries if e.account == account), _ZERO)


def _tfr(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.kind == "tfr_accrual_item"), _ZERO
    )


def test_regular_month_withholds_cassa_colf_and_pays_no_board_in_cash() -> None:
    """March 2026: gross 1,193.84, net 1,193.84 - 66.96 - 4.32 = 1,122.56.

    The employer pays 216 x 0.04 = 8.64 to the Cassa Colf.  The TFR quota
    counts board and lodging: (1,193.84 + 199.80) / 13.5 = 103.23.
    """
    result = _run(PayrollRun.regular(year=2026, month=3), 216)

    assert result.period_gross == Decimal("1193.84")
    assert _account(result, "bilateral_fund_employee") == Decimal("4.32")
    assert _account(result, "bilateral_fund_employer") == Decimal("8.64")
    assert result.period_net == Decimal("1122.56")
    assert _tfr(result) == Decimal("103.23")
    (decision,) = (
        d for d in result.decisions if d.capability == "assistance_contribution"
    )
    assert decision.inputs["hours"] == Decimal(216)
    assert decision.source is not None
    assert decision.source.section is not None
    assert "Art. 54 c. 2" in decision.source.section


def test_regular_month_reports_the_unpaid_board_substitute() -> None:
    """The cash substitute of days without board is an open limitation."""
    result = _run(PayrollRun.regular(year=2026, month=3), 216)

    ids = {limitation.id for limitation in result.assurance.limitations}
    assert "lavoro-domestico-convivente/board_lodging_substitute" in ids
    assert not result.is_payable


def test_non_convivente_reports_the_meal_indennity() -> None:
    """Art. 14 c. 8: the meal owed to a non convivente is not computed."""
    result = _run(
        PayrollRun.regular(year=2026, month=1),
        173,
        _employment(_NON_CONVIVENTE, 40),
    )

    ids = {limitation.id for limitation in result.assurance.limitations}
    assert ids >= {"lavoro-domestico-non-convivente/meal_indennity"}
    # 173 x 0.02 = 3.46 withheld, 173 x 0.04 = 6.92 paid by the employer.
    assert _account(result, "bilateral_fund_employee") == Decimal("3.46")
    assert _account(result, "bilateral_fund_employer") == Decimal("6.92")


def test_thirteenth_pays_board_and_lodging_in_cash() -> None:
    """Full-year tredicesima: 1,193.84 + 199.80 = 1,393.64.

    It is paid on no contributable hour, so no Cassa Colf is charged; its
    TFR quota is 1,393.64 / 13.5 = 103.23.
    """
    result = _run(PayrollRun.thirteenth(2026, 12), 0)

    allowances = {
        i.allowance_code: i.amount
        for i in result.pay_items
        if i.kind == "fixed_allowance_earning"
    }
    assert allowances == {"vitto_alloggio": Decimal("199.80")}
    assert result.period_gross == Decimal("1393.64")
    assert _account(result, "bilateral_fund_employee") == _ZERO
    assert _tfr(result) == Decimal("103.23")


def test_termination_ratei_include_board_and_lodging() -> None:
    """Employed January to June: the June run settles 6/12 of the tredicesima.

    6/12 of each component: 1,193.84 / 2 = 596.92 and 199.80 / 2 = 99.90,
    so the ratei pay 696.82.
    """
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug=_CONVIVENTE,
                level_code="CS",
                seniority=new_hire(),
                weekly_hours=WeeklyHours(54),
                full_time_weekly_hours=WeeklyHours(54),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 6, 30)),
            ),
            employer=_HOUSEHOLD,
            default_facts=_facts(216),
        )
    )

    ratei = [
        i.amount
        for r in year.period_results
        for i in r.pay_items
        if i.kind == "extra_month_earning"
    ]
    assert ratei == [Decimal("696.82")]
