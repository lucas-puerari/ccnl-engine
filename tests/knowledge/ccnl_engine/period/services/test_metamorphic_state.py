"""Metamorphic properties of the state of a year, on every production CCNL.

- the totals of every payment are the sums of its postings;
- a year exported at June and imported back resumes as the year in one
  pass, up to the settlement of an employment that ends in September, and
  the state the end closes reads back from JSON;
- the year plan and the same runs chained one by one, each opening with the
  state the run before closed, pay the same;
- a fact the run needs, left unknown, blocks the feature it decides: an
  unknown is never read as zero, so no total built on it is payable.
"""

from __future__ import annotations

from dataclasses import replace
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
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    OpeningBalances,
    PaymentId,
    PeriodState,
    Permanent,
    PriorYearTaxFacts,
    period_state_from_json,
    period_state_to_json,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

pytestmark = pytest.mark.legal_scenario

_D = Decimal
_ENGINE = PayrollEngine.bundled()
_OPERATIONAL = PayrollEngine.bundled(mode="operational")
_PRODUCTION = {
    "commercio-confcommercio": "4",
    "metalmeccanico-federmeccanica": "C3",
    "edilizia-ance-impiegati": "4",
    "pubblici-esercizi-fipe-angem-ristorazione-collettiva": "4",
}
_CCNLS = sorted(_PRODUCTION)
_FACTS = PeriodFacts(regione="IT-25", comune_belfiore="A005")
_PRIOR = PriorYearTaxFacts(employment_income=_D(40000))
_EMPLOYER = EmployerProfile(headcount=Headcount(20))


_ENDED = date(2026, 9, 30)


def _employment(ccnl: str, ended_on: date | None = None) -> Employment:
    return Employment(
        ccnl_id=ccnl,
        level_code=_PRODUCTION[ccnl],
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2026, 1, 1), ended_on),
        contract_type=Permanent(),
    )


def _year(
    ccnl: str, opening: PeriodState | None = None, ended_on: date | None = None
) -> CompetenceYearResult:
    return _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment(ccnl, ended_on),
            employer=_EMPLOYER,
            default_facts=_FACTS,
            prior_year=_PRIOR,
            opening_state=opening,
        )
    )


@cache
def _one_pass(ccnl: str) -> CompetenceYearResult:
    return _year(ccnl)


def _by_account(result: PeriodResult) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for entry in result.ledger_entries:
        totals[entry.account.value] = totals.get(entry.account.value, _D(0)) + (
            entry.amount
        )
    return totals


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_the_totals_of_every_payment_are_the_sums_of_its_postings(ccnl: str) -> None:
    """Gross, net, employer cost and remittances of each 2026 payment."""
    for result in _one_pass(ccnl).period_results:
        ledger = _by_account(result)

        def total(*accounts: str, ledger: dict[str, Decimal] = ledger) -> Decimal:
            return sum((ledger.get(a, _D(0)) for a in accounts), _D(0))

        gross = total("cash_earnings")
        assert result.period_gross == gross, result.run
        assert result.period_net == gross - total(
            "employee_contributions", "ordinary_tax", "surtax"
        ) - total("pension_fund_employee", "bilateral_fund_employee"), result.run
        remitted = sum((line.amount for line in result.remittance_summary()), _D(0))
        assert remitted == total("ordinary_tax", "surtax"), result.run


def _exported(state: PeriodState) -> OpeningBalances:
    cash = state.cash
    return OpeningBalances(
        tax_year=2026,
        payments=cash.payments,
        inps_bases=state.accrual.inps_bases,
        gross=cash.earnings.gross,
        taxable=cash.earnings.taxable,
        inps_employee=cash.earnings.inps_employee,
        irpef_withheld=cash.tax.irpef,
        trattamento_recognized=cash.trattamento.recognized,
        trattamento_recovered=cash.trattamento.recovered,
        trattamento_due=cash.trattamento.due,
        trattamento_reason=cash.trattamento.reason,
        somma_esente_recognized=cash.somma_esente.recognized,
        somma_esente_recovered=cash.somma_esente.recovered,
        somma_esente_due=cash.somma_esente.due,
        somma_esente_reason=cash.somma_esente.reason,
        ulteriore_recognized=cash.ulteriore_detrazione.recognized,
        ulteriore_recovered=cash.ulteriore_detrazione.recovered,
        ulteriore_due=cash.ulteriore_detrazione.due,
        ulteriore_reason=cash.ulteriore_detrazione.reason,
        recoveries=(),
        surtax_obligations=(),
        employment_spells=cash.employment_spells,
        tfr_quotas=state.accrual.tfr_quotas,
        leave_balances=state.accrual.leave.balances,
    )


