"""PayrollRun: a single payroll computation unit with an explicit run kind.

A :class:`PayrollRun` names one payslip computation within a payroll year.
The ``run_kind`` axis distinguishes ordinary monthly cedolini from the
thirteenth/fourteenth-month payments and the special adjustment and
termination runs, enabling :func:`calculate_year` to generate the correct
run sequence from the CCNL calendar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum

from ccnl_engine.shared.domain.validation import (
    parse_enum,
    reject,
    require_int,
)

__all__ = ["PayrollRun", "PayrollRunId", "RunKind", "run_identifier"]

_MIN_YEAR = 1970
_RUN_ID_PATTERN = re.compile(r"(\d{4})-(\d{2})-([a-z]+)")


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

    @property
    def consumes_withholding_slot(self) -> bool:
        """Whether a run of this kind takes one IRPEF withholding slot.

        Every payslip does, except an adjustment run, which corrects a run
        already closed without opening a new withholding instalment.
        """
        return self is not RunKind.ADJUSTMENT

    @property
    def rank_in_month(self) -> int:
        """Position of a run of this kind among the runs of its month.

        The regular payslip comes first, the extra months follow it
        (:meth:`~ccnl_engine.payroll.domain.schedule.PayrollSchedule\
.from_calendar`), a termination run closes the month.  An adjustment run
        corrects a run already closed and is not ordered.
        """
        return _RANK_IN_MONTH[self]


_RANK_IN_MONTH: dict[RunKind, int] = {
    RunKind.REGULAR: 0,
    RunKind.THIRTEENTH: 1,
    RunKind.FOURTEENTH: 1,
    RunKind.TERMINATION: 2,
    RunKind.ADJUSTMENT: 3,
}


_FEATURE = "payroll_run"
_EXTRA_MONTH_KINDS = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})


def _check_year_month(owner: str, year: object, month: object) -> None:
    """Reject a month outside 1-12 or a year before 1970."""
    require_int(month, f"{owner}.month", feature=_FEATURE, minimum=1, maximum=12)
    require_int(year, f"{owner}.year", feature=_FEATURE, minimum=_MIN_YEAR)


def _run_kind(value: object, path: str) -> RunKind:
    """Return ``value`` as a :class:`RunKind`.

    Returns:
        The run kind named by ``value``.
    """
    return parse_enum(value, RunKind, path, feature=_FEATURE)


@dataclass(frozen=True)
class PayrollRunId:
    """Typed identifier of a payroll run: year, month and kind of the run.

    The text form is ``"{year}-{month:02d}-{kind}"``, e.g.
    ``"2026-12-thirteenth"``, as in :attr:`PayrollRun.run_id`.  A year has
    at most one run per (month, kind), so no sequence number is needed.

    Attributes:
        year: Year of the run month (the competence year).  The tax year of
            the run follows from its payment date and can be later.
        month: Run month, 1-12.
        kind: Kind of the run.
    """

    year: int
    month: int
    kind: RunKind

    def __post_init__(self) -> None:
        """Normalise ``kind`` and validate the month and the year.

        A kind that is not a run kind, a month outside 1-12 or a year
        before 1970 raises
        :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
        """
        object.__setattr__(self, "kind", _run_kind(self.kind, "PayrollRunId.kind"))
        _check_year_month("PayrollRunId", self.year, self.month)

    def __str__(self) -> str:
        """Return the text form.

        Returns:
            ``"{year}-{month:02d}-{kind}"``, e.g. ``"2026-01-regular"``.
        """
        return f"{self.year}-{self.month:02d}-{self.kind}"

    @classmethod
    def parse(cls, text: str) -> PayrollRunId:
        """Parse the text form ``"{year}-{month:02d}-{kind}"``.

        Args:
            text: A run id such as ``"2026-06-fourteenth"``.

        Returns:
            The typed identifier.  A ``text`` that is not a well-formed run
            id raises
            :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
        """
        match = _RUN_ID_PATTERN.fullmatch(text) if isinstance(text, str) else None
        if match is None:
            reject(
                "PayrollRunId",
                "a run id such as '2026-01-regular'",
                text,
                feature=_FEATURE,
            )
        year, month, kind = match.groups()
        return cls(
            year=int(year), month=int(month), kind=_run_kind(kind, "PayrollRunId.kind")
        )

    @property
    def order_key(self) -> tuple[int, int, int]:
        """Key ordering the runs as they are paid: year, month, kind rank."""
        return (self.year, self.month, self.kind.rank_in_month)

    @property
    def payment_key(self) -> tuple[int, int, RunKind]:
        """Key of what the run pays, closed once per employment.

        A regular, termination or adjustment run pays its month; a
        tredicesima or quattordicesima pays the extra month of its year,
        whatever month it is paid in: the quattordicesima of 2027 is the
        same entitlement paid in June or in July.
        """
        month = 0 if self.kind in _EXTRA_MONTH_KINDS else self.month
        return (self.year, month, self.kind)


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

        month: Calendar month (1-12) of the run.
        year: Year of the run month.  The tax year follows from the payment
            date (:class:`~ccnl_engine.payroll.domain.tax_year.TaxYearPolicy`)
            and can be the next year when the run is paid late.
        run_id: Unique, deterministic identifier derived from year, month and
            kind, e.g. ``"2026-01-regular"`` or ``"2026-12-thirteenth"``.
            Computed automatically; do not pass to the constructor.
    """

    run_kind: RunKind
    month: int
    year: int
    run_id: str = field(init=False, default="")

    def __post_init__(self) -> None:  # noqa: D105
        object.__setattr__(
            self, "run_kind", _run_kind(self.run_kind, "PayrollRun.run_kind")
        )
        _check_year_month("PayrollRun", self.year, self.month)
        object.__setattr__(self, "run_id", str(self.identifier))

    @property
    def identifier(self) -> PayrollRunId:
        """Typed identifier of the run; ``str()`` of it is :attr:`run_id`."""
        return PayrollRunId(year=self.year, month=self.month, kind=self.run_kind)

    @classmethod
    def of(cls, run_id: PayrollRunId) -> PayrollRun:
        """Return the run ``run_id`` identifies.

        Returns:
            A :class:`PayrollRun` whose :attr:`identifier` is ``run_id``.
        """
        return cls(run_kind=run_id.kind, month=run_id.month, year=run_id.year)

    @classmethod
    def regular(cls, year: int, month: int) -> PayrollRun:
        """Create a regular monthly run for the given year and month.

        Args:
            year: Year of the run month.
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
            year: Year of the run month.
            payment_month: Calendar month in which the tredicesima is paid.

        Returns:
            A :class:`PayrollRun` with ``run_kind=RunKind.THIRTEENTH``.
        """
        return cls(run_kind=RunKind.THIRTEENTH, month=payment_month, year=year)

    @classmethod
    def fourteenth(cls, year: int, payment_month: int) -> PayrollRun:
        """Create a quattordicesima run paid in the given calendar month.

        Args:
            year: Year of the run month.
            payment_month: Calendar month in which the quattordicesima is paid.

        Returns:
            A :class:`PayrollRun` with ``run_kind=RunKind.FOURTEENTH``.
        """
        return cls(run_kind=RunKind.FOURTEENTH, month=payment_month, year=year)


def run_identifier(run: PayrollRun | None, year: int, month: int) -> PayrollRunId:
    """Return the identifier of the run a period calculation closes.

    Args:
        run: The run of the calculation, ``None`` for a bare period.
        year: Year of the competence period.
        month: Month of the competence period.

    Returns:
        ``run.identifier``, or the regular run of the period without a run.
    """
    if run is not None:
        return run.identifier
    return PayrollRunId(year=year, month=month, kind=RunKind.REGULAR)
