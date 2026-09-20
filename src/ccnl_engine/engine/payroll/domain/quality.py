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


class LimitationSeverity(StrEnum):
    """Impact severity of an engine limitation."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LimitationIntegrationStatus(StrEnum):
    """Whether the limitation amount is folded into the totals."""

    NOT_INTEGRATED = "not_integrated"
    PARTIALLY_INTEGRATED = "partially_integrated"
    INTEGRATED = "integrated"


@dataclass(frozen=True)
class Limitation:
    """A machine-readable engine or dataset limitation.

    Attributes:
        code: Snake_case identifier for this limitation type.
        affected_component: The feature or component the limitation applies to.
        applicability_predicate: Named condition under which this limitation
            applies (e.g. ``"always"``).
        severity: How materially the limitation affects the result.
        impact_axis: Accounting axes affected (subset of ``gross``,
            ``contribution``, ``tax``, ``net``, ``cost``).
        integration_status: Whether the limitation amount is folded into
            the period totals.
        remediation: Human-readable description and remediation guidance.
        source: Normative or data reference for the limitation.
    """

    code: str
    affected_component: str
    applicability_predicate: str
    severity: LimitationSeverity
    impact_axis: tuple[str, ...]
    integration_status: LimitationIntegrationStatus
    remediation: str
    source: str = ""

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict.

        Returns:
            Dict with tuple as list, StrEnum fields as strings.
        """
        return {
            "code": self.code,
            "affected_component": self.affected_component,
            "applicability_predicate": self.applicability_predicate,
            "severity": self.severity.value,
            "impact_axis": list(self.impact_axis),
            "integration_status": self.integration_status.value,
            "remediation": self.remediation,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Limitation:
        """Reconstruct from a serialised dict.

        Returns:
            A new :class:`Limitation` with all fields restored.
        """
        raw_axis = data.get("impact_axis") or []
        if not isinstance(raw_axis, list):
            raw_axis = []
        return cls(
            code=str(data["code"]),
            affected_component=str(data["affected_component"]),
            applicability_predicate=str(data["applicability_predicate"]),
            severity=LimitationSeverity(str(data["severity"])),
            impact_axis=tuple(str(a) for a in raw_axis),
            integration_status=LimitationIntegrationStatus(
                str(data["integration_status"])
            ),
            remediation=str(data.get("remediation", "")),
            source=str(data.get("source", "")),
        )


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
