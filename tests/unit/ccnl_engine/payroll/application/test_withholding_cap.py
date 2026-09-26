"""IRPEF and surtax withheld up to the pay left, the shortfall carried.

Art. 33 c. 4 D.Lgs. 33/2025 (ex art. 23 c. 3 DPR 600/1973): the conguaglio
settles the tax on the whole year; what the pay cannot cover on the last
slot is communicated to the worker.

The Metalmeccanico C3 case: 160 absence hours at 12.50 EUR deduct 2,000 EUR
of the 2,158.26 EUR January pay.  The expectation is derived by hand:

- employee INPS on the 158.26 EUR left: 9.19% IVS (14.54) plus 0.30% CIGS
  (0.47), rounded per component: 15.01; pay left 158.26 - 15.01 = 143.25;
- projected taxable: 143.25 plus twelve slots of 2,158.26 less 9.49% INPS
  (2,457.83 on 25,899.12): 23,584.54;
- net IRPEF by the independent oracle, split over 13 slots: 162.33;
- shortfall: 162.33 - 143.25 = 19.08, carried to February.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from functools import cache

from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.tax.service.tax_annual_assembler import load_year_rules
from ccnl_engine.payroll.application._period_amounts import _PeriodAmounts
from ccnl_engine.payroll.application._withholding_cap import (
    CappedWithholding,
    cap_withholding,
)
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import (
    YearResult,
    calculate_year,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.events import AbsenceEvent
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.ytd_accounts import WithholdingShortfall
from ccnl_engine.payroll.service.rounding import money
from tests.fixtures.legal_examples.irpef_2026 import net_irpef
from tests.helpers import year_input

_CCNL = "metalmeccanico-federmeccanica.json"
_YEAR = 2026
_ZERO = Decimal(0)
_PAY = Decimal("2158.26")
_ABSENCE = AbsenceEvent(
    event_date=date(_YEAR, 1, 15), hours=Decimal(160), hourly_rate=Decimal("12.50")
)


def _run(month: int, opening: PeriodState, *events: AbsenceEvent) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 27),
            ccnl_slug=_CCNL,
            level_code="C3",
            opening_state=opening,
            events=events,
        )
    )


@cache
def _january() -> PeriodResult:
    return _run(1, PeriodState.zero(), _ABSENCE)


@cache
def _year() -> YearResult:
    return calculate_year(year_input(_YEAR, _CCNL, "C3", events={1: (_ABSENCE,)}))


def _expected_january_share() -> Decimal:
    upcoming = 12 * _PAY
    inps = (upcoming * Decimal("0.0949")).quantize(Decimal("0.01"), ROUND_HALF_UP)
    projected = Decimal("143.25") + upcoming - inps
    return money(net_irpef(projected) / 13)


def _ordinary_tax(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        ),
        _ZERO,
    )


class TestAbsenceShortfall:
    """The C3 January absence withholds the pay left and carries the rest."""

    def test_january_net_is_zero(self) -> None:
        """IRPEF takes the 143.25 EUR left and no more."""
        result = _january()
        assert result.period_net == Decimal("0.00")
        assert _ordinary_tax(result) == Decimal("143.25")

    def test_shortfall_is_carried(self) -> None:
        """The 19.08 EUR not withheld is carried in the tax year state."""
        assert _expected_january_share() == Decimal("162.33")
        shortfall = _january().closing_state.ytd.shortfall
        assert shortfall.irpef == _expected_january_share() - Decimal("143.25")
        assert shortfall.irpef == Decimal("19.08")
        assert shortfall.surtax == _ZERO

    def test_decision_records_the_cap(self) -> None:
        """The run records why it withheld less than due."""
        (decision,) = (
            d for d in _january().decisions if d.capability == "withholding_shortfall"
        )
        assert decision.reason_code == "withholding_capped"
        assert decision.amount == Decimal("19.08")
        assert decision.inputs["pay_available"] == Decimal("143.25")

    def test_catalog_capabilities_have_no_gap(self) -> None:
        """The capabilities the catalog now declares are traced every run."""
        gaps = {g.feature for g in _january().capability_report.gaps}
        declared = {
            "withholding_shortfall",
            "somma_esente",
            "rinnovo_substitute_tax",
            "notte_festivi_turni_substitute_tax",
        }
        assert gaps.isdisjoint(declared)

    def test_february_withholds_the_carried_amount(self) -> None:
        """February withholds the 19.08 EUR in full, outside the spread.

        With the carried amount the remaining balance spread over the twelve
        slots left excludes it, so February withholds 19.08 - 19.08 / 12 =
        17.49 EUR more than a state that carried nothing.
        """
        opening = _january().closing_state
        february = _run(2, opening)
        plain_ytd = replace(opening.ytd, shortfall=WithholdingShortfall())
        plain = _run(2, replace(opening, ytd=plain_ytd))
        difference = _ordinary_tax(february) - _ordinary_tax(plain)
        assert abs(difference - Decimal("17.49")) <= Decimal("0.01")
        assert february.closing_state.ytd.shortfall.total == _ZERO
        (decision,) = (
            d for d in february.decisions if d.capability == "withholding_shortfall"
        )
        assert decision.reason_code == "shortfall_withheld"
        assert decision.amount == _ZERO

    def test_year_withholds_the_oracle_irpef(self) -> None:
        """Over the year the IRPEF withheld is the net IRPEF of the oracle."""
        year = _year()
        final = year.period_results[-1].closing_state.ytd
        withheld = sum((_ordinary_tax(r) for r in year.period_results), _ZERO)
        assert withheld == final.tax.irpef
        assert abs(withheld - net_irpef(final.earnings.taxable)) <= Decimal("0.01")
        assert final.shortfall.total == _ZERO
        assert all(r.period_net >= _ZERO for r in year.period_results)
        assert not [i for i in year.issues if i.code.startswith("withholding")]


def _amounts(irpef: Decimal, surtax: Decimal) -> _PeriodAmounts:
    return _PeriodAmounts(
        monthly_gross=_ZERO,
        inps_employee=_ZERO,
        inps_employer=_ZERO,
        tfr=_ZERO,
        period_irpef=irpef,
        period_tratt=_ZERO,
        period_surtax=surtax,
        period_taxable=_ZERO,
        period_substitute_tax=_ZERO,
        pdr_eligible=_ZERO,
    )


def _entry(account: AccountKind, amount: Decimal) -> LedgerEntry:
    return LedgerEntry(
        entry_id=f"{account}_x",
        competence_period=CompetencePeriod(year=_YEAR, month=12),
        payment_date=date(_YEAR, 12, 27),
        pay_item_id="x",
        pay_item_kind="x",
        account=account,
        amount=amount,
    )


_RULES = load_year_rules(_YEAR, TaxSector.INDUSTRIA, 50)


def _cap(
    irpef: Decimal, surtax: Decimal, pay: Decimal, *, last_slot: bool = False
) -> CappedWithholding:
    entries = [_entry(AccountKind.CASH_EARNINGS, pay)]
    if irpef > _ZERO:
        entries.append(_entry(AccountKind.ORDINARY_TAX, irpef))
    elif irpef < _ZERO:
        entries.append(_entry(AccountKind.CREDITS, -irpef))
    if surtax:
        entries.append(_entry(AccountKind.SURTAX, surtax))
    return cap_withholding(
        _amounts(irpef, surtax),
        tuple(entries),
        WithholdingShortfall(),
        last_slot=last_slot,
        rules=_RULES,
    )


class TestCapWithholding:
    """Order of the cap and what is never capped."""

    def test_nothing_to_cap(self) -> None:
        """A run whose pay covers the tax is left unchanged, no decision."""
        amounts = _amounts(Decimal(100), Decimal(10))
        capped = cap_withholding(
            amounts,
            (_entry(AccountKind.CASH_EARNINGS, Decimal(500)),),
            WithholdingShortfall(),
            last_slot=False,
            rules=_RULES,
        )
        assert capped.amounts is amounts
        assert capped.decisions == ()

    def test_irpef_before_surtax(self) -> None:
        """IRPEF is withheld first; the surtax takes what is left."""
        capped = _cap(Decimal(100), Decimal(30), Decimal(120))
        assert capped.amounts.period_irpef == Decimal(100)
        assert capped.amounts.period_surtax == Decimal(20)
        assert capped.shortfall == WithholdingShortfall(surtax=Decimal(10))

    def test_refund_is_not_capped(self) -> None:
        """A conguaglio refund is paid; only the surtax is capped."""
        capped = _cap(Decimal(-40), Decimal(80), Decimal(0))
        assert capped.amounts.period_irpef == Decimal(-40)
        assert capped.amounts.period_surtax == Decimal(40)
        assert capped.shortfall == WithholdingShortfall(surtax=Decimal(40))

    def test_last_slot_reports_the_shortfall(self) -> None:
        """A shortfall left on the last slot is a provisional issue."""
        capped = _cap(Decimal(100), _ZERO, Decimal(60), last_slot=True)
        (issue,) = capped.issues
        assert issue.code == "withholding_shortfall_unrecovered"
        assert issue.status == CalculationStatus.PROVISIONAL
        assert "40 IRPEF" in issue.message

    def test_no_pay_left_withholds_nothing(self) -> None:
        """Deductions above the pay leave nothing to withhold."""
        amounts = _amounts(Decimal(50), _ZERO)
        entries = (
            _entry(AccountKind.CASH_EARNINGS, Decimal(10)),
            _entry(AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal(20)),
            _entry(AccountKind.ORDINARY_TAX, Decimal(50)),
        )
        capped = cap_withholding(
            amounts, entries, WithholdingShortfall(), last_slot=False, rules=_RULES
        )
        assert capped.amounts.period_irpef == _ZERO
        assert capped.shortfall.irpef == Decimal(50)
