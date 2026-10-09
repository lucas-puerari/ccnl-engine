"""Default cases of the facts of a pension fund enrolment.

Part of :data:`tests.fixtures.default_cases.DEFAULT_CASES`: the explicit
Concia D2 moved to Metalmeccanico Federmeccanica C3 and enrolled in Cometa,
whose employer rate is higher for a young member.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.inputs import PensionFundEnrolment
from tests.fixtures.explicit_facts import CONCIA_D2

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ccnl_engine import Employment

__all__ = ["pension_cases"]


def _cometa(young_member: bool | None) -> Employment:
    enrolment = PensionFundEnrolment(
        "COMETA", Decimal("0.012"), tfr_to_fund=True, young_member=young_member
    )
    return replace(
        CONCIA_D2,
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        pension_fund=enrolment,
    )


def pension_cases[C](
    pair: Callable[[Employment, Employment, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the enrolment facts, built with ``pair``.

    Returns:
        The cases keyed ``Type.field``.
    """
    return {
        "PensionFundEnrolment.young_member": (
            pair(_cometa(True), _cometa(None), "young_member"),
            pair(_cometa(False), _cometa(None), "young_member"),
        ),
    }
