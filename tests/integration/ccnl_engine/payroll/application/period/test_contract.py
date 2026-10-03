"""The INPS rules of a run are those of its competence year."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.period._contract import (
    with_competence_contributions,
)
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.run import PayrollRun
from tests.fixtures.next_year_repository import NextYearRepository

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.ruleset import YearRules

_CEILING_2027 = Decimal("130000.00")


class _Repository(NextYearRepository):
    """2026 rules for 2027, with a 2027 massimale of its own."""

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        """Return the rules of ``year``; 2027 has a massimale of 130,000.

        Returns:
            The rules, labelled with ``year``.
        """
        rules = super().load_year_rules(year, sector, num_employees)
        if year != 2027 or rules.inps is None:
            return rules
        inps = rules.inps.model_copy(update={"ceiling": _CEILING_2027})
        return rules.model_copy(update={"inps": inps})


def _ceiling(run: PayrollRun, paid_on: date) -> object:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=run.year, month=run.month),
            payment_date=paid_on,
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            run=run,
        ),
        repo=_Repository(),
    )
    (decision,) = (
        d for d in result.decisions if d.capability == "ivs_ceiling_eligibility"
    )
    return decision.inputs["ceiling"]


def test_late_december_reads_the_massimale_of_its_competence_year() -> None:
    """December 2026 paid in 2027: 2026 massimale, 2027 IRPEF rules."""
    assert _ceiling(PayrollRun.regular(2026, 12), date(2027, 1, 13)) == Decimal(
        "122295.00"
    )
    assert _ceiling(PayrollRun.regular(2027, 1), date(2027, 1, 28)) == _CEILING_2027


def test_rules_of_the_competence_year_are_returned_unchanged() -> None:
    """A run paid in its own year keeps the rules it was given."""
    repository = _Repository()
    rules = repository.load_year_rules(2027, TaxSector.TERZIARIO, 50)

    assert (
        with_competence_contributions(repository, rules, 2027, TaxSector.TERZIARIO, 50)
        is rules
    )
