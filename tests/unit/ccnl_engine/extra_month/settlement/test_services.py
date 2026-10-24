"""Ratei liquidated at the termination: their earnings and the bases they enter."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.event.total.handlers import _EventTotals
from ccnl_engine.extra_month.models import ExtraMonthAccrual
from ccnl_engine.extra_month.schedule.models import AccrualWindow, ExtraMonthKind
from ccnl_engine.extra_month.settlement.services import (
    ExtraMonthSettlement,
    settle_extra_months,
)
from ccnl_engine.pay_item.facade import CompetencePeriod, ExtraMonthEarning
from ccnl_engine.pay_item.policies import (
    ContributionAxis,
    PolicyContext,
    TaxAxis,
    TfrAxis,
)

_D = Decimal
_PAID = date(2026, 6, 27)


def _edr(*, tfr_relevant: bool) -> Allowance:
    monthly = TimeSeries(
        periods=(
            ValidityPeriod(
                value=_D(120), valid_from=date(2024, 1, 1), valid_until=None
            ),
        )
    )
    return Allowance(
        code="edr",
        description="EDR",
        monthly=monthly,
        months_per_year=14,
        tfr_relevant=tfr_relevant,
    )


_CHAIN = MonthlyPayChain(
    base=_D(1200), seniority=_D(60), allowances=((_edr(tfr_relevant=False), _D(120)),)
)


def _accrual(kind: ExtraMonthKind, months: int) -> ExtraMonthAccrual:
    start = date(2026, 1, 1)
    return ExtraMonthAccrual(
        kind=kind, window=AccrualWindow(start, start, date(2026, 12, 31)), months=months
    )


class _Resolver:
    """Resolves every kind to one treatment, as the bundle policy would."""

    def __init__(self, *, included: bool) -> None:
        axis = (
            (ContributionAxis.INCLUDED, TfrAxis.INCLUDED, TaxAxis.ORDINARY)
            if included
            else (ContributionAxis.EXCLUDED, TfrAxis.EXCLUDED, TaxAxis.EXEMPT)
        )
        self._resolution = SimpleNamespace(
            contribution=axis[0], tfr=axis[1], tax=axis[2], policy_id="it/test"
        )

    def resolve(self, kind: str, context: object) -> Any:  # noqa: ANN401
        return self._resolution


def _settle(
    settlements: tuple[ExtraMonthAccrual, ...], *, included: bool = True
) -> ExtraMonthSettlement:
    return settle_extra_months(
        settlements,
        _CHAIN,
        CompetencePeriod(year=2026, month=6),
        _PAID,
        "2026-06-regular",
        _Resolver(included=included),  # type: ignore[arg-type]
        PolicyContext(year=2026, as_of=_PAID),
    )


def _earnings(settled: ExtraMonthSettlement) -> list[ExtraMonthEarning]:
    return [i for i in settled.items if isinstance(i, ExtraMonthEarning)]


def test_each_extra_month_pays_its_ratei_of_the_whole_chain() -> None:
    """Six twelfths of base, seniority and EDR: 690.00, as month 13 or 14."""
    settled = _settle((
        _accrual(ExtraMonthKind.THIRTEENTH, 6),
        _accrual(ExtraMonthKind.FOURTEENTH, 3),
    ))

    assert [(i.month_number, i.amount) for i in _earnings(settled)] == [
        (13, _D("690.00")),
        (14, _D("345.00")),
    ]
    assert [i.source for i in _earnings(settled)] == [
        "ratei at termination: 6/12",
        "ratei at termination: 3/12",
    ]
    assert [e.amount for e in settled.entries] == [_D("690.00"), _D("345.00")]


def test_the_ratei_enter_every_base_but_the_edr_stays_out_of_the_tfr() -> None:
    """INPS and IRPEF take the whole ratei; the TFR leaves the EDR out."""
    settled = _settle((_accrual(ExtraMonthKind.THIRTEENTH, 6),))

    assert settled.inps_base == _D("690.00")
    assert settled.irpef_base == _D("690.00")
    assert settled.tfr_base == _D("630.00")


def test_a_policy_outside_the_bases_leaves_them_at_zero() -> None:
    """Exempt and excluded from INPS and TFR: the ratei are paid, untaxed."""
    settled = _settle((_accrual(ExtraMonthKind.THIRTEENTH, 6),), included=False)

    assert settled.items
    assert (settled.inps_base, settled.tfr_base, settled.irpef_base) == (
        _D(0),
        _D(0),
        _D(0),
    )


def test_no_qualifying_month_settles_nothing() -> None:
    """Zero months accrued pays no earning and needs no policy."""
    assert _settle((_accrual(ExtraMonthKind.THIRTEENTH, 0),)) == ExtraMonthSettlement()


def test_the_settlement_adds_to_the_bases_and_issues_of_the_run() -> None:
    """Each base grows by the settled amount; the issues are appended."""
    issue = CalculationIssue(
        code="x",
        capability="base_salary",
        message="m",
        status=CalculationStatus.INCOMPLETE,
    )
    totals = _EventTotals(
        inps_base=_D(10),
        tfr_base=_D(20),
        irpef_base=_D(30),
        fringe_value=_D(0),
        fringe_inps=_D(0),
        fringe_irpef=_D(0),
        substitute_base=_D(0),
    )
    settled = ExtraMonthSettlement(
        inps_base=_D(1), tfr_base=_D(2), irpef_base=_D(3), issues=(issue,)
    )

    added = settled.added_to(totals)

    assert (added.inps_base, added.tfr_base, added.irpef_base) == (
        _D(11),
        _D(22),
        _D(33),
    )
    assert added.issues == (issue,)


@pytest.mark.parametrize("kind", list(ExtraMonthKind))
def test_the_month_number_follows_the_kind(kind: ExtraMonthKind) -> None:
    """A quattordicesima is month 14, any other extra month 13."""
    (item,) = _earnings(_settle((_accrual(kind, 12),)))

    assert item.month_number == (14 if kind is ExtraMonthKind.FOURTEENTH else 13)
