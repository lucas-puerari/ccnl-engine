"""The validity window of each contract predicts which runs of 2026 compute.

A scan of the whole bundle: every CCNL, each month of 2026 and each level at
least once.  A run whose competence date the window of
:attr:`ContractSummary.validity` covers must compute; a run outside it may
compute (it reads no rule outside the window) or raise
:class:`~ccnl_engine.MissingRuleError` on a date outside the window.  No
other outcome is admitted.  The amounts are not checked here.

The worker is employed with 36 months of seniority, so the runs read the
seniority series too, and with the category that prices them where the
level needs one.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    MissingRuleError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.inputs import (
    ContributableHours,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from tests.fixtures.seniority import pricing_category

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.catalog import ContractSummary, ValidityWindow
    from ccnl_engine.contract.domain.identity import CCNL

_ENGINE = PayrollEngine.bundled()
_YEAR = 2026
_CONTRACTS = {str(c.ccnl_id): c for c in PayrollEngine.list_contracts()}
_DOMESTIC = frozenset({
    "lavoro-domestico-convivente",
    "lavoro-domestico-non-convivente",
})
_SENIORITY = SeniorityFact(36, date(_YEAR, 1, 1), SenioritySource.PAYSLIP)
#: First day of the base salary of every level in the bundle file of the
#: CCNLs whose 2026 pay tables start after January: the first tranche the
#: bundle holds, with no earlier table.  The dates are those of the sources
#: cited by each file, not checked here against a signed text:
#: - anas: CCNL 2025-2027 signed 18 December 2025, "Tabella retributiva",
#:   tranches from 1 March 2026 (https://www.stradeanas.it/sites/default/
#:   files/Azienda/Lavora_con_noi/CCNL-2025-2027.pdf);
#: - igiene-ambientale-utilitalia: renewal of 9 December 2025, the new
#:   16-level classification in force from 1 February 2026
#:   (https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=551);
#: - lavanderie-industriali-assosistema: tranche of 1 May 2026
#:   (https://www.assosistema.it/11527-2/);
#: - metalmeccanico-confimi-pmi: table "Categoria 2 - 01/06/2026"
#:   (https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=445).
_LATE_TABLES = {
    "anas": date(_YEAR, 3, 1),
    "igiene-ambientale-utilitalia": date(_YEAR, 2, 1),
    "lavanderie-industriali-assosistema": date(_YEAR, 5, 1),
    "metalmeccanico-confimi-pmi": date(_YEAR, 6, 1),
}


def _employment(ccnl: CCNL, level_code: str) -> Employment:
    domestic = ccnl.meta.ccnl_id in _DOMESTIC
    return Employment(
        ccnl_slug=f"{ccnl.meta.ccnl_id}.json",
        level_code=level_code,
        weekly_hours=WeeklyHours(25) if domestic else None,
        seniority=_SENIORITY,
        category=pricing_category(ccnl.parameters.seniority_increments, level_code),
    )


def _facts(ccnl: CCNL) -> PeriodFacts:
    if ccnl.meta.ccnl_id in _DOMESTIC:
        return PeriodFacts(contributable_hours=ContributableHours(Decimal(108)))
    return PeriodFacts()


def _runs(ccnl: CCNL) -> Iterator[tuple[str, int]]:
    """Yield ``(level, month)``: every month, every level at least once.

    Yields:
        The level of month ``m`` rotates over the levels; the levels past the
        twelfth run in the month of their position.
    """
    codes = [level.code for level in ccnl.levels]
    for month in range(1, 13):
        yield codes[(month - 1) % len(codes)], month
    for index, code in enumerate(codes[12:], start=12):
        yield code, index % 12 + 1


def _outcome(ccnl: CCNL, level_code: str, month: int) -> MissingRuleError | None:
    """Return the missing rule of the run, ``None`` when it computed.

    Returns:
        The error of a run that misses a rule of the bundle.
    """
    request = PeriodInput(
        run=PayrollRun.regular(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 27),
        employment=_employment(ccnl, level_code),
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=_facts(ccnl),
    )
    try:
        _ENGINE.calculate_period(request)
    except MissingRuleError as error:
        return error
    return None


def _window(summary: ContractSummary) -> ValidityWindow:
    assert summary.validity is not None, summary.ccnl_id
    return summary.validity


@pytest.mark.parametrize("ccnl_id", sorted(_CONTRACTS))
def test_the_window_predicts_every_run_of_the_year(ccnl_id: str) -> None:
    """Inside the window a run computes; outside it may miss a rule."""
    window = _window(_CONTRACTS[ccnl_id])
    ccnl = load_ccnl(f"{ccnl_id}.json")
    wrong: list[str] = []
    for level_code, month in _runs(ccnl):
        competence = date(_YEAR, month, 1)
        error = _outcome(ccnl, level_code, month)
        if error is None:
            continue
        if window.covers(competence) or window.covers(error.as_of):
            wrong.append(f"{level_code}/{month}: {error}")
    assert wrong == []


def test_only_the_contracts_with_a_late_window_miss_a_rule_in_2026() -> None:
    """A window from 1 January 2026 or earlier covers every run of 2026."""
    late = {
        c for c, s in _CONTRACTS.items() if _window(s).first_day > date(_YEAR, 1, 1)
    }
    assert set(_LATE_TABLES) <= late
    for ccnl_id, first_day in _LATE_TABLES.items():
        assert _window(_CONTRACTS[ccnl_id]).first_day == first_day


@pytest.mark.parametrize(("ccnl_id", "first_day"), sorted(_LATE_TABLES.items()))
def test_a_competence_year_leaves_out_the_months_before_the_tables(
    ccnl_id: str, first_day: date
) -> None:
    """The months the window does not cover are listed, the others computed."""
    ccnl = load_ccnl(f"{ccnl_id}.json")
    plan = CompetenceYearPlan(
        year=_YEAR,
        employment=_employment(ccnl, ccnl.levels[0].code),
        employer=EmployerProfile(headcount=Headcount(50)),
    )
    result = _ENGINE.calculate_competence_year(plan)

    left_out = [u.payment.competence for u in result.uncovered_runs]
    assert left_out == [date(_YEAR, m, 1) for m in range(1, first_day.month)]
    assert not any(_window(_CONTRACTS[ccnl_id]).covers(d) for d in left_out)
    assert all(r.period_id.month >= first_day.month for r in result.period_results)
    assert not result.is_payable
    assert sum(b.code == "run_not_computed" for b in result.blockers) == len(left_out)
