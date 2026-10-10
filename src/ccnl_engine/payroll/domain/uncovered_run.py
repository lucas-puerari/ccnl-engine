"""A run of a year the bundle cannot compute: its pay rules are not in force."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.errors import MissingRuleError
from ccnl_engine.payroll.domain.assurance import BlockerCode, ResultBlocker

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.payment import PaymentId

__all__ = ["UncoveredRun"]


@dataclass(frozen=True, slots=True)
class UncoveredRun:
    """A run of a competence year that was not computed.

    The bundle holds no base salary of the CCNL level on the competence
    date of the run: the pay tables start later, or the date falls in a
    gap the bundle declares.  The year computes its other runs and is not
    payable (see :attr:`blocker`).  The fields are those of the
    :class:`~ccnl_engine.errors.MissingRuleError` a run of
    that date raises, rebuilt by :attr:`error`.

    Attributes:
        payment: The run and the date it would have been paid.
        ruleset: Id of the CCNL whose rule is missing.
        feature: The rule with no value (``base_salary``).
        as_of: The date the rule was read on: the competence date.
        gap_kind: Kind of the declared gap, ``None`` before the rule starts.
        detail: Why the rule has no value on :attr:`as_of`.
        remediation: What the caller can do about it.
    """

    payment: PaymentId
    ruleset: str | None
    feature: str | None
    as_of: date
    gap_kind: str | None
    detail: str
    remediation: str | None

    @classmethod
    def of(cls, payment: PaymentId, error: MissingRuleError) -> UncoveredRun:
        """Return the run left out with the error a run of its date raises.

        Returns:
            The run, with the fields of ``error``.
        """
        return cls(
            payment=payment,
            ruleset=error.ruleset,
            feature=error.feature,
            as_of=error.as_of,
            gap_kind=error.gap_kind,
            detail=error.detail,
            remediation=error.remediation,
        )

    @property
    def error(self) -> MissingRuleError:
        """The error a run of :attr:`payment` raises."""
        return MissingRuleError(
            self.detail,
            as_of=self.as_of,
            gap_kind=self.gap_kind,
            feature=self.feature,
            ruleset=self.ruleset,
            remediation=self.remediation,
        )

    @property
    def blocker(self) -> ResultBlocker:
        """The ``run_not_computed`` blocker of the run, detail its run id."""
        return ResultBlocker(
            code=BlockerCode.RUN_NOT_COMPUTED,
            feature=self.feature,
            detail=str(self.payment.run_id),
            remediation=self.remediation or self.detail,
        )
