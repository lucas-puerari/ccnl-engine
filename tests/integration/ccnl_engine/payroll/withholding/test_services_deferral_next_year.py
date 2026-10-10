"""Deferred IRPEF shortfall withheld in the year after the conguaglio.

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

from datetime import date
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.employment.inputs_fact import (
    EmploymentPeriod,
)
from ccnl_engine.payroll.event.facade import AbsenceEvent
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.ledger.models_remittance import remittance_summary
from tests.integration.ccnl_engine.payroll.withholding.builders_shortfall_deferral import (  # noqa: E501
    decision_amount,
    deferred_lines,
    opening_with_deferral,
    year_n1,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.year.results import CompetenceYearResult

_CCNL = "metalmeccanico-federmeccanica.json"
_YEAR = 2026
_ZERO = Decimal(0)
_CENT = Decimal("0.01")


def _cents_down(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_DOWN)


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


@cache
def _plain_n1() -> CompetenceYearResult:
    return year_n1(None)


class TestWithholdingInYearN1:
    """The payslips of N+1 withhold the deferral from March, with interest."""

    def test_march_withholds_principal_and_interest(self) -> None:
        """300.00 EUR deferred: March withholds it with 3 months of interest.

        Interest: 300.00 x 0.50% x 3 = 4.50 EUR, both coded 1066.
        """
        year = year_n1(opening_with_deferral("300.00"))
        plain = _plain_n1()
        runs = year.period_results
        assert all(deferred_lines(r) == [] for r in runs[:2])
        assert runs[1].closing_state.cash.obligations.deferred_shortfall != ()
        march = runs[2]
        assert deferred_lines(march) == [
            ("deferred_irpef_2025_2026-03-regular", Decimal("300.00")),
            ("deferred_irpef_2025_interest_2026-03-regular", Decimal("4.50")),
        ]
        assert march.period_net == plain.period_results[2].period_net - Decimal(
            "304.50"
        )
        assert march.closing_state.cash.obligations.deferred_shortfall == ()
        assert (
            march.closing_state.cash.tax
            == plain.period_results[2].closing_state.cash.tax
        )
        assert decision_amount(
            march, "shortfall_deferral", "deferred_shortfall_withheld"
        ) == Decimal("304.50")

    def test_remittance_reports_code_1066(self) -> None:
        """The F24 summary keeps the 1066 amount apart from 1001."""
        march = year_n1(opening_with_deferral("300.00")).period_results[2]
        codes = {
            line.remittance_code: line.amount
            for line in remittance_summary(march.ledger_entries)
            if line.account == AccountKind.ORDINARY_TAX
        }
        assert codes["1066"] == Decimal("304.50")
        assert "1001" in codes

    def test_thin_march_defers_to_april(self) -> None:
        """March absences leave no pay: April withholds with 4 months.

        78 hours of absence at 27.67 EUR deduct the whole 2,158.26 EUR of
        March pay, so nothing of the 300.00 EUR is withheld; April withholds
        it with 300.00 x 0.50% x 4 = 6.00 EUR of interest.
        """
        absence = AbsenceEvent(
            event_date=date(_YEAR, 3, 16),
            hours=Decimal(78),
            hourly_rate=Decimal("27.67"),
        )
        runs = year_n1(opening_with_deferral("300.00"), {3: (absence,)}).period_results
        assert runs[2].period_net == _ZERO
        assert deferred_lines(runs[2]) == []
        assert deferred_lines(runs[3]) == [
            ("deferred_irpef_2025_2026-04-regular", Decimal("300.00")),
            ("deferred_irpef_2025_interest_2026-04-regular", Decimal("6.00")),
        ]

    def test_large_deferral_runs_over_several_payslips(self) -> None:
        """Each payslip withholds the largest principal its pay covers.

        March leaves the net pay N of the plain run: principal
        floor(N / 1.015), interest principal x 1.50%.  April withholds the
        rest with 2.00% of interest.
        """
        year = year_n1(opening_with_deferral("2500.00"))
        plain_march = _plain_n1().period_results[2].period_net
        principal = _cents_down(plain_march / Decimal("1.015"))
        interest = _cents(principal * Decimal("0.015"))
        march, april = year.period_results[2], year.period_results[3]
        assert [a for _, a in deferred_lines(march)] == [principal, interest]
        rest = Decimal("2500.00") - principal
        assert [a for _, a in deferred_lines(april)] == [
            rest,
            _cents(rest * Decimal("0.020")),
        ]
        assert march.period_net <= _CENT

    def test_residual_at_the_conguaglio_is_communicated(self) -> None:
        """What December N+1 leaves is dropped with a provisional issue."""
        year = year_n1(opening_with_deferral("100000.00"))
        withheld = sum(
            (
                a
                for r in year.period_results
                for entry_id, a in deferred_lines(r)
                if "interest" not in entry_id
            ),
            _ZERO,
        )
        last = year.period_results[-1]
        (issue,) = (
            i for i in last.issues if i.code == "deferred_shortfall_unrecovered"
        )
        assert issue.status == CalculationStatus.PROVISIONAL
        left = decision_amount(
            last, "shortfall_deferral", "deferred_shortfall_unrecovered"
        )
        assert withheld + left == Decimal("100000.00")
        assert last.closing_state.cash.obligations.deferred_shortfall == ()

    def test_termination_before_march_communicates_it(self) -> None:
        """An employment ending in February withholds nothing of it."""
        year = year_n1(
            opening_with_deferral("300.00"),
            employment_period=EmploymentPeriod(date(2020, 1, 1), date(_YEAR, 2, 28)),
        )
        last = year.period_results[-1]
        assert all(deferred_lines(r) == [] for r in year.period_results)
        assert "deferred_shortfall_unrecovered" in {i.code for i in last.issues}
        assert last.closing_state.cash.obligations.deferred_shortfall == ()
