"""Quality metadata types for payroll results."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CoverageStatus(StrEnum):
    """Completeness of the payroll computation."""

    PARTIAL = "partial"
    COMPLETE = "complete"


class ConfidenceLevel(StrEnum):
    """Confidence level attached to a payroll result."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class PayrollWarning:
    """A structured diagnostic from the payroll engine.

    Attributes:
        code: Machine-readable identifier (snake_case).
        message: Human-readable description.
        path: Optional field path where the issue originates.
    """

    code: str
    message: str
    path: str | None = None
