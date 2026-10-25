"""compare_totals: a run next to the payslip of another payroll.

Commercio level 4, January 2026, the regular run of the knowledge support:
the totals the engine computes compared with themselves match, a provider
value one cent off matches at the default tolerance, two cents do not.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import InvalidInputError
from ccnl_engine.results import TOTALS, compare_totals
from tests.knowledge.ccnl_engine.support import regular_period

_RUN = regular_period()
_CENT = Decimal("0.01")
#: What the engine computed for each total, read through the comparison.
_ENGINE = {
    d.total: d.engine
    for d in compare_totals(_RUN, dict.fromkeys(TOTALS, Decimal(0))).differences
}


def test_the_totals_of_a_run_match_themselves() -> None:
    """Every total read back is a match; the result keeps its payability."""
    comparison = compare_totals(_RUN, _ENGINE)

    assert comparison.matches
    assert [d.total for d in comparison.differences] == list(TOTALS)
    assert comparison.payable is _RUN.is_payable


def test_the_tolerance_decides_a_match() -> None:
    """One cent off is within 0.01; two cents are not, with the signed gap."""
    net = _ENGINE["net"]
    near = compare_totals(_RUN, {"net": net - _CENT})
    far = compare_totals(_RUN, {"net": net - 2 * _CENT})

    assert near.matches
    assert not far.matches
    assert far.differences[0].difference == 2 * _CENT


@pytest.mark.parametrize(
    ("expected", "tolerance", "field"),
    [
        ({"netto": Decimal(1)}, _CENT, "expected"),
        ({"net": 1500.0}, _CENT, "expected.net"),
        ({"net": Decimal(1)}, Decimal(-1), "tolerance"),
    ],
)
def test_an_invalid_comparison_is_invalid_input(
    expected: dict[str, object], tolerance: Decimal, field: str
) -> None:
    """An unknown total, a float or a negative tolerance names its field."""
    with pytest.raises(InvalidInputError) as raised:
        compare_totals(_RUN, expected, tolerance=tolerance)  # type: ignore[arg-type]
    assert raised.value.field == field