def _june_index(year: CompetenceYearResult) -> int:
    return next(
        i
        for i, r in enumerate(year.period_results)
        if r.run is not None and (r.run.month, r.run.run_kind.value) == (6, "regular")
    )


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_a_year_resumed_from_an_exported_june_pays_as_one_pass(ccnl: str) -> None:
    """Export the state June closed with, import it, run July onwards."""
    one = _one_pass(ccnl)
    june = _june_index(one)
    imported = _ENGINE.import_opening_balances(
        _exported(one.period_results[june].closing_state)
    )
    resumed = _year(ccnl, imported)

    tail = list(one.period_results[june + 1 :])
    assert [r.period_net for r in resumed.period_results[-len(tail) :]] == [
        r.period_net for r in tail
    ]


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_an_end_resumed_from_an_exported_june_settles_as_one_pass(ccnl: str) -> None:
    """Leave, extra months and TFR the end pays: imported or accrued, the same."""
    one = _year(ccnl, ended_on=_ENDED)
    june = _june_index(one)
    imported = _ENGINE.import_opening_balances(
        _exported(one.period_results[june].closing_state)
    )
    end, resumed = (
        one.period_results[-1],
        _year(ccnl, imported, _ENDED).period_results[-1],
    )

    assert end.run is not None
    assert (end.run.month, end.run.run_kind.value) == (9, "regular")
    assert "termination_residual_leave" in {d.capability for d in end.decisions}
    assert _by_account(resumed) == _by_account(end)
    closed, reopened = end.closing_state.accrual, resumed.closing_state.accrual
    assert (reopened.tfr_quotas, reopened.leave) == (closed.tfr_quotas, closed.leave)


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_the_state_an_end_closes_reads_back_from_json_with_nothing_left(
    ccnl: str,
) -> None:
    """A leave balance is closed only when paid; the TFR quota of the year is kept."""
    end = _year(ccnl, ended_on=_ENDED).period_results[-1]
    state = end.closing_state
    leave = next(
        d for d in end.decisions if d.capability == "termination_residual_leave"
    )

    assert period_state_from_json(period_state_to_json(state)) == state
    assert state.accrual.leave.known
    for balance in state.accrual.leave.balances:
        assert balance.settled is (leave.amount is not None), balance
    assert [q.year for q in state.accrual.tfr_quotas] == [2026]


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_the_year_plan_pays_what_its_runs_chained_one_by_one_pay(ccnl: str) -> None:
    """Each run of the plan, computed alone on the state the run before closed."""
    one = _one_pass(ccnl)
    state = PeriodState.zero()
    chained = []
    payments = [
        PaymentId(r.run.identifier, r.payment_date)
        for r in one.period_results
        if r.run is not None
    ]
    for index, result in enumerate(one.period_results):
        assert result.run is not None
        single = _ENGINE.calculate_period(
            PeriodInput(
                run=result.run,
                payment_date=result.payment_date,
                employment=_employment(ccnl),
                employer=_EMPLOYER,
                facts=_FACTS,
                prior_year=_PRIOR,
                opening_state=state,
                planned_payments=tuple(payments[index + 1 :]),
            )
        )
        chained.append(single)
        state = single.closing_state

    assert [r.period_net for r in chained] == [r.period_net for r in one.period_results]
    assert chained[-1].closing_state == one.period_results[-1].closing_state


def _january(
    ccnl: str,
    *,
    employment: Employment | None = None,
    facts: PeriodFacts = _FACTS,
) -> PeriodResult:
    return _OPERATIONAL.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 27),
            employment=employment or _employment(ccnl),
            employer=_EMPLOYER,
            facts=facts,
            prior_year=_PRIOR,
        )
    )


def _blocked(result: PeriodResult) -> set[str | None]:
    return {b.feature for b in result.blockers}


@pytest.mark.parametrize("ccnl", _CCNLS)
def test_an_unknown_fact_blocks_the_feature_it_decides(ccnl: str) -> None:
    """Unknown seniority or residence is never read as zero or as none."""
    known = _january(ccnl)
    seniority = _january(ccnl, employment=replace(_employment(ccnl), seniority=None))
    residence = _january(ccnl, facts=PeriodFacts())

    assert "seniority" not in _blocked(known)
    assert "seniority" in _blocked(seniority)
    assert not seniority.is_payable
    assert {"addizionale_regionale", "addizionale_comunale"} <= _blocked(residence)
    assert not residence.is_payable
