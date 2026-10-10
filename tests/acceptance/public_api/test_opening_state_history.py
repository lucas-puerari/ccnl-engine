"""A run opens with the history of its employment, or it is not payable.

The progressive IRPEF of art. 23 DPR 600/1973 and the IVS massimale of
L. 335/1995 art. 2 c. 18 are computed on the totals of the year, and the
first run of a tax year withholds what the conguaglio of the year before
carried.  The zero state is the fact only for the first run of an
employment whose start is stated; any other run opened without its
history has a ``missing_fact opening_state`` blocker, and so has every run
that descends from it.  Scenario: the Concia D2 of
:mod:`tests.fixtures.explicit_facts`, every other fact explicit.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from ccnl_engine import PayrollEngine, PeriodResult
from ccnl_engine.inputs import EmploymentPeriod, PeriodState
from ccnl_engine.results import BlockerCode
from tests.fixtures.explicit_facts import CONCIA_D2, competence_year, regular_run
from tests.fixtures.opening_state import fresh_tax_year

_ENGINE = PayrollEngine.bundled()
#: The same worker, employed since 2020.
_SINCE_2020 = replace(CONCIA_D2, employment_period=EmploymentPeriod(date(2020, 1, 1)))


def _misses_history(result: PeriodResult) -> bool:
    return any(
        b.code is BlockerCode.MISSING_FACT and b.detail == "opening_state"
        for b in result.blockers
    )


def test_first_run_of_a_stated_hire_opens_with_the_zero_state() -> None:
    """January of a hire on 1 January: nothing came before it."""
    january = _ENGINE.calculate_period(regular_run(1, opening_state=PeriodState.zero()))

    assert not _misses_history(january)
    assert january.closing_state.history_known


def test_a_chain_from_a_run_without_its_history_keeps_blocking() -> None:
    """June from zero drops January to May; July chained from June too."""
    june = _ENGINE.calculate_period(regular_run(6, opening_state=PeriodState.zero()))
    july = _ENGINE.calculate_period(regular_run(7, opening_state=june.closing_state))

    assert _misses_history(june)
    assert _misses_history(july)
    assert not july.closing_state.history_known
    assert not july.is_payable


def test_january_of_an_earlier_employment_needs_the_year_before() -> None:
    """From zero, the carried surtax and recoveries of 2025 would be dropped."""
    from_zero = regular_run(1, employment=_SINCE_2020, opening_state=PeriodState.zero())
    imported = replace(from_zero, opening_state=fresh_tax_year(2026))

    assert _misses_history(_ENGINE.calculate_period(from_zero))
    assert not _misses_history(_ENGINE.calculate_period(imported))


def test_a_year_of_an_earlier_employment_opened_from_nothing_blocks_every_run() -> None:
    """Without an opening state, a plan of an employment begun earlier blocks."""
    plan = competence_year(employment=_SINCE_2020)

    unknown = _ENGINE.calculate_competence_year(plan).period_results
    stated = _ENGINE.calculate_competence_year(
        replace(plan, opening_state=fresh_tax_year(2026))
    ).period_results

    assert all(_misses_history(result) for result in unknown)
    assert not any(_misses_history(result) for result in stated)


def test_a_month_without_pay_tables_blocks_the_year_once() -> None:
    """Igiene Ambientale tables start in February 2026: January is left out.

    The year reports January once as not computed; the later runs do not
    each report it again as missing history.
    """
    employment = replace(
        CONCIA_D2,
        category=None,
        ccnl_slug="igiene-ambientale-utilitalia.json",
        level_code="D1",
    )
    year = _ENGINE.calculate_competence_year(competence_year(employment=employment))

    assert [str(u.payment.run_id) for u in year.uncovered_runs] == ["2026-01-regular"]
    assert not any(_misses_history(result) for result in year.period_results)
    assert {b.code for b in year.assurance.blockers} >= {BlockerCode.RUN_NOT_COMPUTED}
