"""Decision trace emitted during period calculation for capability reporting."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TraceState(StrEnum):
    """Observed computation state for one feature in a period run."""

    COMPUTED = "computed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    UNRESOLVED = "unresolved"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class DecisionTrace:
    """Record of whether and how one payroll feature was computed in a run.

    Attributes:
        feature: Catalog feature name (e.g. ``"base_salary"``, ``"irpef"``).
        state: Computation outcome for this feature in the run.
    """

    feature: str
    state: TraceState
