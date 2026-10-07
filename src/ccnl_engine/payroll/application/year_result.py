"""Results of a sequence of payments: a competence year or a tax year."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.close_tax_year import close_tax_year
from ccnl_engine.payroll.domain.assurance import ResultAssurance
from ccnl_engine.payroll.domain.remittance import remittance_summary

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.assurance import ResultBlocker
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.payment import PaymentId
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.remittance import RemittanceLine
    from ccnl_engine.payroll.domain.uncovered_run import UncoveredRun
    from ccnl_engine.provenance.domain.ruleset_assurance import RulesetAssurance

__all__ = ["CompetenceYearResult", "PaymentsResult", "TaxYearResult"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class PaymentsResult:
    """Results of payments computed one after the other, in payment order.

    Attributes:
        period_results: One :class:`PeriodResult` per payment computed, in
            payment order.  Payments the opening state already closed are
            not computed again and have no result here.
        opening_state: State the first payment opened with.
        bundle_version: Knowledge-bundle version of the calculation.
        uncovered_runs: Runs of the plans not computed because the bundle
            holds no base salary of their level on their competence date,
            in run order.  Each adds a ``run_not_computed`` blocker: a
            partial year is not payable, and its withholding and
            conguaglio leave those runs out.
    """

    period_results: tuple[PeriodResult, ...]
    opening_state: PeriodState
    bundle_version: str | None = field(default=None, kw_only=True)
    uncovered_runs: tuple[UncoveredRun, ...] = field(default=(), kw_only=True)

    @property
    def annual_gross(self) -> Decimal:
        """Sum of ``period_gross`` across the payments computed."""
        return sum((r.period_gross for r in self.period_results), _ZERO)

    @property
    def annual_net(self) -> Decimal:
        """Sum of ``period_net`` across the payments computed."""
        return sum((r.period_net for r in self.period_results), _ZERO)

    @property
    def annual_employer_cost(self) -> Decimal:
        """Sum of ``period_employer_cost`` across the payments computed."""
        return sum((r.period_employer_cost for r in self.period_results), _ZERO)

    @property
    def assurance(self) -> ResultAssurance:
        """Assurance of every payment, combined.

        Each axis is the worst of the runs; rulesets and blockers are
        listed once each, followed by one ``run_not_computed`` blocker per
        run of :attr:`uncovered_runs`.  The result is payable only when
        every run is and none was left out.
        """
        combined = ResultAssurance.combine(r.assurance for r in self.period_results)
        return combined.with_blockers(u.blocker for u in self.uncovered_runs)

    @property
    def is_payable(self) -> bool:
        """Whether every payment computed is payable."""
        return self.assurance.is_payable

    @property
    def blockers(self) -> tuple[ResultBlocker, ...]:
        """Blockers of every payment, each listed once."""
        return self.assurance.blockers

    @property
    def rulesets(self) -> tuple[RulesetAssurance, ...]:
        """Rulesets read by any payment, each listed once."""
        return self.assurance.rulesets

    @property
    def issues(self) -> tuple[CalculationIssue, ...]:
        """Issues of every payment in payment order, each reported once.

        A run repeats the issue of an assumption that holds for the whole
        year (e.g. ``somma_esente_income_assumed``) on every payslip; the
        result lists it once, at its first occurrence.  Issues with the same
        code and a different message (e.g. two shortfall amounts) are kept.
        The issues of a single run stay on :attr:`period_results`.
        """
        seen: set[tuple[str, str]] = set()
        issues: list[CalculationIssue] = []
        for issue in (i for r in self.period_results for i in r.issues):
            if (issue.code, issue.message) not in seen:
                seen.add((issue.code, issue.message))
                issues.append(issue)
        return tuple(issues)

    @property
    def decisions(self) -> tuple[CalculationDecision, ...]:
        """Decisions of every payment, concatenated in payment order."""
        return tuple(d for r in self.period_results for d in r.decisions)

    def remittance_summary(self) -> tuple[RemittanceLine, ...]:
        """Return the tax and credit amounts by codice tributo.

        The F24 is filed by month of payment: use
        :meth:`PeriodResult.remittance_summary` on each run for that.

        Returns:
            The lines of every payment, summed by account and code.
        """
        return remittance_summary(
            e for r in self.period_results for e in r.ledger_entries
        )

    @property
    def closing_state(self) -> PeriodState:
        """State after the last payment: the opening state when none ran."""
        if not self.period_results:
            return self.opening_state
        return self.period_results[-1].closing_state

    @property
    def conguagli(self) -> tuple[PaymentId, ...]:
        """Payments that settled the conguaglio of their tax year, in order."""
        found: list[PaymentId] = []
        for result in self.period_results:
            conguaglio = result.closing_state.cash.conguaglio
            if conguaglio is not None and conguaglio not in found:
                found.append(conguaglio)
        return tuple(found)


@dataclass(frozen=True)
class CompetenceYearResult(PaymentsResult):
    """Results of the runs of one competence year, in payment order.

    The runs paid in the competence year come first and the last of them
    settles the conguaglio of that tax year, which is then closed; the
    runs paid in the next tax year (a December paid after 12 January)
    follow and open it.

    Attributes:
        year: The competence year.
        calendar: The calendar the year ran on: the CCNL standard calendar,
            or the accepted override.
        calendar_override: The override that replaced the standard calendar,
            with its reason and note, or ``None`` when the standard applied.
    """

    year: int = field(kw_only=True)
    calendar: WorkCalendar = field(kw_only=True)
    calendar_override: CalendarOverride | None = field(default=None, kw_only=True)

    @property
    def next_opening_state(self) -> PeriodState:
        """State to open the next competence year with.

        ``close_tax_year()`` of :attr:`closing_state` when the last payment
        settled its tax year; otherwise the closing state itself, a state
        of the next tax year that already holds the late payments.
        """
        closing = self.closing_state
        if closing.cash.is_complete:
            return close_tax_year(closing)
        return closing


@dataclass(frozen=True)
class TaxYearResult(PaymentsResult):
    """Results of every payment of one tax year, in payment order.

    Attributes:
        tax_year: The tax year.
        payments: Every payment of the tax year in payment order: those
            the opening state had already closed, then those computed.
    """

    tax_year: int = field(kw_only=True)
    payments: tuple[PaymentId, ...] = field(kw_only=True)

    @property
    def conguaglio(self) -> PaymentId | None:
        """The payment that settled the conguaglio, ``None`` when none did."""
        return self.closing_state.cash.conguaglio

    @property
    def next_opening_state(self) -> PeriodState:
        """``close_tax_year()`` of :attr:`closing_state`: the next tax year."""
        return close_tax_year(self.closing_state)
