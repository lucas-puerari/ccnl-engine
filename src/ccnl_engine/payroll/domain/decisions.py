"""Calculation status, issues and decisions attached to payroll results.

A result is only as trustworthy as its weakest input.  Each capability that
cannot fully decide (an unknown table, a missing fact, an unsupported case)
records a :class:`CalculationIssue`; the result status is the worst status
implied by its issues.  A :class:`CalculationDecision` records what one
capability actually decided, from which normalized inputs and under which
rule version.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from decimal import Decimal

    from ccnl_engine.provenance.domain.source import SourceLocation

__all__ = ["CalculationDecision", "CalculationIssue", "CalculationStatus"]

_CODE_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


class CalculationStatus(StrEnum):
    """How far a calculation result can be relied upon.

    Members are listed from least to most severe.  Compare them with
    :attr:`severity` or combine them with :meth:`worst`; the string values
    do not sort in severity order.

    Attributes:
        FINAL: Every capability decided from known rules and facts.
        PROVISIONAL: Computed, but at least one decision rests on an
            assumption that may change the amounts once confirmed.
        INCOMPLETE: At least one amount could not be determined; the
            result must not be paid as is.
        REJECTED: The inputs cannot produce a meaningful result.
    """

    FINAL = "final"
    PROVISIONAL = "provisional"
    INCOMPLETE = "incomplete"
    REJECTED = "rejected"

    @property
    def severity(self) -> int:
        """Rank of this status, ``0`` for final up to ``3`` for rejected."""
        return _SEVERITY[self]

    @classmethod
    def worst(cls, statuses: Iterable[CalculationStatus]) -> CalculationStatus:
        """Return the most severe status in ``statuses``.

        Args:
            statuses: Statuses to combine, possibly empty.

        Returns:
            The status with the highest :attr:`severity`, or
            :attr:`FINAL` when ``statuses`` is empty.
        """
        return max(statuses, key=_SEVERITY.__getitem__, default=cls.FINAL)


_SEVERITY: dict[CalculationStatus, int] = {
    status: rank for rank, status in enumerate(CalculationStatus)
}


def _require_code(value: str, name: str) -> None:
    if not _CODE_PATTERN.fullmatch(value):
        msg = f"{name} must be lower snake case (e.g. 'unknown_table'); got {value!r}"
        raise ValueError(msg)


def _require_text(value: str, name: str) -> None:
    if not value:
        msg = f"{name} must not be empty"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class CalculationIssue:
    """A condition that lowers the status of a calculation result.

    Attributes:
        code: Stable machine-readable identifier in lower snake case, e.g.
            ``"surtax_table_unknown"``.  Callers may branch on it.
        message: Human-readable explanation for the caller.
        status: Status the issue implies for the result that carries it.
        source: Normative source behind the issue, when one applies.

    Raises:
        ValueError: When ``code`` is not lower snake case or ``message``
            is empty.
    """

    code: str
    message: str
    status: CalculationStatus
    source: SourceLocation | None = None

    def __post_init__(self) -> None:  # noqa: D105
        _require_code(self.code, "code")
        _require_text(self.message, "message")


@dataclass(frozen=True, slots=True)
class CalculationDecision:
    """What one capability decided in a calculation, and why.

    Attributes:
        capability: Catalog feature name, e.g. ``"regional_surtax"``.
        status: Status implied by this decision.
        reason_code: Stable machine-readable reason in lower snake case,
            e.g. ``"table_found"``.
        rule: Identifier of the rule applied.
        rule_version: Version of the rule applied, e.g. the tax year or
            the data bundle version.
        inputs: Normalized inputs the decision was taken from.  Copied and
            read-only after construction.
        source: Normative source of the rule, when recorded.
        amount: Amount produced by the decision; ``None`` when the decision
            yields no amount or the amount is unknown.

    Raises:
        ValueError: When ``reason_code`` is not lower snake case, when
            ``capability``, ``rule`` or ``rule_version`` is empty, or when
            ``amount`` is not finite.
    """

    capability: str
    status: CalculationStatus
    reason_code: str
    rule: str
    rule_version: str
    inputs: Mapping[str, Decimal | str] = field(
        default_factory=lambda: MappingProxyType({})
    )
    source: SourceLocation | None = None
    amount: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        _require_text(self.capability, "capability")
        _require_code(self.reason_code, "reason_code")
        _require_text(self.rule, "rule")
        _require_text(self.rule_version, "rule_version")
        if self.amount is not None and not self.amount.is_finite():
            msg = f"amount must be finite; got {self.amount}"
            raise ValueError(msg)
        object.__setattr__(self, "inputs", MappingProxyType(dict(self.inputs)))
