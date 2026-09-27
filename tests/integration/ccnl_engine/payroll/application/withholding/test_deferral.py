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
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from functools import cache
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.payroll.application.calculate_year import YearResult, calculate_year
from ccnl_engine.payroll.application.close_tax_year import close_tax_year
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.employment_facts import (
    ContributableHours,
    EmploymentPeriod,
    WeeklyHours,
)
from ccnl_engine.payroll.domain.events import AbsenceEvent, FringeEvent
from ccnl_engine.payroll.domain.inputs import PeriodFacts, PeriodInput
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import (
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
)
from ccnl_engine.payroll.domain.remittance import remittance_summary
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.shared.domain.errors import InvalidInputError, OutOfScopeError
from tests.helpers import EMPLOYER_50, year_input

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

_CCNL = "metalmeccanico-federmeccanica.json"
_YEAR = 2026
_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_FRINGE = FringeEvent(event_date=date(_YEAR, 12, 5), amount=Decimal(20000))
_REQUEST = ShortfallDeferralRequest(signed_on=date(_YEAR, 12, 10))


def _year_n(
    request: ShortfallDeferralRequest | None,
    employment_period: EmploymentPeriod | None = None,
) -> YearResult:
    return calculate_year(
        year_input(
            _YEAR,
            _CCNL,
            "C3",
            events={12: (_FRINGE,)},
            prior_year=PriorYearTaxFacts(shortfall_deferral=request),
            employment_period=employment_period,
        )
    )


@cache
def _without_request() -> YearResult:
    return _year_n(None)


@cache
def _with_request() -> YearResult:
    return _year_n(_REQUEST)


def _decision(result: PeriodResult, capability: str, reason: str) -> Decimal:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == reason
    )
    assert decision.amount is not None
    return decision.amount


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
        last = _without_request().period_results[-1]
        shortfall = _conguaglio_shortfall(last)
        assert shortfall > _ZERO
        assert last.closing_state.ytd.shortfall.irpef == shortfall
        assert last.closing_state.obligations.deferred_shortfall == ()
        assert "withholding_shortfall_unrecovered" in {i.code for i in last.issues}

    def test_with_request_the_irpef_is_deferred(self) -> None:
        """The request turns the IRPEF left into an obligation of N+1."""
        last = _with_request().period_results[-1]
        shortfall = _conguaglio_shortfall(last)
        (deferred,) = last.closing_state.obligations.deferred_shortfall
        assert deferred == DeferredShortfall(
            tax_year=_YEAR,
            signed_on=_REQUEST.signed_on,
            deferred_from=date(_YEAR, 12, 1),
            irpef=shortfall,
        )
        assert last.closing_state.ytd.shortfall.total == _ZERO
        assert not [i for i in last.issues if i.code.endswith("_unrecovered")]
        assert _decision(last, "shortfall_deferral", "shortfall_deferred") == shortfall

    def test_the_same_irpef_is_withheld_in_n(self) -> None:
        """The deferral changes nothing that N withholds."""
        plain = _without_request().period_results[-1].closing_state.ytd
        deferred = _with_request().period_results[-1].closing_state.ytd
        assert deferred.tax.irpef == plain.tax.irpef

    def test_close_tax_year_carries_the_deferral(self) -> None:
        """The next year opens with the deferral and nothing else of N."""
        closing = _with_request().period_results[-1].closing_state
        opened = close_tax_year(closing)
        assert opened.tax_year == _YEAR + 1
        assert opened.obligations.deferred_shortfall == (
            closing.obligations.deferred_shortfall
        )

    def test_termination_in_n_keeps_the_issue(self) -> None:
        """No payslip follows the last run: the request cannot defer."""
        year = _year_n(
            _REQUEST,
            employment_period=EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 12, 31)),
        )
        last = year.period_results[-1]
        assert last.closing_state.obligations.deferred_shortfall == ()
        assert _decision(last, "shortfall_deferral", "deferral_not_possible") == 0
        assert "withholding_shortfall_unrecovered" in {i.code for i in last.issues}

    def test_request_after_february_is_rejected(self) -> None:
        """The request must precede the deadline of the conguaglio."""
        late = ShortfallDeferralRequest(signed_on=date(_YEAR + 1, 3, 1))
        with pytest.raises(InvalidInputError, match="deferral request"):
            _year_n(late)


