"""PayrollRun: a single payroll computation unit with an explicit run kind.

A :class:`PayrollRun` names one payslip computation within a payroll year.
The ``run_kind`` axis distinguishes ordinary monthly cedolini from the
thirteenth/fourteenth-month payments and the special adjustment and
termination runs, enabling :func:`calculate_year` to generate the correct
run sequence from the CCNL calendar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

__all__ = ["PayrollRun", "RunKind"]


class RunKind(StrEnum):
    """Classification of a payroll run.

    Members compare equal to their string values, so ``RunKind.REGULAR == "regular"``
    is ``True`` and existing comparisons with plain strings continue to work.
    """

    REGULAR = "regular"
    THIRTEENTH = "thirteenth"
    FOURTEENTH = "fourteenth"
    ADJUSTMENT = "adjustment"
    TERMINATION = "termination"


@dataclass(frozen=True)
class PayrollRun:
    """Identity and classification of one payroll computation.

    Attributes:
        run_kind: Classification of the run type:

            - ``RunKind.REGULAR`` — ordinary monthly salary period.
            - ``RunKind.THIRTEENTH`` — tredicesima mensilità.
            - ``RunKind.FOURTEENTH`` — quattordicesima mensilità.
            - ``RunKind.ADJUSTMENT`` — conguaglio correction run.
            - ``RunKind.TERMINATION`` — cessazione run including TFR settlement.

        month: Calendar month (1-12) in which the run is paid.
        year: Tax year this run belongs to.
        run_id: Unique, deterministic identifier derived from year, month and
            kind, e.g. ``"2026-01-regular"`` or ``"2026-12-thirteenth"``.
            Computed automatically; do not pass to the constructor.
    """

    run_kind: RunKind
    month: int
    year: int
    run_id: str = field(init=False, default="")

    def __post_init__(self) -> None:  # noqa: D105
        try:
            object.__setattr__(self, "run_kind", RunKind(self.run_kind))
        except ValueError:
            valid = [k.value for k in RunKind]
            msg = f"run_kind must be one of {valid}; got {self.run_kind!r}"
            raise ValueError(msg) from None
        if not 1 <= self.month <= 12:
            msg = f"month must be 1-12; got {self.month}"
            raise ValueError(msg)
        if self.year < 1970:
            msg = f"year must be >= 1970; got {self.year}"
            raise ValueError(msg)
        object.__setattr__(
            self, "run_id", f"{self.year}-{self.month:02d}-{self.run_kind}"
        )

    @classmethod
    def regular(cls, year: int, month: int) -> PayrollRun:
        """Create a regular monthly run for the given year and month.

        Args:
            year: Tax year.
            month: Calendar month (1-12).

        Returns:
            A :class:`PayrollRun` with ``run_kind=RunKind.REGULAR`` and a
            deterministic ``run_id``.
        """
        return cls(run_kind=RunKind.REGULAR, month=month, year=year)

    @classmethod
    def thirteenth(cls, year: int, payment_month: int) -> PayrollRun:
        """Create a tredicesima run paid in the given calendar month.

        Args:
            year: Tax year.
            payment_month: Calendar month in which the tredicesima is paid.

        Returns:
            A :class:`PayrollRun` with ``run_kind=RunKind.THIRTEENTH``.
        """
        return cls(run_kind=RunKind.THIRTEENTH, month=payment_month, year=year)

    @classmethod
    def fourteenth(cls, year: int, payment_month: int) -> PayrollRun:
        """Create a quattordicesima run paid in the given calendar month.

        Args:
            year: Tax year.
            payment_month: Calendar month in which the quattordicesima is paid.

        Returns:
            A :class:`PayrollRun` with ``run_kind=RunKind.FOURTEENTH``.
        """
        return cls(run_kind=RunKind.FOURTEENTH, month=payment_month, year=year)
