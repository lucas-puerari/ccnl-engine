"""The eight totals of a payslip, read from a result and compared."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Final

from ccnl_engine.ledger.models import AccountKind

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.period.results import PeriodResult

__all__ = ["TOTALS", "TotalDifference", "TotalsComparison", "read_total"]

_ZERO: Final = Decimal(0)
_A = AccountKind


def _accounts(
    *plus: AccountKind, minus: tuple[AccountKind, ...] = ()
) -> Callable[[PeriodResult], Decimal]:
    def read(result: PeriodResult) -> Decimal:
        def total(kinds: tuple[AccountKind, ...]) -> Decimal:
            entries = result.ledger_entries
            return sum((e.amount for e in entries if e.account in kinds), _ZERO)

        return total(plus) - total(minus)

    return read


def _base_salary(result: PeriodResult) -> Decimal:
    items = result.pay_items
    return sum((i.amount for i in items if i.kind == "base_salary_earning"), _ZERO)


#: How each total of the definition of done is read from a run: the base
#: salary of the tables, the gross, the INPS of each side, the taxes withheld
#: net of refunds before credits, the net, the TFR accrued wherever it goes,
#: and the employer cost.
TOTALS: Final[dict[str, Callable[[PeriodResult], Decimal]]] = {
    "base_salary": _base_salary,
    "gross": lambda r: r.period_gross,
    "employee_contributions": _accounts(_A.EMPLOYEE_CONTRIBUTIONS),
    "employer_contributions": _accounts(_A.EMPLOYER_CONTRIBUTIONS),
    "tax": _accounts(
        _A.ORDINARY_TAX,
        _A.SURTAX,
        _A.SUBSTITUTE_TAX,
        _A.SEPARATE_TAX,
        minus=(_A.TAX_REFUNDS, _A.SURTAX_REFUNDS),
    ),
    "net": lambda r: r.period_net,
    "tfr": _accounts(_A.TFR_ACCRUAL, _A.PENSION_FUND_TFR, _A.TFR_TREASURY_FUND),
    "employer_cost": lambda r: r.period_employer_cost,
}


def read_total(result: PeriodResult, total: str) -> Decimal:
    """Return one total of ``result``, by its name in :data:`TOTALS`.

    Returns:
        The amount of the run; a name outside :data:`TOTALS` raises
        ``KeyError``.
    """
    return TOTALS[total](result)


@dataclass(frozen=True)
class TotalDifference:
    """One total of a run next to the value it is compared with.

    Attributes:
        total: Name of the total, a key of :data:`TOTALS`.
        engine: What the engine computed.
        expected: The value of the other output.
        difference: ``engine - expected``.
        within_tolerance: Whether the difference is within the tolerance.
    """

    total: str
    engine: Decimal
    expected: Decimal
    difference: Decimal
    within_tolerance: bool


@dataclass(frozen=True)
class TotalsComparison:
    """The totals of a run compared with another output.

    Attributes:
        differences: One entry per total compared, in the order given.
        tolerance: The largest absolute difference that counts as a match.
        payable: Whether the engine's result is payable as it is.
    """

    differences: tuple[TotalDifference, ...]
    tolerance: Decimal
    payable: bool

    @property
    def matches(self) -> bool:
        """Whether every compared total is within the tolerance."""
        return all(d.within_tolerance for d in self.differences)
