"""State entering a payroll run: tax year state and lasting obligations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, final

from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import require_instances


@final
@dataclass(frozen=True)
class PeriodState:
    """State entering a payroll run: the tax year and the lasting obligations.

    Pass :meth:`zero` for the first run of an employment.  Between runs of
    one tax year, pass the ``closing_state`` of the previous run.  To open
    the next tax year, pass the closing state of the last run of the year to
    :func:`~ccnl_engine.payroll.application.close_tax_year.close_tax_year`:
    it resets :attr:`ytd` and carries :attr:`obligations`.

    Attributes:
        ytd: Counters and YTD accounts of the current tax year; they
            restart every tax year.
        obligations: Obligations that survive the change of tax year, such
            as an installment recovery of trattamento integrativo or somma
            esente, the surtax a conguaglio determined, or the IRPEF of a
            conguaglio deferred on written request.
    """

    SCHEMA_VERSION: ClassVar[int] = 5

    ytd: TaxYearState = field(default_factory=TaxYearState)
    obligations: EmploymentObligations = field(default_factory=EmploymentObligations)

    def __post_init__(self) -> None:
        """Reject a field of the wrong type or an obligation opened too late.

        Raises:
            InvalidInputError: When a field is not of its type, or a recovery
                or surtax obligation originates in a year later than
                ``ytd.tax_year``.
        """
        require_instances(
            "PeriodState",
            (
                ("ytd", self.ytd, TaxYearState, False),
                ("obligations", self.obligations, EmploymentObligations, False),
            ),
            feature="period_state",
        )
        latest = self.obligations.latest_tax_year
        if self.tax_year is not None and latest is not None and latest > self.tax_year:
            msg = (
                f"obligations include one opened in {latest}, after the "
                f"tax year of the state ({self.tax_year})"
            )
            raise InvalidInputError(
                msg, field="PeriodState.obligations", feature="period_state"
            )

    @property
    def tax_year(self) -> int | None:
        """Tax year of :attr:`ytd`; ``None`` when not yet bound to a year."""
        return self.ytd.tax_year

    @classmethod
    def zero(cls) -> PeriodState:
        """Return the state of a new employment: no run closed, no obligation.

        Returns:
            A :class:`PeriodState` with all counters and accumulators at zero.
        """
        return cls()
