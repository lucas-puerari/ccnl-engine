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
alone is contributed here.  They count the same way toward the band of
the additional 1% IVS of D.L. 384/1992 art. 3-ter (circ. INPS 6/2026 note
10), whose conguaglio deducts the 1% already withheld on them.  Whether the
worker had other employments in the year is a fact the caller states:
``None`` is not known, ``0`` is none.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import final

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validation import require_decimal, require_int

__all__ = ["InpsBaseYtd"]

_ZERO = Decimal(0)
_FEATURE = "inps_base"


@final
@dataclass(frozen=True)
class InpsBaseYtd:
    """INPS base of one competence year, toward the massimale and the 1% band.

    Attributes:
        year: The competence year.
        own: INPS base of the runs of this employment of :attr:`year`.
        other_employers: INPS base of the worker's other employments of
            :attr:`year`, earlier or simultaneous, as certified (CU) or
            declared by the worker.  It counts toward the massimale and the
            band of the additional 1% IVS and is never contributed by this
            employer.  ``None`` means not known: a run whose contributions
            could depend on it has a ``missing_fact`` blocker; ``0`` states
            that there is none.
        additional_ivs: Additional 1% IVS (D.L. 384/1992 art. 3-ter) this
            employment withheld on the pay of :attr:`year`, net of what its
            conguagli gave back.  Negative only when a conguaglio refunded
            more than this employment withheld, giving back what other
            employers withheld (INPS circ. 156/2025 par. 5).
        other_employers_additional_ivs: Additional 1% IVS the other
            employments withheld on :attr:`other_employers`, as certified;
            the conguaglio deducts it from the 1% due on the year.  ``None``
            when not stated: with a base of other employers the conguaglio
            then cannot be settled (:attr:`other_employers_withheld_unknown`).
        month: Competence month of the latest run of this employment,
            ``None`` before the first run of :attr:`year`.
        month_base: INPS base of the runs of this employment of
            :attr:`month`: the runs of one month share its threshold of the
            additional 1% IVS.

    Raises:
        InvalidInputError: When a field is not of its type, an amount other
            than :attr:`additional_ivs` is negative, an amount is not
            finite, or :attr:`month_base` is not zero without a month.
    """

    year: int
    own: Decimal = _ZERO
    other_employers: Decimal | None = None
    additional_ivs: Decimal = _ZERO
    other_employers_additional_ivs: Decimal | None = None
    month: int | None = None
    month_base: Decimal = _ZERO

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.year, "InpsBaseYtd.year", feature=_FEATURE, minimum=1970, maximum=9999
        )
        for name in (
            "own",
            "other_employers",
            "other_employers_additional_ivs",
            "month_base",
        ):
            require_decimal(
                getattr(self, name),
                f"InpsBaseYtd.{name}",
                feature=_FEATURE,
                minimum=_ZERO,
                optional=name in {"other_employers", "other_employers_additional_ivs"},
            )
        require_decimal(
            self.additional_ivs, "InpsBaseYtd.additional_ivs", feature=_FEATURE
        )
        require_int(
            self.month,
            "InpsBaseYtd.month",
            feature=_FEATURE,
            minimum=1,
            maximum=12,
            optional=True,
        )
        if self.month is None and self.month_base != _ZERO:
            msg = "InpsBaseYtd.month_base requires a month"
            raise InvalidInputError(
                msg, field="InpsBaseYtd.month_base", feature=_FEATURE
            )

    @property
    def other_employers_known(self) -> bool:
        """Whether the base of the other employments is stated."""
        return self.other_employers is not None

    @property
    def total(self) -> Decimal:
        """Base of the year toward the massimale: own and other employers.

        An unknown base of other employers counts as zero: the run computes
        on this employment alone and reports the missing fact.
        """
        return self.own + (self.other_employers or _ZERO)

    def stating_other_employers(self, amount: Decimal) -> InpsBaseYtd:
        """Return the base with the other employers' base stated as ``amount``.

        Returns:
            A new base with ``other_employers`` set and every other field
            unchanged.
        """
        return replace(self, other_employers=amount)

    @property
    def additional_ivs_withheld(self) -> Decimal:
        """Additional 1% IVS withheld on the year by every employment.

        An unstated 1% of other employers counts as zero here; see
        :attr:`other_employers_withheld_unknown`.
        """
        others = self.other_employers_additional_ivs
        return self.additional_ivs + (_ZERO if others is None else others)

    @property
    def other_employers_withheld_unknown(self) -> bool:
        """Whether other employers have a base but their 1% is not stated."""
        others = self.other_employers or _ZERO
        return others > _ZERO and self.other_employers_additional_ivs is None

    def base_of_month(self, month: int) -> Decimal:
        """Return the INPS base this employment already declared for ``month``.

        Returns:
            :attr:`month_base` when ``month`` is :attr:`month`, else zero.
        """
        return self.month_base if month == self.month else _ZERO

    def plus(
        self, amount: Decimal, month: int, additional_ivs: Decimal = _ZERO
    ) -> InpsBaseYtd:
        """Return the base after a run of this employment of ``month``.

        Args:
            amount: INPS base of the run.
            month: Competence month of the run.
            additional_ivs: Additional 1% IVS the run withheld, negative
                when its conguaglio gave some back.

        Returns:
            A new base with ``own`` raised by ``amount`` and the base of
            ``month`` by the same amount.
        """
        return replace(
            self,
            own=self.own + amount,
            additional_ivs=self.additional_ivs + additional_ivs,
            month=month,
            month_base=self.base_of_month(month) + amount,
        )
