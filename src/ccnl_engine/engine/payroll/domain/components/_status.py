"""Calculation status enums and ScopeItem dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CalculationStatus(StrEnum):
    """Whether the engine computed the feature."""

    COMPUTED = "computed"
    PARTIAL = "partial"
    NOT_COMPUTED = "not_computed"
    EXCLUDED = "excluded"


class EligibilityStatus(StrEnum):
    """Verification level of the inputs that triggered the computation."""

    ENGINE_VERIFIED = "engine_verified"
    CALLER_DECLARED = "caller_declared"
    UNKNOWN = "unknown"
    N_A = "n_a"


class SourceQuality(StrEnum):
    """Quality of the normative data source behind the computation."""

    VERIFIED_PRIMARY = "verified_primary"
    UNVERIFIED = "unverified"
    ESTIMATED = "estimated"
    N_A = "n_a"


@dataclass(frozen=True)
class ScopeItem:
    """One entry in the calculation scope list.

    ``calculation_status``
        Whether the engine computed the feature (``"computed"``), partially
        computed it (``"partial"``), could not compute it (``"not_computed"``),
        or the caller did not request it (``"excluded"``).

    Integration axes (``gross_integrated``, ``contribution_integrated``,
    ``tax_integrated``, ``net_integrated``, ``cost_integrated``)
        One boolean per accounting axis.  ``True`` means the feature's amount
        flows into that axis of the period totals.  All axes are ``False`` for
        informational-only features (computed but not wired into any total) and
        for excluded or not-computed features.

    ``eligibility_status``
        Verification level of the inputs that triggered the computation:
        ``"engine_verified"`` when the engine could check all inputs,
        ``"caller_declared"`` when the caller asserted conditions the engine
        cannot verify (e.g. dependent eligibility, disability certification),
        ``"unknown"`` when the engine has no schema to check against, ``"n_a"``
        otherwise.

    ``source_quality``
        Quality of the normative data source behind the computation:
        ``"verified_primary"`` for a verified primary source, ``"unverified"``
        for an unverified or secondary source, ``"estimated"`` for a derived or
        estimated rule, ``"n_a"`` when no source applies.

    ``assumptions``
        Typed simplification flags active for this feature (e.g.
        ``"partial_detrazioni_art15"``).
    """

    feature: str
    calculation_status: CalculationStatus
    gross_integrated: bool = False
    contribution_integrated: bool = False
    tax_integrated: bool = False
    net_integrated: bool = False
    cost_integrated: bool = False
    eligibility_status: EligibilityStatus = EligibilityStatus.N_A
    source_quality: SourceQuality = SourceQuality.N_A
    assumptions: tuple[str, ...] = ()
