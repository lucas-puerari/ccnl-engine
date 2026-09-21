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


class CapabilityGapKind(StrEnum):
    """Classification of a capability gap between declared and observed status.

    Attributes:
        NOT_COMPUTED: Feature declared computed or partially_computed, but
            observed as ``"not_computed"`` in the calculation.
        FEATURE_ABSENT: Feature declared computed or partially_computed, but
            absent from the observed map entirely (integration missing).
        PROMISED_COMPUTED_GOT_PARTIAL: Feature declared as ``computed`` but
            the engine only produced a ``"partially_computed"`` result.
        WRONG_YEAR: Catalog year differs from the requested computation year.
    """

    NOT_COMPUTED = "not_computed"
    FEATURE_ABSENT = "feature_absent"
    PROMISED_COMPUTED_GOT_PARTIAL = "promised_computed_got_partial"
    WRONG_YEAR = "wrong_year"


@dataclass(frozen=True)
class CapabilityEntry:
    """One feature in the capability catalog."""

    feature: str
    status: CapabilityStatus
    description: str = ""


@dataclass(frozen=True)
class CapabilityGap:
    """A mismatch between declared and observed capability status.

    Attributes:
        feature: The feature name from the catalog.
        declared: The :class:`CapabilityStatus` declared in the catalog.
        observed: The raw observed status string (or ``"absent"`` when missing
            from the observed map).
        kind: The :class:`CapabilityGapKind` classifying the mismatch.
    """

    feature: str
    declared: CapabilityStatus
    observed: str
    kind: CapabilityGapKind = CapabilityGapKind.NOT_COMPUTED


@dataclass(frozen=True)
class CapabilityReport:
    """Aggregated capability verification result for one period calculation.

    Attributes:
        catalog_year: The year of the catalog used for verification.
        gaps: All detected gaps, in declaration order.
    """

    catalog_year: int
    gaps: tuple[CapabilityGap, ...]

    @classmethod
    def empty(cls, year: int) -> CapabilityReport:
        """Return an empty report (no gaps) for *year*.

        Returns:
            A :class:`CapabilityReport` with no gaps and ``status == "complete"``.
        """
        return cls(catalog_year=year, gaps=())

    @property
    def status(self) -> str:
        """Derived completeness status.

        Returns:
            ``"complete"`` when no gaps exist, ``"partial"`` when only
            :attr:`~CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL` gaps
            exist, or ``"incomplete"`` otherwise.
        """
        if not self.gaps:
            return "complete"
        kinds = {g.kind for g in self.gaps}
        if kinds <= {CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL}:
            return "partial"
        return "incomplete"

    @property
    def confidence(self) -> str:
        """Derived confidence level: ``"high"`` / ``"medium"`` / ``"low"``.

        Returns:
            ``"high"`` when status is complete, ``"medium"`` when partial,
            ``"low"`` otherwise.  An ``"unverified"`` (incomplete) status
            cannot produce ``"high"`` confidence.
        """
        s = self.status
        if s == "complete":
            return "high"
        if s == "partial":
            return "medium"
        return "low"


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

    def gaps(
        self,
        observed: Mapping[str, str],
        *,
        detect_absent: bool = False,
        year: int | None = None,
    ) -> tuple[CapabilityGap, ...]:
        """Return entries where the observed status is worse than declared.

        The base behavior (``detect_absent=False``, no ``year``) reports only
        features explicitly observed as ``"not_computed"``.  With
        ``detect_absent=True``, features absent from *observed* are also
        reported as :attr:`~CapabilityGapKind.FEATURE_ABSENT` gaps.  When
        *year* is provided and differs from :attr:`year`, a
        :attr:`~CapabilityGapKind.WRONG_YEAR` gap is prepended.

        Args:
            observed: Mapping of feature name to observed calculation status.
            detect_absent: When ``True``, also report features absent from
                *observed* as :attr:`~CapabilityGapKind.FEATURE_ABSENT` gaps.
            year: Computation year to validate against :attr:`year`.  A
                mismatch adds a :attr:`~CapabilityGapKind.WRONG_YEAR` gap.

        Returns:
            Gaps in declaration order (WRONG_YEAR prepended when detected),
            one per mismatched feature.
        """
        result: list[CapabilityGap] = []
        if year is not None and year != self.year:
            result.append(
                CapabilityGap(
                    feature="__catalog__",
                    declared=CapabilityStatus.COMPUTED,
                    observed=str(year),
                    kind=CapabilityGapKind.WRONG_YEAR,
                )
            )
        for entry in self.capabilities:
            if entry.status not in {
                CapabilityStatus.COMPUTED,
                CapabilityStatus.PARTIALLY_COMPUTED,
            }:
                continue
            obs = observed.get(entry.feature)
            if obs is None:
                if detect_absent:
                    result.append(
                        CapabilityGap(
                            feature=entry.feature,
                            declared=entry.status,
                            observed="absent",
                            kind=CapabilityGapKind.FEATURE_ABSENT,
                        )
                    )
            elif obs == "not_computed":
                result.append(
                    CapabilityGap(
                        feature=entry.feature,
                        declared=entry.status,
                        observed=obs,
                        kind=CapabilityGapKind.NOT_COMPUTED,
                    )
                )
            elif (
                entry.status == CapabilityStatus.COMPUTED
                and obs == "partially_computed"
            ):
                result.append(
                    CapabilityGap(
                        feature=entry.feature,
                        declared=entry.status,
                        observed=obs,
                        kind=CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL,
                    )
                )
        return tuple(result)
