"""Default cases of the facts of a fixed-term contract.

Part of
``DEFAULT_CASES``: the explicit
Concia D2 of 2026 hired on a fixed-term contract, whose sector charges the
NASpI surcharge of L. 92/2012 art. 2 c. 28 and its increase per renewal.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.inputs import FixedTerm, NaspiExclusion
from tests.knowledge.ccnl_engine.payroll.period.builders_explicit_facts import CONCIA_D2

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ccnl_engine import Employment

__all__ = ["fixed_term_cases"]

#: A first fixed-term contract with no exclusion of L. 92/2012 art. 2 c. 29.
_FIXED_TERM = FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE)


def fixed_term_cases[C](
    pair: Callable[[Employment, Employment, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the fixed-term facts, built with ``pair``.

    Returns:
        The cases keyed ``Type.field``.
    """
    stated = replace(CONCIA_D2, contract_type=_FIXED_TERM)
    return {
        "FixedTerm.renewals": (
            pair(
                stated,
                replace(
                    CONCIA_D2,
                    contract_type=FixedTerm(naspi_exclusion=NaspiExclusion.NONE),
                ),
                "renewals",
            ),
        ),
        "FixedTerm.naspi_exclusion": (
            pair(
                stated,
                replace(CONCIA_D2, contract_type=FixedTerm(renewals=0)),
                "naspi_exclusion",
            ),
        ),
    }