def _opening(irpef: str) -> PeriodState:
    deferred = DeferredShortfall(
        tax_year=_YEAR - 1,
        signed_on=date(_YEAR - 1, 12, 10),
        deferred_from=date(_YEAR - 1, 12, 1),
        irpef=Decimal(irpef),
    )
    return PeriodState(
        ytd=TaxYearState(tax_year=_YEAR),
        obligations=EmploymentObligations(deferred_shortfall=(deferred,)),
    )


def _year_n1(
    opening: PeriodState | None,
    events: dict[int, tuple[AbsenceEvent, ...]] | None = None,
    employment_period: EmploymentPeriod | None = None,
) -> YearResult:
    return calculate_year(
        year_input(
            _YEAR,
            _CCNL,
            "C3",
            events=events,
            opening_state=opening,
            employment_period=employment_period,
        )
    )


def _deferred_lines(result: PeriodResult) -> list[tuple[str, Decimal]]:
    return [
        (e.entry_id, e.amount)
        for e in result.ledger_entries
        if e.account == AccountKind.ORDINARY_TAX and e.remittance_code == "1066"
    ]


def _cents_down(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_DOWN)


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


@cache
def _plain_n1() -> YearResult:
    return _year_n1(None)


class TestWithholdingInYearN1:
    """The payslips of N+1 withhold the deferral from March, with interest."""

    def test_march_withholds_principal_and_interest(self) -> None:
        """300.00 EUR deferred: March withholds it with 3 months of interest.

        Interest: 300.00 x 0.50% x 3 = 4.50 EUR, both coded 1066.
        """
        year = _year_n1(_opening("300.00"))
        plain = _plain_n1()
        runs = year.period_results
        assert all(_deferred_lines(r) == [] for r in runs[:2])
        assert runs[1].closing_state.obligations.deferred_shortfall != ()
        march = runs[2]
        assert _deferred_lines(march) == [
            ("deferred_irpef_2025_2026-03-regular", Decimal("300.00")),
            ("deferred_irpef_2025_interest_2026-03-regular", Decimal("4.50")),
        ]
        assert march.period_net == plain.period_results[2].period_net - Decimal(
            "304.50"
        )
        assert march.closing_state.obligations.deferred_shortfall == ()
        assert (
            march.closing_state.ytd.tax == plain.period_results[2].closing_state.ytd.tax
        )
        assert _decision(
            march, "shortfall_deferral", "deferred_shortfall_withheld"
        ) == Decimal("304.50")

    def test_remittance_reports_code_1066(self) -> None:
        """The F24 summary keeps the 1066 amount apart from 1001."""
        march = _year_n1(_opening("300.00")).period_results[2]
        codes = {
            line.remittance_code: line.amount
            for line in remittance_summary(march.ledger_entries)
            if line.account == AccountKind.ORDINARY_TAX
        }
        assert codes["1066"] == Decimal("304.50")
        assert "1001" in codes

    def test_thin_march_defers_to_april(self) -> None:
        """March absences leave no pay: April withholds with 4 months.

        The 160 hours of absence leave no net pay in March, so nothing of
        the 300.00 EUR is withheld; April withholds it with 300.00 x 0.50%
        x 4 = 6.00 EUR of interest.
        """
        absence = AbsenceEvent(
            event_date=date(_YEAR, 3, 16),
            hours=Decimal(160),
            hourly_rate=Decimal("12.50"),
        )
        runs = _year_n1(_opening("300.00"), {3: (absence,)}).period_results
        assert runs[2].period_net == _ZERO
        assert _deferred_lines(runs[2]) == []
        assert _deferred_lines(runs[3]) == [
            ("deferred_irpef_2025_2026-04-regular", Decimal("300.00")),
            ("deferred_irpef_2025_interest_2026-04-regular", Decimal("6.00")),
        ]

    def test_large_deferral_runs_over_several_payslips(self) -> None:
        """Each payslip withholds the largest principal its pay covers.

        March leaves the net pay N of the plain run: principal
        floor(N / 1.015), interest principal x 1.50%.  April withholds the
        rest with 2.00% of interest.
        """
        year = _year_n1(_opening("2500.00"))
        plain_march = _plain_n1().period_results[2].period_net
        principal = _cents_down(plain_march / Decimal("1.015"))
        interest = _cents(principal * Decimal("0.015"))
        march, april = year.period_results[2], year.period_results[3]
        assert [a for _, a in _deferred_lines(march)] == [principal, interest]
        rest = Decimal("2500.00") - principal
        assert [a for _, a in _deferred_lines(april)] == [
            rest,
            _cents(rest * Decimal("0.020")),
        ]
        assert march.period_net <= _CENT

    def test_residual_at_the_conguaglio_is_communicated(self) -> None:
        """What December N+1 leaves is dropped with a provisional issue."""
        year = _year_n1(_opening("100000.00"))
        withheld = sum(
            (
                a
                for r in year.period_results
                for entry_id, a in _deferred_lines(r)
                if "interest" not in entry_id
            ),
            _ZERO,
        )
        last = year.period_results[-1]
        (issue,) = (
            i for i in last.issues if i.code == "deferred_shortfall_unrecovered"
        )
        assert issue.status == CalculationStatus.PROVISIONAL
        left = _decision(last, "shortfall_deferral", "deferred_shortfall_unrecovered")
        assert withheld + left == Decimal("100000.00")
        assert last.closing_state.obligations.deferred_shortfall == ()

    def test_termination_before_march_communicates_it(self) -> None:
        """An employment ending in February withholds nothing of it."""
        year = _year_n1(
            _opening("300.00"),
            employment_period=EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 2, 28)),
        )
        last = year.period_results[-1]
        assert all(_deferred_lines(r) == [] for r in year.period_results)
        assert "deferred_shortfall_unrecovered" in {i.code for i in last.issues}
        assert last.closing_state.obligations.deferred_shortfall == ()


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
                ccnl_slug=_CCNL, level_code="C3", employment_period=period
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
        which it neither withholds again nor drops.
        """
        plain = _adjustment(12, _without_request().period_results[-1].closing_state)
        closing = _with_request().period_results[-1].closing_state
        (deferred,) = closing.obligations.deferred_shortfall
        result = _adjustment(12, closing)
        owed = _ordinary_1001(plain) + plain.closing_state.ytd.shortfall.irpef
        assert _ordinary_1001(result) == owed - deferred.irpef
        assert result.closing_state.ytd.shortfall.irpef == _ZERO
        assert result.closing_state.obligations.deferred_shortfall == (deferred,)

    def test_refund_while_deferred_is_rejected(self) -> None:
        """A refund of the year of an open deferral is not modelled."""
        closing = _with_request().period_results[-1].closing_state
        tax = replace(closing.ytd.tax, irpef=closing.ytd.tax.irpef + 10000)
        opening = replace(closing, ytd=replace(closing.ytd, tax=tax))
        with pytest.raises(OutOfScopeError, match="deferred on written request"):
            _adjustment(12, opening)

    def test_termination_after_the_conguaglio_drops_the_deferral(self) -> None:
        """The last run of the employment in N leaves no payslip for it."""
        closing = _with_request().period_results[-1].closing_state
        result = _adjustment(12, closing, RunKind.TERMINATION)
        assert result.closing_state.obligations.deferred_shortfall == ()
        assert "deferred_shortfall_unrecovered" in {i.code for i in result.issues}

    def test_adjustment_of_n1_does_not_withhold(self) -> None:
        """An adjustment run is no pay period: March withholds instead."""
        february = _year_n1(_opening("300.00")).period_results[1].closing_state
        result = _adjustment(3, february)
        assert _deferred_lines(result) == []
        assert result.closing_state.obligations.deferred_shortfall == (
            february.obligations.deferred_shortfall
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
            ytd=TaxYearState(tax_year=_YEAR),
            obligations=EmploymentObligations(deferred_shortfall=(stale,)),
        )
        january = _year_n1(opening).period_results[0]
        assert _deferred_lines(january) == []
        assert "deferred_shortfall_unrecovered" in {i.code for i in january.issues}
        assert january.closing_state.obligations.deferred_shortfall == ()

    def test_one_cent_has_no_interest_line(self) -> None:
        """0.01 EUR at 1.50% rounds to no interest: only the principal."""
        march = _year_n1(_opening("0.01")).period_results[2]
        assert _deferred_lines(march) == [
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
                    ),
                    employer=EmployerProfile(headcount=Headcount(1)),
                    facts=PeriodFacts(
                        contributable_hours=ContributableHours(Decimal(173))
                    ),
                    opening_state=_opening("300.00"),
                )
            )
