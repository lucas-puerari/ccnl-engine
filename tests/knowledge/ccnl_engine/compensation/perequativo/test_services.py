"""Elemento perequativo of the CCNL metalmeccanici Federmeccanica.

CCNL of 5 February 2021, art. 13 (Sez. Quarta, Titolo IV): the workers in
force on 1 January of a company without second-level bargaining are paid
"con la retribuzione del mese di giugno, una cifra annua pari a" 485 euro
(from 2014), "onnicomprensiva e non incidente sul Tfr", "ovvero una cifra
inferiore fino a concorrenza in caso di presenza di retribuzioni aggiuntive
a quelle fissate dal CCNL, in funzione della durata [...] del rapporto di
lavoro nel corso dell'anno precedente"; "la frazione di mese superiore a 15
giorni" counts as a month, and a termination before June pays it "all'atto
della liquidazione delle competenze".

An impiegato C3 hired on 10 March 2025 has 10 months of 2025 (22 days of
March count): 485 x 10 / 12 = 404.1666 -> 404.17, less 150.00 of pay above
the CCNL: 254.17 on the June run of 2026.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment, PayrollRun, PeriodInput
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.pay_item.loaders import load_policy_resolver
from ccnl_engine.pay_item.policies import PolicyContext, TfrAxis
from scripts.provenance.rules import KNOWLEDGE_DIR
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import EMPLOYER, ENGINE

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult, PeriodResult
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_CCNL = "metalmeccanico-federmeccanica.json"
_PART_TIME = "metalmeccanico-federmeccanica/elemento_perequativo_part_time"
_HIRED = EmploymentPeriod(date(2025, 3, 10))
_ABOVE = Decimal(150)


def _employment(
    period: EmploymentPeriod | None = _HIRED, hours: int | None = None
) -> Employment:
    return Employment(
        ccnl_slug=_CCNL,
        level_code="C3",
        category=WorkerCategory.IMPIEGATO,
        seniority=new_hire(2025),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        employment_period=period,
        weekly_hours=None if hours is None else WeeklyHours(hours),
        full_time_weekly_hours=None if hours is None else WeeklyHours(40),
    )


def _run(
    month: int = 6,
    *,
    bargaining: bool | None = False,
    above: Decimal | None = _ABOVE,
    employment: Employment | None = None,
) -> PeriodResult:
    return ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=employment or _employment(),
            employer=replace(EMPLOYER, second_level_bargaining=bargaining),
            prior_year=PriorYearTaxFacts(
                employment_income=Decimal(30_000), pay_above_ccnl=above
            ),
        )
    )


def _paid(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.kind == "perequativo_element_earning"),
        Decimal(0),
    )


def _decisions(result: PeriodResult) -> list[CalculationDecision]:
    return [d for d in result.decisions if d.rule.endswith(":perequativo_element")]


def _codes(result: PeriodResult) -> set[str]:
    return {i.code for i in result.issues}


def test_june_pays_the_months_of_2025_less_the_pay_above() -> None:
    """10 months: 404.17 less 150.00 is 254.17, a final decision."""
    june = _run()
    assert _paid(june) == Decimal("254.17")
    (decision,) = [d for d in june.decisions if d.reason_code == "perequativo_paid"]
    assert decision.amount == Decimal("254.17")
    assert decision.inputs == {
        "months": "10",
        "annual": Decimal("485.00"),
        "prorated": Decimal("404.17"),
        "pay_above_ccnl": _ABOVE,
    }


def test_ordinary_pay_for_inps_and_irpef_outside_the_tfr() -> None:
    """The gross, INPS and taxable grow by it; the TFR base does not."""
    paid, owed_none = _run(), _run(bargaining=True)
    earnings, without = paid.closing_state.cash.earnings, owed_none.closing_state.cash
    assert paid.period_gross - owed_none.period_gross == Decimal("254.17")
    inps = earnings.inps_employee - without.earnings.inps_employee
    assert inps > 0
    assert earnings.taxable - without.earnings.taxable == Decimal("254.17") - inps

    def tfr_base(result: PeriodResult) -> object:
        (decision,) = [d for d in result.decisions if d.capability == "tfr"]
        return decision.inputs["base"]

    assert tfr_base(paid) == tfr_base(owed_none)


def _year(bargaining: bool) -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment(),
            employer=replace(EMPLOYER, second_level_bargaining=bargaining),
            prior_year=PriorYearTaxFacts(
                employment_income=Decimal(30_000), pay_above_ccnl=_ABOVE
            ),
            current_year=employment_only(),
        )
    )


def test_the_tredicesima_leaves_it_out() -> None:
    """The year pays it once, in June; the tredicesima is the same."""
    paid, without = _year(False), _year(True)

    def gross(year: CompetenceYearResult, kind: str, month: int) -> Decimal:
        (result,) = [
            r
            for r in year.period_results
            if r.run is not None
            and r.run.run_kind == kind
            and r.period_id.month == month
        ]
        return result.period_gross

    assert sum(_paid(r) for r in paid.period_results) == Decimal("254.17")
    assert gross(paid, "regular", 6) - gross(without, "regular", 6) == Decimal("254.17")
    assert gross(paid, "thirteenth", 12) == gross(without, "thirteenth", 12)


def test_a_termination_before_june_pays_it_on_the_last_run() -> None:
    """Ended on 15 March 2026, in force all 2025: 485.00 on the March run."""
    leaver = _employment(EmploymentPeriod(date(2020, 1, 1), date(2026, 3, 15)))
    march = _run(3, above=Decimal(0), employment=leaver)
    assert _paid(march) == Decimal("485.00")
    assert _paid(_run(2, above=Decimal(0), employment=leaver)) == 0


def test_unknown_bargaining_is_a_missing_fact_of_the_paying_run() -> None:
    """June leaves it out and names the fact; July has nothing to pay."""
    june, july = _run(bargaining=None), _run(7, bargaining=None)
    assert _paid(june) == 0
    assert not _decisions(june)
    (issue,) = [i for i in june.issues if i.code == "second_level_bargaining_unknown"]
    assert issue.fact == "second_level_bargaining"
    assert not june.is_payable
    assert "second_level_bargaining_unknown" not in _codes(july)


def test_second_level_bargaining_takes_it_away() -> None:
    """An employer with second-level bargaining pays none, without issue."""
    june = _run(bargaining=True, above=None)
    assert _paid(june) == 0
    assert not _decisions(june)
    assert {"second_level_bargaining_unknown", "pay_above_ccnl_unknown"}.isdisjoint(
        _codes(june)
    )


def test_unknown_pay_above_is_an_incomplete_issue() -> None:
    """Never taken as zero: the element is left out, provisional."""
    june = _run(above=None)
    assert _paid(june) == 0
    (issue,) = [i for i in june.issues if i.code == "pay_above_ccnl_unknown"]
    assert issue.fact == "pay_above_ccnl"
    (decision,) = _decisions(june)
    assert decision.reason_code == "required_fact_missing"
    assert decision.amount is None
    assert "pay_above_ccnl" not in decision.inputs


def test_pay_above_the_prorated_amount_absorbs_it() -> None:
    """500.00 above the CCNL absorbs 404.17: no earning, a zero decision."""
    june = _run(above=Decimal(500))
    assert _paid(june) == 0
    (decision,) = _decisions(june)
    assert decision.amount == 0


def test_a_hire_of_1_january_has_no_month_of_2025() -> None:
    """In force on 1 January 2026 with no month in 2025: nothing, no issue."""
    june = _run(
        bargaining=None, employment=_employment(EmploymentPeriod(date(2026, 1, 1)))
    )
    assert _paid(june) == 0
    assert "second_level_bargaining_unknown" not in _codes(june)


def test_an_unstated_employment_period_counts_twelve_months() -> None:
    """Without dates, the worker is taken as employed all 2025: 485.00."""
    june = _run(above=Decimal(0), employment=_employment(None))
    assert _paid(june) == Decimal("485.00")


def test_a_part_time_worker_is_paid_in_full_with_a_limitation() -> None:
    """20 of 40 hours: the full 254.17 and the part-time limitation."""
    part_time = _run(employment=_employment(hours=20))
    assert _paid(part_time) == Decimal("254.17")
    assert _PART_TIME in {limitation.id for limitation in part_time.limitations}
    assert _PART_TIME not in {limitation.id for limitation in _run().limitations}


def test_the_policy_agrees_with_every_clause_on_the_tfr() -> None:
    """Each CCNL with the clause states the TFR treatment of the policy."""
    resolution = load_policy_resolver().resolve(
        "perequativo_element_earning", PolicyContext(year=2026, as_of=date(2026, 6, 1))
    )
    assert resolution is not None
    clauses = [
        clause
        for path in sorted((KNOWLEDGE_DIR / "agreement").glob("*.json"))
        if (clause := load_ccnl(path.name).parameters.perequativo_element)
    ]
    assert clauses
    for clause in clauses:
        assert (resolution.tfr is TfrAxis.INCLUDED) is clause.tfr_relevant
