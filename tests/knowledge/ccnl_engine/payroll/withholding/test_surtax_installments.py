"""Surtax determined by the conguaglio and withheld by installments next year.

Commercio L4, resident in Sassari (Sardegna), employed since 2020 and
computed by the engine from January 2026, with no surtax imported from the
previous provider.  The expected amounts come from the independent oracle
:mod:`tests.knowledge.ccnl_engine.payroll.taxation.oracles_surtax_2026` on the annual
taxable
income each conguaglio reports; the IRPEF oracle confirms that net IRPEF
is due.

The 2027 tables are not bundled: 2027 runs use
``NextYearRepository``, the 2026
rules relabelled.  The oracle rates are the same in both years, so the
2027 figures check the mechanism, not the 2027 law.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache
from typing import TYPE_CHECKING

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
)
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    PeriodState,
    Permanent,
    SurtaxComponent,
)
from ccnl_engine.results import CalculationStatus
from tests.integration.ccnl_engine.payroll.year.builders_next_year_repository import (
    NextYearRepository,
)
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.state.builders_opening_state import (
    fresh_tax_year,
)
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)
from tests.knowledge.ccnl_engine.payroll.taxation.oracles_irpef_2026 import net_irpef
from tests.knowledge.ccnl_engine.payroll.taxation.oracles_surtax_2026 import (
    ADVANCE_MONTHS,
    BALANCE_MONTHS,
    installments,
    municipal_advance,
    municipal_sassari,
    regional_sardegna,
)
from tests.knowledge.ccnl_engine.payroll.termination.builders_tfr import no_tfr_fund

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult, PeriodResult

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine(repository=NextYearRepository())
_FACTS = PeriodFacts(regione="IT-88", comune_belfiore="I452")
_EMPLOYER = EmployerProfile(provincial_pay_element=False, headcount=Headcount(50))
_ZERO = Decimal(0)
_REGIONAL, _SALDO, _ACCONTO = "3802", "3848", "3847"


def _year(
    year: int, opening: PeriodState | None, ended_on: date | None
) -> CompetenceYearResult:
    employment = Employment(
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2020, 1, 1), ended_on),
        contract_type=Permanent(),
        pension_fund=NoPensionFund(),
        tfr_fund=no_tfr_fund(year),
        tfr_treasury_fund=False,
    )
    return _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=year,
            employment=employment,
            employer=_EMPLOYER,
            default_facts=_FACTS,
            opening_state=opening,
            current_year=employment_only(year),
        )
    )


@cache
def _year_2026() -> CompetenceYearResult:
    return _year(2026, fresh_tax_year(2026), None)


@cache
def _year_2027(ended_on: date | None = None) -> CompetenceYearResult:
    opening = _ENGINE.close_tax_year(_year_2026().period_results[-1].closing_state)
    return _year(2027, opening, ended_on)


def _run(result: PeriodResult) -> PayrollRun:
    run = result.run
    assert run is not None
    return run


def _taxable(result: PeriodResult) -> Decimal:
    """Return the annual taxable income the conguaglio decided on.

    Returns:
        The ``taxable_income`` input of the annual regional decision.
    """
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "addizionale_regionale" and "component" not in d.inputs
    )
    taxable = decision.inputs["taxable_income"]
    assert isinstance(taxable, Decimal)
    return taxable


def _oracle(result: PeriodResult) -> tuple[Decimal, Decimal]:
    """Return the oracle regional and municipal surtax of a conguaglio.

    Returns:
        ``(regional, municipal)`` on the taxable income of ``result``.
    """
    taxable = _taxable(result)
    irpef = net_irpef(taxable)
    assert irpef > 0
    return regional_sardegna(taxable, irpef), municipal_sassari(taxable, irpef)


def _by_code(result: PeriodResult) -> dict[str | None, Decimal]:
    """Return the surtax a run withholds, by codice tributo.

    Returns:
        Totals of the ``SURTAX`` entries by code, zero totals omitted.
    """
    totals: dict[str | None, Decimal] = {}
    for entry in result.ledger_entries:
        if entry.account == "surtax":
            code = entry.remittance_code
            totals[code] = totals.get(code, _ZERO) + entry.amount
    return totals


def _deferred(result: PeriodResult) -> dict[SurtaxComponent, tuple[Decimal, int]]:
    return {
        o.component: (o.plan.original_amount, o.plan.installments_total)
        for o in result.closing_state.cash.obligations.surtax
    }


def _saldi_2026() -> tuple[Decimal, Decimal, Decimal]:
    """Return the 2026 regional surtax, municipal saldo and 2027 acconto.

    Returns:
        The oracle amounts on the 2026 conguaglio.
    """
    regional, municipal = _oracle(_year_2026().period_results[-1])
    return regional, municipal, municipal_advance(municipal)


def test_first_year_withholds_no_surtax() -> None:
    """No surtax is withheld in the first year the engine computes.

    The surtax of 2026 is determined by the 2026 conguaglio and withheld in
    2027 (D.Lgs. 446/1997 art. 50 c. 4; D.Lgs. 360/1998 art. 1 c. 5).  The
    2025 surtax and the 2026 acconto were determined by the conguaglio of
    2025, which the engine did not run and nothing imports here: the law
    still requires them to be withheld in 2026, by the employer that
    certified them, so an integration must import them
    (``OpeningBalances.surtax_obligations``).
    """
    results = _year_2026().period_results

    assert [_by_code(r) for r in results] == [{}] * len(results)


def test_conguaglio_determines_the_saldi_and_the_next_acconto() -> None:
    """The 2026 conguaglio defers the saldi and the 2027 acconto.

    No acconto was withheld in 2026, so the municipal saldo is the whole
    municipal surtax; the acconto of 2027 is 30% of it, on 2026 income and
    rate.  The bundled municipal table holds the 2025 rates, so the result
    is provisional and names the missing table.  The conguaglio is the last
    payment of the year: the December run of the 28th, after the tredicesima
    paid on Christmas Eve (CCNL Terziario art. 220).
    """
    conguaglio = _year_2026().period_results[-1]
    regional, municipal, acconto = _saldi_2026()

    assert _run(conguaglio).run_kind == "regular"
    assert _deferred(conguaglio) == {
        SurtaxComponent.REGIONAL_BALANCE: (regional, 11),
        SurtaxComponent.MUNICIPAL_BALANCE: (municipal, 11),
        SurtaxComponent.MUNICIPAL_ADVANCE: (acconto, 9),
    }
    assert conguaglio.assurance.calculation is CalculationStatus.PROVISIONAL
    assert "municipal_surtax_prior_year_rates" in {i.code for i in conguaglio.issues}


def test_next_year_withholds_by_statutory_installments() -> None:
    """January to November the saldi, March to November the acconto.

    Only regular payslips take an installment: the quattordicesima, the
    December payslip and the tredicesima withhold none of the 2026 surtax.
    """
    regional, municipal, acconto = _saldi_2026()
    due = {
        _REGIONAL: installments(regional, BALANCE_MONTHS),
        _SALDO: installments(municipal, BALANCE_MONTHS),
        _ACCONTO: installments(acconto, ADVANCE_MONTHS),
    }
    results = _year_2027().period_results[:-1]

    for result in results:
        run = _run(result)
        month, regular = run.month, run.run_kind == "regular"
        expected = {
            code: split[month]
            for code, split in due.items()
            if regular and month in split
        }
        assert _by_code(result) == expected, run.run_id


def test_next_conguaglio_deducts_the_acconto_withheld() -> None:
    """The 2027 municipal saldo is the 2027 surtax less the 2027 acconto."""
    conguaglio = _year_2027().period_results[-1]
    _, _, acconto = _saldi_2026()
    regional, municipal = _oracle(conguaglio)

    assert conguaglio.closing_state.cash.tax.municipal_advance == acconto
    assert _deferred(conguaglio) == {
        SurtaxComponent.REGIONAL_BALANCE: (regional, 11),
        SurtaxComponent.MUNICIPAL_BALANCE: (municipal - acconto, 11),
        SurtaxComponent.MUNICIPAL_ADVANCE: (municipal_advance(municipal), 9),
    }


def test_termination_withholds_every_residual_at_once() -> None:
    """Ending on 31 August 2027: the last run withholds every residual.

    Art. 50 c. 4 and art. 1 c. 5: at the cessazione the residual surtax is
    withheld "in unica soluzione".  August takes the rest of the 2026
    saldi (four installments) and the 2027 surtax on the income paid, the
    municipal part net of the five acconto installments of March to July;
    no acconto of 2028 is determined (CU 2026 instructions, point 29).
    """
    results = _year_2027(date(2027, 8, 31)).period_results
    last = results[-1]
    regional_26, municipal_26, acconto = _saldi_2026()
    regional, municipal = _oracle(last)
    withheld_acconto = sum(
        installments(acconto, ADVANCE_MONTHS)[m] for m in range(3, 8)
    )
    before = {m: installments(regional_26, BALANCE_MONTHS)[m] for m in range(1, 8)}
    saldo_before = sum(
        installments(municipal_26, BALANCE_MONTHS)[m] for m in range(1, 8)
    )

    assert (_run(last).month, _run(last).run_kind) == (8, "regular")
    assert _by_code(last) == {
        _REGIONAL: regional_26 - sum(before.values()) + regional,
        _SALDO: municipal_26 - saldo_before + municipal - withheld_acconto,
    }
    assert last.closing_state.cash.obligations.surtax == ()


def test_termination_refunds_an_acconto_above_the_surtax_due() -> None:
    """Ending on 30 June 2027 below the Sassari threshold: acconto refunded.

    The 2027 taxable income paid is at most 15,000 EUR, so no municipal
    surtax is due; the four acconto installments of March to June are
    given back ("al netto ... di quanto eventualmente restituito", CU 2026
    instructions, point 26) on a ``SURTAX_REFUNDS`` line.
    """
    last = _year_2027(date(2027, 6, 30)).period_results[-1]
    _, _, acconto = _saldi_2026()
    withheld = sum(installments(acconto, ADVANCE_MONTHS)[m] for m in range(3, 7))

    assert municipal_sassari(_taxable(last), Decimal(1)) == _ZERO
    refunds = [e for e in last.ledger_entries if e.account == "surtax_refunds"]
    assert [e.amount for e in refunds] == [withheld]
    assert last.closing_state.cash.tax.municipal_advance == _ZERO
    assert last.closing_state.cash.obligations.surtax == ()


def test_capability_report_follows_the_surtax_decisions() -> None:
    """A provisional conguaglio is partial; an installment run is computed.

    The 2026 conguaglio applies the 2025 municipal rates, so the municipal
    surtax is a partial result against the registry; a 2027 run that only withholds
    installments reports no surtax gap.
    """
    conguaglio = _year_2026().period_results[-1]
    january = _year_2027().period_results[0]

    gaps = {g.feature: g.kind for g in conguaglio.capability_report.gaps}
    assert gaps.get("addizionale_comunale") == "partial_result"
    assert "addizionale_regionale" not in gaps
    assert not {g.feature for g in january.capability_report.gaps} & {
        "addizionale_regionale",
        "addizionale_comunale",
    }


_METALMECCANICO_C3 = "metalmeccanico-federmeccanica.json"
#: The December pay was posted by the regular run: the termination run pays
#: only its own items, here 60 overtime hours at 25.00 (1,500.00), enough
#: net pay for the surtax it withholds.
_TERMINATION_FACTS = PeriodFacts(
    regione="IT-88",
    comune_belfiore="I452",
    events=(
        OvertimeEvent(
            event_date=date(2026, 12, 30),
            hours=Decimal(60),
            hourly_rate=Decimal("25.00"),
        ),
    ),
)


def _termination_after(ended_on: date | None) -> tuple[PeriodResult, PeriodResult]:
    """Return the 2026 tredicesima and a termination run paid after it.

    Metalmeccanico C3 pays 13 runs, so a termination run on 31 December
    still takes a withholding slot after the tredicesima; it is a second
    conguaglio of 2026.

    Returns:
        The tredicesima and the termination run.
    """
    employment = Employment(
        ccnl_slug=_METALMECCANICO_C3,
        level_code="C3",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2020, 1, 1), ended_on),
        contract_type=Permanent(),
        pension_fund=NoPensionFund(),
    )
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026, employment=employment, employer=_EMPLOYER, default_facts=_FACTS
        )
    )
    thirteenth = year.period_results[-1]
    termination = _ENGINE.calculate_period(
        PeriodInput(
            # RunKind is not public: the constructor normalises its value.
            run=PayrollRun(run_kind="termination", month=12, year=2026),  # type: ignore[arg-type]
            payment_date=date(2026, 12, 31),
            employment=Employment(
                ccnl_slug=_METALMECCANICO_C3,
                level_code="C3",
                seniority=new_hire(),
                employment_period=EmploymentPeriod(
                    date(2020, 1, 1), date(2026, 12, 31)
                ),
                contract_type=Permanent(),
                pension_fund=NoPensionFund(),
            ),
            employer=_EMPLOYER,
            facts=_TERMINATION_FACTS,
            opening_state=thirteenth.closing_state,
        )
    )
    return thirteenth, termination


def test_second_conguaglio_withholds_only_the_difference() -> None:
    """The tredicesima already withheld the surtax: termination adds the rest.

    The employment ends on 31 December, so the tredicesima is a conguaglio
    of the last run and withholds the 2026 surtax at once; the termination
    run after it re-determines the surtax on the income including its own
    pay and withholds only the increase.
    """
    thirteenth, termination = _termination_after(date(2026, 12, 31))
    regional_1, municipal_1 = _oracle(thirteenth)
    regional_2, municipal_2 = _oracle(termination)

    assert _by_code(thirteenth) == {_REGIONAL: regional_1, _SALDO: municipal_1}
    assert _by_code(termination) == {
        _REGIONAL: regional_2 - regional_1,
        _SALDO: municipal_2 - municipal_1,
    }
    assert termination.closing_state.cash.obligations.surtax == ()


def test_termination_after_an_ordinary_conguaglio_replaces_its_deferral() -> None:
    """The deferred 2026 surtax is withheld at once when the employment ends.

    The tredicesima ran as an ordinary conguaglio and deferred the 2026
    surtax to 2027; the termination run that follows in December ends the
    employment, so it drops the deferral and withholds the whole surtax on
    the final income (art. 50 c. 4, art. 1 c. 5).
    """
    thirteenth, termination = _termination_after(None)
    regional, municipal = _oracle(termination)

    assert len(thirteenth.closing_state.cash.obligations.surtax) == 3
    assert _by_code(termination) == {_REGIONAL: regional, _SALDO: municipal}
    assert termination.closing_state.cash.obligations.surtax == ()
