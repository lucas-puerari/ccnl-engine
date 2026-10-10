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

from ccnl_engine.payroll.domain.run_kind import RunKind, check_year_month, run_kind
from ccnl_engine.validation import reject, require_int

__all__ = ["PayrollRun", "PayrollRunId", "RunKind", "run_identifier"]

_FEATURE = "payroll_run"
#: A sequence suffix is canonical: 2 or more, without a leading zero.
_RUN_ID_PATTERN = re.compile(r"(\d{4})-(\d{2})-([a-z]+)(?:-([2-9]|[1-9]\d+))?")
_EXTRA_MONTH_KINDS = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})


def _check_sequence(owner: str, kind: RunKind, sequence: object) -> None:
    """Reject a sequence below 1, or above 1 on a kind that closes once."""
    require_int(sequence, f"{owner}.sequence", feature=_FEATURE, minimum=1)
    if sequence != 1 and not kind.repeats_in_month:
        reject(
            f"{owner}.sequence",
            f"1: a {kind} run closes once per month",
            sequence,
            feature=_FEATURE,
        )


@dataclass(frozen=True)
class PayrollRunId:
    """Typed identifier of a payroll run: year, month, kind and sequence.

    The text form is ``"{year}-{month:02d}-{kind}"``, e.g.
    ``"2026-12-thirteenth"``, as in :attr:`PayrollRun.run_id`.  A month has
    at most one run of each kind, except adjustment runs: the second and
    later adjustments of a month carry their sequence number as a suffix,
    e.g. ``"2026-12-adjustment-2"``.

    Attributes:
        year: Year of the run month (the competence year).  The tax year of
            the run follows from its payment date and can be later.
        month: Run month, 1-12.
        kind: Kind of the run.
        sequence: Number of the run among the runs of its kind and month,
            from 1.  Above 1 only for an adjustment run.
    """

    year: int
    month: int
    kind: RunKind
    sequence: int = 1

    def __post_init__(self) -> None:
        """Normalise ``kind`` and validate the month, year and sequence.

        A kind that is not a run kind, a month outside 1-12, a year before
        1970, a sequence below 1 or a sequence above 1 on a kind other than
        an adjustment raises
        :class:`~ccnl_engine.errors.InvalidInputError`.
        """
        object.__setattr__(self, "kind", run_kind(self.kind, "PayrollRunId.kind"))
        check_year_month("PayrollRunId", self.year, self.month)
        _check_sequence("PayrollRunId", self.kind, self.sequence)

    def __str__(self) -> str:
        """Return the text form.

        Returns:
            ``"{year}-{month:02d}-{kind}"``, e.g. ``"2026-01-regular"``,
            followed by ``"-{sequence}"`` when the sequence is above 1.
        """
        suffix = "" if self.sequence == 1 else f"-{self.sequence}"
        return f"{self.year}-{self.month:02d}-{self.kind}{suffix}"

    @classmethod
    def parse(cls, text: str) -> PayrollRunId:
        """Parse the text form of :meth:`__str__`.

        Args:
            text: A run id such as ``"2026-06-fourteenth"`` or
                ``"2026-12-adjustment-2"``.

        Returns:
            The typed identifier.  A ``text`` that is not a well-formed run
            id, or not in its canonical form (a ``"-1"`` or ``"-02"``
            suffix), raises
            :class:`~ccnl_engine.errors.InvalidInputError`.
        """
        match = _RUN_ID_PATTERN.fullmatch(text) if isinstance(text, str) else None
        if match is None:
            reject(
                "PayrollRunId",
                "a run id such as '2026-01-regular'",
                text,
                feature=_FEATURE,
            )
        year, month, kind, sequence = match.groups()
        return cls(
            year=int(year),
            month=int(month),
            kind=run_kind(kind, "PayrollRunId.kind"),
            sequence=1 if sequence is None else int(sequence),
        )

    @property
    def order_key(self) -> tuple[int, int, int, int]:
        """Key ordering the runs as they are paid: year, month, kind rank, sequence."""
        return (self.year, self.month, self.kind.rank_in_month, self.sequence)

    @property
    def payment_key(self) -> tuple[int, int, RunKind, int]:
        """Key of what the run pays, closed once per employment.

        A regular, termination or adjustment run pays its month, an
        adjustment once per sequence number; a tredicesima or
        quattordicesima pays the extra month of its year, whatever month it
        is paid in: the quattordicesima of 2027 is the same entitlement paid
        in June or in July.
        """
        month = 0 if self.kind in _EXTRA_MONTH_KINDS else self.month
        return (self.year, month, self.kind, self.sequence)


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
        sequence: Number of the run among the runs of its kind and month,
            from 1.  Above 1 only for a second or later adjustment run of
            the month (:meth:`adjustment`).
        run_id: Unique, deterministic identifier derived from year, month,
            kind and sequence, e.g. ``"2026-01-regular"`` or
            ``"2026-12-adjustment-2"``.  Computed automatically; do not pass
            to the constructor.
    """

    run_kind: RunKind
    month: int
    year: int
    sequence: int = 1
    run_id: str = field(init=False, default="")

    def __post_init__(self) -> None:  # noqa: D105
        object.__setattr__(
            self, "run_kind", run_kind(self.run_kind, "PayrollRun.run_kind")
        )
        check_year_month("PayrollRun", self.year, self.month)
        _check_sequence("PayrollRun", self.run_kind, self.sequence)
        object.__setattr__(self, "run_id", str(self.identifier))

    @property
    def identifier(self) -> PayrollRunId:
        """Typed identifier of the run; ``str()`` of it is :attr:`run_id`."""
        return PayrollRunId(
            year=self.year,
            month=self.month,
            kind=self.run_kind,
            sequence=self.sequence,
        )

    @classmethod
    def of(cls, run_id: PayrollRunId) -> PayrollRun:
        """Return the run ``run_id`` identifies.

        Returns:
            A :class:`PayrollRun` whose :attr:`identifier` is ``run_id``.
        """
        return cls(
            run_kind=run_id.kind,
            month=run_id.month,
            year=run_id.year,
            sequence=run_id.sequence,
        )

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

    @classmethod
    def adjustment(cls, year: int, month: int, sequence: int = 1) -> PayrollRun:
        """Create an adjustment run correcting a run of the given month.

        Args:
            year: Year of the run month.
            month: Calendar month (1-12) of the run corrected.
            sequence: Number of the adjustment within the month: 1 for the
                first, 2 for a second correction of the same month, and so
                on.  Each closes once.

        Returns:
            A :class:`PayrollRun` with ``run_kind=RunKind.ADJUSTMENT``.
        """
        return cls(
            run_kind=RunKind.ADJUSTMENT, month=month, year=year, sequence=sequence
        )


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
