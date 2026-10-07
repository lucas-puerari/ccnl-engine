"""Year-end IRPEF shortfall deferred to the next year on written request.

Art. 23 c. 3 DPR 600/1973 (in force for 2026): on the worker's written
request the IRPEF the conguaglio cannot withhold is withheld "sulle
retribuzioni dei periodi di paga successivi al secondo dello stesso periodo
di imposta", with interest "in ragione dello 0,50 per cento mensile",
remitted as the tax (code 1066, ris. AdE 6/E/2021).

Year N is the 2026 Metalmeccanico C3 year with a 20,000 EUR fringe benefit
in December: its IRPEF exceeds the December and thirteenth pay, so the
conguaglio on the thirteenth leaves a shortfall.  Year N+1 is modelled as
2026 opening with a deferral of the conguaglio 2025 (paid on the December
2025 payslip), the only year whose rules the bundle holds.  The interest of
a payslip of March is 3 months (December to March) at 0.50 per cent:
1.50 per cent of the principal.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.payroll.application.close_tax_year import close_tax_year
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment, Permanent
from ccnl_engine.payroll.domain.employment_facts import (
    ContributableHours,
    EmploymentPeriod,
    WeeklyHours,
)
from ccnl_engine.payroll.domain.inputs import PeriodFacts, PeriodInput
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import (
    ShortfallDeferralRequest,
)
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.shared.domain.errors import InvalidInputError, OutOfScopeError
from tests.fixtures.shortfall_deferral import (
    DEFERRAL_REQUEST,
    decision_amount,
    deferred_lines,
    opening_with_deferral,
    year_n,
    year_n1,
    year_n_with_request,
    year_n_without_request,
)
from tests.helpers import EMPLOYER_50

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

_CCNL = "metalmeccanico-federmeccanica.json"
_YEAR = 2026
_ZERO = Decimal(0)
_CENT = Decimal("0.01")


def _conguaglio_shortfall(result: PeriodResult) -> Decimal:
    """Return the IRPEF due on the conguaglio less the pay it leaves.

    Returns:
        The difference of the inputs the cap decision recorded.
    """
    (cap,) = (d for d in result.decisions if d.capability == "withholding_shortfall")
    return Decimal(cap.inputs["irpef_due"]) - Decimal(cap.inputs["pay_available"])


class TestConguaglioOfYearN:
    """The conguaglio of N with and without the written request."""

    def test_without_request_the_shortfall_is_communicated(self) -> None:
        """No request: the shortfall stays an issue and nothing is deferred."""
        last = year_n_without_request().period_results[-1]
        shortfall = _conguaglio_shortfall(last)
        assert shortfall > _ZERO
        assert last.closing_state.cash.shortfall.irpef == shortfall
        assert last.closing_state.cash.obligations.deferred_shortfall == ()
        assert "withholding_shortfall_unrecovered" in {i.code for i in last.issues}

    def test_with_request_the_irpef_is_deferred(self) -> None:
        """The request turns the IRPEF left into an obligation of N+1."""
        last = year_n_with_request().period_results[-1]
        shortfall = _conguaglio_shortfall(last)
        (deferred,) = last.closing_state.cash.obligations.deferred_shortfall
        assert deferred == DeferredShortfall(
            tax_year=_YEAR,
            signed_on=DEFERRAL_REQUEST.signed_on,
            deferred_from=date(_YEAR, 12, 1),
            irpef=shortfall,
        )
        assert last.closing_state.cash.shortfall.total == _ZERO
        assert not [i for i in last.issues if i.code.endswith("_unrecovered")]
        assert (
            decision_amount(last, "shortfall_deferral", "shortfall_deferred")
            == shortfall
        )

    def test_the_same_irpef_is_withheld_in_n(self) -> None:
        """The deferral changes nothing that N withholds."""
        plain = year_n_without_request().period_results[-1].closing_state.cash
        deferred = year_n_with_request().period_results[-1].closing_state.cash
        assert deferred.tax.irpef == plain.tax.irpef

    def test_close_tax_year_carries_the_deferral(self) -> None:
        """The next year opens with the deferral and nothing else of N."""
        closing = year_n_with_request().period_results[-1].closing_state
        opened = close_tax_year(closing)
        assert opened.tax_year == _YEAR + 1
        assert opened.cash.obligations.deferred_shortfall == (
            closing.cash.obligations.deferred_shortfall
        )

    def test_termination_in_n_keeps_the_issue(self) -> None:
        """No payslip follows the last run: the request cannot defer."""
        year = year_n(
            DEFERRAL_REQUEST,
            employment_period=EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 12, 31)),
        )
        last = year.period_results[-1]
        assert last.closing_state.cash.obligations.deferred_shortfall == ()
        assert decision_amount(last, "shortfall_deferral", "deferral_not_possible") == 0
        assert "withholding_shortfall_unrecovered" in {i.code for i in last.issues}

    def test_request_after_february_is_rejected(self) -> None:
        """The request must precede the deadline of the conguaglio."""
        late = ShortfallDeferralRequest(signed_on=date(_YEAR + 1, 3, 1))
        with pytest.raises(InvalidInputError, match="deferral request"):
            year_n(late)


def _adjustment(
    month: int, opening: PeriodState, kind: RunKind = RunKind.ADJUSTMENT
) -> PeriodResult:
    period = (
        EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 12, 31))
        if kind is RunKind.TERMINATION
        else None
    )
    return PayrollEngine().calculate_period(
        PeriodInput(
            run=PayrollRun(run_kind=kind, month=month, year=_YEAR),
            payment_date=date(_YEAR, month, 28),
            employment=Employment(
                ccnl_slug=_CCNL,
                level_code="C3",
                employment_period=period,
                contract_type=Permanent(),
            ),
            employer=EMPLOYER_50,
            opening_state=opening,
        )
    )


def _ordinary_1001(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX and e.remittance_code == "1001"
        ),
        _ZERO,
    )


class TestOtherRuns:
    """Adjustment runs and deferrals of an earlier year."""

    def test_adjustment_after_the_conguaglio_keeps_the_deferral(self) -> None:
        """An adjustment run of N counts the deferred IRPEF as withheld.

        Without the request the adjustment owes the IRPEF of its own pay
        plus the shortfall carried in: 1001 withheld plus the shortfall it
        carries out.  With the request it owes that less the deferred IRPEF,
        which it neither withholds again nor drops.  The adjustment pays no
        cash, so what it owes is carried out as a shortfall.
        """
        plain = _adjustment(
            12, year_n_without_request().period_results[-1].closing_state
        )
        closing = year_n_with_request().period_results[-1].closing_state
        (deferred,) = closing.cash.obligations.deferred_shortfall
        result = _adjustment(12, closing)
        owed = _ordinary_1001(plain) + plain.closing_state.cash.shortfall.irpef
        result_owed = _ordinary_1001(result) + result.closing_state.cash.shortfall.irpef
        assert result_owed == owed - deferred.irpef
        assert result.closing_state.cash.obligations.deferred_shortfall == (deferred,)

    def test_refund_while_deferred_is_rejected(self) -> None:
        """A refund of the year of an open deferral is not modelled."""
        closing = year_n_with_request().period_results[-1].closing_state
        tax = replace(closing.cash.tax, irpef=closing.cash.tax.irpef + 10000)
        opening = replace(closing, cash=replace(closing.cash, tax=tax))
        with pytest.raises(OutOfScopeError, match="deferred on written request"):
            _adjustment(12, opening)

    def test_termination_after_the_conguaglio_drops_the_deferral(self) -> None:
        """The last run of the employment in N leaves no payslip for it."""
        closing = year_n_with_request().period_results[-1].closing_state
        result = _adjustment(12, closing, RunKind.TERMINATION)
        assert result.closing_state.cash.obligations.deferred_shortfall == ()
        assert "deferred_shortfall_unrecovered" in {i.code for i in result.issues}

    def test_adjustment_of_n1_does_not_withhold(self) -> None:
        """An adjustment run is no pay period: March withholds instead."""
        february = (
            year_n1(opening_with_deferral("300.00")).period_results[1].closing_state
        )
        result = _adjustment(3, february)
        assert deferred_lines(result) == []
        assert result.closing_state.cash.obligations.deferred_shortfall == (
            february.cash.obligations.deferred_shortfall
        )

    def test_deferral_of_an_older_year_is_communicated(self) -> None:
        """A deferral of N-2 is past its year: January drops it at once."""
        stale = DeferredShortfall(
            tax_year=_YEAR - 2,
            signed_on=date(_YEAR - 2, 12, 10),
            deferred_from=date(_YEAR - 2, 12, 1),
            irpef=Decimal("50.00"),
        )
        opening = PeriodState(
            cash=TaxCashState(
                tax_year=_YEAR,
                obligations=EmploymentObligations(deferred_shortfall=(stale,)),
            )
        )
        january = year_n1(opening).period_results[0]
        assert deferred_lines(january) == []
        assert "deferred_shortfall_unrecovered" in {i.code for i in january.issues}
        assert january.closing_state.cash.obligations.deferred_shortfall == ()

    def test_one_cent_has_no_interest_line(self) -> None:
        """0.01 EUR at 1.50% rounds to no interest: only the principal."""
        march = year_n1(opening_with_deferral("0.01")).period_results[2]
        assert deferred_lines(march) == [
            ("deferred_irpef_2025_2026-03-regular", Decimal("0.01"))
        ]

    def test_employer_without_withholding_rejects_a_deferral(self) -> None:
        """A household employer cannot carry a deferred IRPEF."""
        with pytest.raises(InvalidInputError, match="withholding shortfall"):
            PayrollEngine().calculate_period(
                PeriodInput(
                    run=PayrollRun.regular(year=_YEAR, month=3),
                    payment_date=date(_YEAR, 3, 28),
                    employment=Employment(
                        ccnl_slug="lavoro-domestico-convivente.json",
                        level_code="A",
                        weekly_hours=WeeklyHours(40),
                        contract_type=Permanent(),
                    ),
                    employer=EmployerProfile(headcount=Headcount(1)),
                    facts=PeriodFacts(
                        contributable_hours=ContributableHours(Decimal(173))
                    ),
                    opening_state=opening_with_deferral("300.00"),
                )
            )
