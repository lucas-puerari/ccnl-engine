"""A run of a year the bundle cannot compute: its pay rules are not in force."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.assurance import BlockerCode, ResultBlocker

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.payment import PaymentId
    from ccnl_engine.shared.domain.errors import MissingRuleError

__all__ = ["UncoveredRun"]


@dataclass(frozen=True, slots=True)
class UncoveredRun:
    """A run of a competence year that was not computed.

    The bundle holds no base salary of the CCNL level on the competence
    date of the run: the pay tables start later, or the date falls in a
    gap the bundle declares.  The year computes its other runs and is not
    payable (see :attr:`blocker`).

    Attributes:
        payment: The run and the date it would have been paid.
        error: The error a run of that date raises, with the rule, the
            date, the gap kind and the remediation.
    """

    payment: PaymentId
    error: MissingRuleError

    @property
    def blocker(self) -> ResultBlocker:
        """The ``run_not_computed`` blocker of the run, detail its run id."""
        return ResultBlocker(
            code=BlockerCode.RUN_NOT_COMPUTED,
            feature=self.error.feature,
            detail=str(self.payment.run_id),
            remediation=self.error.remediation or self.error.detail,
        )
