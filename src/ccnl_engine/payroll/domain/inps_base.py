"""INPS contribution base of one competence year, toward the IVS massimale.

INPS contributions follow competence: the pay of a month is declared and
contributed in the denuncia of that month, whatever day it is paid, and the
massimale of L. 335/1995 art. 2 c. 18 caps the base of a calendar year
(INPS circ. 237/2016 par. 2.1 and 3.1).  December 2026 paid on 13 January
2027 is IRPEF income of 2027 but INPS base of 2026, so the base is counted
per competence year in the accrual state, which survives the change of tax
year, and not in the tax cash state.

The massimale is per worker, not per employment: the bases of earlier and
simultaneous employments of the same year count toward it (circ. 237/2016
par. 3.1), on the certificate of the earlier employer or the worker's
declaration.  They are held apart from the base of this employment, which
alone is contributed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import final

from ccnl_engine.shared.domain.validation import require_decimal, require_int

__all__ = ["InpsBaseYtd"]

_ZERO = Decimal(0)
_FEATURE = "inps_base"


@final
@dataclass(frozen=True)
class InpsBaseYtd:
    """INPS base of one competence year that counts toward the massimale.

    Attributes:
        year: The competence year.
        own: INPS base of the runs of this employment of :attr:`year`.
        other_employers: INPS base of the worker's other employments of
            :attr:`year`, earlier or simultaneous, as certified (CU) or
            declared by the worker.  It counts toward the massimale and is
            never contributed by this employer.

    Raises:
        InvalidInputError: When a field is not of its type or an amount is
            negative or not finite.
    """

    year: int
    own: Decimal = _ZERO
    other_employers: Decimal = _ZERO

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.year, "InpsBaseYtd.year", feature=_FEATURE, minimum=1970, maximum=9999
        )
        for name in ("own", "other_employers"):
            require_decimal(
                getattr(self, name),
                f"InpsBaseYtd.{name}",
                feature=_FEATURE,
                minimum=_ZERO,
            )

    @property
    def total(self) -> Decimal:
        """Base of the year toward the massimale: own and other employers."""
        return self.own + self.other_employers

    def plus(self, amount: Decimal) -> InpsBaseYtd:
        """Return the base after a run of this employment adds ``amount``.

        Returns:
            A new base with ``own`` raised by ``amount``.
        """
        return InpsBaseYtd(self.year, self.own + amount, self.other_employers)
