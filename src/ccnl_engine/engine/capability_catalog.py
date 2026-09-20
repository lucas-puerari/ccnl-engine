"""Versioned catalog of fiscal capabilities declared per year."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


class CapabilityStatus(StrEnum):
    """Engine implementation status for a fiscal capability in a given year."""

    NOT_APPLICABLE = "not_applicable"
    COMPUTED = "computed"
    PARTIALLY_COMPUTED = "partially_computed"
    NOT_COMPUTED = "not_computed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CapabilityEntry:
    """One feature in the capability catalog."""

    feature: str
    status: CapabilityStatus
    description: str = ""


@dataclass(frozen=True)
class CapabilityGap:
    """A mismatch between declared and observed capability status."""

    feature: str
    declared: CapabilityStatus
    observed: str


@dataclass(frozen=True)
class CapabilityCatalog:
    """Versioned list of fiscal capabilities expected for a given fiscal year."""

    year: int
    capabilities: tuple[CapabilityEntry, ...]

    def by_feature(self, feature: str) -> CapabilityEntry | None:
        """Return the entry for *feature*, or ``None`` when absent.

        Returns:
            The matching :class:`CapabilityEntry`, or ``None``.
        """
        for cap in self.capabilities:
            if cap.feature == feature:
                return cap
        return None

    def gaps(self, observed: Mapping[str, str]) -> tuple[CapabilityGap, ...]:
        """Return entries where the observed status is worse than declared.

        Only entries where the catalog declares at minimum ``computed`` or
        ``partially_computed`` and the observed status is ``"not_computed"``
        are reported as gaps.

        Args:
            observed: Mapping of feature name to observed calculation status.

        Returns:
            Gaps in order of declaration, one per mismatched feature.
        """
        result: list[CapabilityGap] = []
        for entry in self.capabilities:
            if entry.status not in {
                CapabilityStatus.COMPUTED,
                CapabilityStatus.PARTIALLY_COMPUTED,
            }:
                continue
            obs = observed.get(entry.feature)
            if obs == "not_computed":
                result.append(
                    CapabilityGap(
                        feature=entry.feature,
                        declared=entry.status,
                        observed=obs,
                    )
                )
        return tuple(result)
