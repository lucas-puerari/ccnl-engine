"""State entering a payroll run: tax year state and lasting obligations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, final

from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState


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
            esente.
    """

    SCHEMA_VERSION: ClassVar[int] = 3

    ytd: TaxYearState = field(default_factory=TaxYearState)
    obligations: EmploymentObligations = field(default_factory=EmploymentObligations)

    def __post_init__(self) -> None:
        """Reject an obligation opened after the tax year of the state.

        Raises:
            ValueError: When a recovery originates in a year later than
                ``ytd.tax_year``.
        """
        latest = self.obligations.latest_tax_year
        if self.tax_year is not None and latest is not None and latest > self.tax_year:
            msg = (
                f"obligations include a recovery opened in {latest}, after the "
                f"tax year of the state ({self.tax_year})"
            )
            raise ValueError(msg)

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
