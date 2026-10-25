"""Compare the totals of a run with the payslip of another payroll."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.comparison.totals.models import (
    TOTALS,
    TotalDifference,
    TotalsComparison,
    read_total,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_decimal

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.period.results import PeriodResult

__all__ = ["compare_totals"]

_CENT = Decimal("0.01")
_FEATURE = "compare_totals"


def compare_totals(
    result: PeriodResult,
    expected: Mapping[str, Decimal],
    *,
    tolerance: Decimal = _CENT,
) -> TotalsComparison:
    """Compare the totals of ``result`` with ``expected``, at ``tolerance``.

    The other output is, for example, the payslip a payroll provider
    computed from the same facts: build the request with
    :func:`~ccnl_engine.inputs.request_from_json` or the input types, run
    it, and pass the provider's totals.  Only the totals named in
    ``expected`` are compared; see the perimeter of each in the trust pages.

    Args:
        result: A run of the engine.
        expected: The other output's value of each total to compare, keyed
            by a name of :data:`~ccnl_engine.comparison.totals.models.TOTALS`.
        tolerance: The largest absolute difference that counts as a match.

    Returns:
        One difference per total, in the order of ``expected``, and whether
        the engine's result is payable.

    Raises:
        InvalidInputError: When a name is not a total, a value is not a
            ``Decimal``, or the tolerance is negative.
    """
    unknown = sorted(set(expected) - set(TOTALS))
    if unknown:
        msg = f"not a total: {', '.join(unknown)}; totals: {', '.join(TOTALS)}"
        raise InvalidInputError(msg, field="expected", feature=_FEATURE)
    require_decimal(tolerance, "tolerance", feature=_FEATURE, minimum=Decimal(0))
    differences = []
    for total, value in expected.items():
        require_decimal(value, f"expected.{total}", feature=_FEATURE)
        engine = read_total(result, total)
        gap = engine - value
        differences.append(
            TotalDifference(total, engine, value, gap, abs(gap) <= tolerance)
        )
    return TotalsComparison(tuple(differences), tolerance, result.is_payable)
