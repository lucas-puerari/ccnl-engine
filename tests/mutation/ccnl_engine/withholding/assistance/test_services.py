"""The payslips of a year settle the 730-4 statement of the worker.

Chimica D1 from January 2026; the statement is received on 20 June: the
July pay settles it first.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.run.models import RunKind
from ccnl_engine.withholding.assistance.inputs import (
    Form730Kind,
    Form730Line,
    Form730Settlement,
)

_HIRED = date(2026, 1, 1)
_ENGINE = PayrollEngine.bundled()
_K = Form730Kind


def _year(*statements: Form730Settlement) -> dict[int, PeriodResult]:
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_id="chimica-farmaceutica-federchimica",
                level_code="D1",
                contract_type=Permanent(),
                category=WorkerCategory.IMPIEGATO,
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                roles=frozenset(),
                sector=EmploymentSector.PRIVATE,
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=True,
                tax_returns=statements,
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), provincial_pay_element=False
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(30000)),
            default_facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="F205",
                family_composition=FamilyComposition(),
            ),
        )
    )
    return {
        r.period_id.month: r
        for r in year.period_results
        if r.run is not None and r.run.run_kind is RunKind.REGULAR
    }


def _form730(result: PeriodResult) -> list[tuple[str, str | None, Decimal]]:
    return sorted(
        (e.account.value, e.remittance_code, e.amount)
        for e in result.ledger_entries
        if e.entry_id.startswith("form730_")
    )


def _statement(installments: int = 1, **amounts: str) -> Form730Settlement:
    lines = tuple(Form730Line(_K(k), Decimal(v)) for k, v in amounts.items())
    return Form730Settlement(date(2026, 6, 20), lines, installments)


def test_july_refunds_and_withholds_on_the_codes_of_the_730() -> None:
    """A 300.00 IRPEF refund (1631) and an 80.00 regional debt (3803)."""
    plain = _year()
    months = _year(_statement(irpef_balance="-300.00", regional_surtax="80.00"))

    assert _form730(months[7]) == [
        (AccountKind.CREDITS.value, "1631", Decimal("300.00")),
        (AccountKind.SURTAX.value, "3803", Decimal("80.00")),
    ]
    assert months[7].period_net - plain[7].period_net == Decimal("220.00")
    assert not _form730(months[6])
    assert not _form730(months[8])
    (decision,) = (
        d for d in months[7].decisions if d.capability == "fiscal_adjustment"
    )
    assert decision.amount == Decimal("-220.00")


def test_installments_and_the_second_acconto_in_november() -> None:
    """300.00 balance in 3 (4731 with 1630 interest), 400.00 acconto in November."""
    months = _year(_statement(3, irpef_balance="300.00", irpef_second_advance="400.00"))

    assert _form730(months[7]) == [
        (AccountKind.ORDINARY_TAX.value, "4731", Decimal(100))
    ]
    assert _form730(months[8]) == [
        (AccountKind.ORDINARY_TAX.value, "1630", Decimal("0.33")),
        (AccountKind.ORDINARY_TAX.value, "4731", Decimal(100)),
    ]
    assert _form730(months[11]) == [
        (AccountKind.ORDINARY_TAX.value, "4730", Decimal("400.00"))
    ]


def test_a_debt_the_pay_cannot_cover_moves_to_the_next_pay() -> None:
    """A balance above the July pay: the rest in August with 0.4% interest."""
    months = _year(_statement(irpef_balance="99999.00"))

    july = sum((a for _, _, a in _form730(months[7])), Decimal(0))
    assert Decimal(0) < july < Decimal("99999.00")
    assert months[7].closing_state.cash.obligations.form730
    (carried,) = months[7].closing_state.cash.obligations.form730
    assert carried.month == 8
    assert carried.interest == (carried.amount * Decimal("0.004")).quantize(
        Decimal("0.01")
    )
    december = months[12]
    assert {i.code for i in december.issues} >= {"form730_debt_unrecovered"}
    assert not december.closing_state.cash.obligations.form730
