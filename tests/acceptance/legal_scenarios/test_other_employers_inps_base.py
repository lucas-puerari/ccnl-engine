"""The INPS base of the worker's other employments toward the massimale.

L. 335/1995 art. 2 c. 18 caps the IVS contribution base of a worker first
enrolled from 1996 at an annual massimale; the massimale is per worker, so
the bases of the earlier and simultaneous employments of the year count
toward it (INPS circ. 237/2016 par. 3.1).  The Concia D2 of
:mod:`tests.fixtures.explicit_facts` was first enrolled in 2005, so the
massimale applies.  No amount is expected from the engine: the properties
hold for any massimale below 1,000,000 EUR, the base the other employments
are stated with.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.inputs import InpsBaseYtd, OpeningBalances
from ccnl_engine.results import BlockerCode
from tests.acceptance.legal_scenarios._support import ENGINE
from tests.fixtures.explicit_facts import regular_run

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_ZERO = Decimal(0)
_IVS = ("ivs_employee", "ivs_employer")


def _january(other_employers: Decimal | None) -> PeriodResult:
    """Return January 2026, the first run, with the other employments stated.

    The current-year facts are left out, so the base of the other
    employments is the one the imported state states.

    Returns:
        The January run of the Concia D2 hired on 1 January 2026.
    """
    opening = ENGINE.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            inps_bases=(InpsBaseYtd(2026, _ZERO, other_employers),),
            recoveries=(),
            surtax_obligations=(),
        )
    )
    request = replace(regular_run(1, opening_state=opening), current_year=None)
    return ENGINE.calculate_period(request)


def _ivs(result: PeriodResult) -> dict[str, tuple[Decimal, Decimal]]:
    return {
        c.name: (c.base, c.amount)
        for c in result.contribution_breakdown.components
        if c.name in _IVS
    }


def _missing_other_employers(result: PeriodResult) -> bool:
    return any(
        b.code is BlockerCode.MISSING_FACT and b.detail == "other_employers"
        for b in result.blockers
    )


def test_other_employments_above_the_massimale_leave_no_ivs_base() -> None:
    """1,000,000 EUR of other employments exhaust the massimale of the year."""
    result = _january(Decimal(1_000_000))

    assert _ivs(result) == dict.fromkeys(_IVS, (_ZERO, _ZERO))
    assert not _missing_other_employers(result)


def test_no_other_employment_contributes_the_whole_base() -> None:
    """With none stated, the IVS base is the base of the run."""
    result = _january(_ZERO)

    assert set(_ivs(result)) == set(_IVS)
    assert all(
        base > _ZERO and amount > _ZERO for base, amount in _ivs(result).values()
    )
    assert not _missing_other_employers(result)


def test_an_unknown_base_blocks_and_simulates_this_employment_alone() -> None:
    """Unknown is not zero: the run computes as if none and is not payable."""
    unknown = _january(None)

    assert _missing_other_employers(unknown)
    assert not unknown.is_payable
    assert _ivs(unknown) == _ivs(_january(_ZERO))
