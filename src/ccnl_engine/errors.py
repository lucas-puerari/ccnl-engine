"""Structured error hierarchy for ccnl-engine.

Public error codes are in ``PUBLIC_ERROR_CODES``: a permanent commitment,
whose names and semantics change only with a major version bump.

Note: Pydantic ``@field_validator`` and ``@model_validator`` methods in the
domain layer must keep raising ``ValueError`` so Pydantic wraps them in
``ValidationError``.  Do not replace those with structured subclasses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


class CcnlEngineError(Exception):
    """Base class for all ccnl-engine public errors.

    Attributes:
        code: Stable machine-readable error code.
        feature: Engine feature that triggered the error, e.g. ``"apprenticeship"``.
        ruleset: CCNL slug when the error is scoped to a specific contract.
        remediation: Suggested fix for the caller, or ``None``.
        result_usable: Whether a partial result is still valid for the caller.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str,
        feature: str | None = None,
        ruleset: str | None = None,
        remediation: str | None = None,
        result_usable: bool = False,
    ) -> None:
        """Initialise with a human-readable message and structured metadata."""
        self.code = code
        self.feature = feature
        self.ruleset = ruleset
        self.remediation = remediation
        self.result_usable = result_usable
        super().__init__(message)


class UnknownCcnlError(CcnlEngineError):
    """Raised when a CCNL identifier cannot be resolved.

    Attributes:
        ccnl_id: The unresolvable identifier.
        suggestions: Similar known identifiers, up to 5.
    """

    def __init__(
        self,
        ccnl_id: str,
        suggestions: tuple[str, ...] = (),
    ) -> None:
        """Initialise with the unresolvable identifier and optional suggestions."""
        self.ccnl_id = ccnl_id
        self.suggestions = suggestions
        parts = [f"Unknown CCNL: {ccnl_id!r}"]
        if suggestions:
            shown = ", ".join(repr(s) for s in suggestions[:3])
            parts.append(f"Did you mean: {shown}?")
        super().__init__(
            " ".join(parts),
            code="unknown_ccnl",
            remediation=(
                "Call PayrollEngine.list_contracts() for the valid CCNL identifiers."
            ),
        )


class UnknownLevelError(CcnlEngineError):
    """Raised when a level code cannot be resolved within a CCNL.

    Attributes:
        level_code: The unresolvable level code.
        ccnl_id: The CCNL slug in which the lookup failed.
    """

    def __init__(self, level_code: str, ccnl_id: str) -> None:
        """Initialise with the unresolvable level code and its CCNL context."""
        self.level_code = level_code
        self.ccnl_id = ccnl_id
        super().__init__(
            f"Unknown level {level_code!r} in CCNL {ccnl_id!r}",
            code="unknown_level",
            ruleset=ccnl_id,
            remediation=(
                f"Check the level codes available in CCNL {ccnl_id!r} "
                "via the CCNL data bundle."
            ),
        )


class OutOfScopeError(CcnlEngineError):
    """Raised when a requested computation cannot be performed for this CCNL.

    Raised when a caller requests a computation (e.g. apprenticeship pay) that
    the CCNL does not model, and no partial result is meaningful.  Features
    that are modelled but not requested are reported as ``"excluded"`` in the
    calculation scope without raising.

    Attributes:
        reason: Sub-reason code, e.g. ``"no_track"``, ``"ambiguous_track"``,
            ``"no_period"``.  Informational only; ``code`` is always
            ``"out_of_scope"``.
    """

    def __init__(
        self,
        message: str,
        *,
        reason: str | None = None,
        feature: str | None = None,
        ruleset: str | None = None,
        remediation: str | None = None,
    ) -> None:
        """Initialise with a human-readable message and optional sub-reason."""
        self.reason = reason
        super().__init__(
            message,
            code="out_of_scope",
            feature=feature,
            ruleset=ruleset,
            remediation=remediation,
            result_usable=False,
        )


class DataIntegrityError(CcnlEngineError):
    """Raised when a knowledge-base file fails an integrity check.

    Covers hash mismatches, year/sector mismatches, and any other case where
    the bundled data is internally inconsistent.  The engine cannot produce a
    trustworthy result when data integrity is violated.
    """

    def __init__(
        self,
        message: str,
        *,
        remediation: str | None = None,
    ) -> None:
        """Initialise with a human-readable message and optional remediation hint."""
        super().__init__(
            message,
            code="data_integrity",
            remediation=remediation,
        )


class InvalidInputError(CcnlEngineError):
    """Raised when caller-supplied inputs are invalid or incompatible.

    Not a ``ValueError``: like every public error it is caught as
    :class:`CcnlEngineError`, so a caller never mistakes a bug of its own
    (or of the engine) for rejected input.

    Attributes:
        field: Path of the rejected field within the input that rejected it,
            e.g. ``"PeriodFacts.events[2]"`` or ``"Employment.roles"``;
            ``None`` when the input as a whole is rejected.
    """

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        feature: str | None = None,
        ruleset: str | None = None,
        remediation: str | None = None,
    ) -> None:
        """Initialise with a human-readable message and optional context fields.

        A rejected ``field`` without a specific ``remediation`` gets the
        generic one: correct that field.
        """
        self.field = field
        if remediation is None and field is not None:
            remediation = f"Correct {field} and build the input again."
        super().__init__(
            message,
            code="invalid_input",
            feature=feature,
            ruleset=ruleset,
            remediation=remediation,
        )


class MissingRequiredFactError(CcnlEngineError):
    """Raised when a computation path requires caller-supplied facts that are absent.

    Some computation paths (e.g. domestic contribution brackets) require facts
    that cannot be derived from the CCNL or tax tables alone.  The engine
    refuses to silently produce zero or approximate results; callers must
    supply the missing facts explicitly.
    """

    def __init__(
        self,
        message: str,
        *,
        feature: str | None = None,
        ruleset: str | None = None,
        remediation: str | None = None,
    ) -> None:
        """Initialise with a human-readable message and optional context fields."""
        super().__init__(
            message,
            code="missing_required_fact",
            feature=feature,
            ruleset=ruleset,
            remediation=remediation,
        )


class MissingRuleError(CcnlEngineError):
    """Raised when the knowledge bundle has no rule value on a date a run needs.

    The date precedes the first value of the rule, or falls in a gap the
    bundle declares (see :class:`~ccnl_engine.contract.identity.rules_validity\
.SalaryGapKind`).

    Attributes:
        as_of: Date the rule was read on.
        gap_kind: Kind of the declared gap, ``None`` before the rule starts.
        detail: Why the rule has no value on ``as_of``.
    """

    def __init__(
        self,
        detail: str,
        *,
        as_of: date,
        gap_kind: str | None = None,
        feature: str | None = None,
        ruleset: str | None = None,
        remediation: str | None = None,
    ) -> None:
        """Initialise with the reason, the date and the rule's context."""
        self.as_of = as_of
        self.gap_kind = gap_kind
        self.detail = detail
        scope = "" if ruleset is None else f" of {ruleset}"
        super().__init__(
            f"no {feature or 'rule'} value{scope} on {as_of}: {detail}",
            code="missing_rule",
            feature=feature,
            ruleset=ruleset,
            remediation=remediation,
        )


class UnsupportedTaxYearError(CcnlEngineError):
    """Raised when the knowledge bundle has no tax tables for a tax year.

    The tax year of a run follows its payment date: a run paid in the next
    year can need tables the bundle does not ship yet.

    Attributes:
        year: The tax year with no bundled tables.
        sector: Tax sector of the missing table, ``None`` for the whole year.
        supported: The tax years the bundle ships, empty when unknown.
    """

    def __init__(
        self, year: int, *, sector: str | None = None, supported: tuple[int, ...] = ()
    ) -> None:
        """Initialise with the unsupported tax year, its sector and the years."""
        self.year, self.sector, self.supported = year, sector, supported
        scope = f" for sector {sector!r}" if sector is not None else ""
        years = ", ".join(str(y) for y in supported) or "none"
        super().__init__(
            f"No tax tables for tax year {year}{scope} in the knowledge bundle",
            code="unsupported_tax_year",
            remediation=(
                f"Supported tax years: {years} (catalog.supported_tax_years); "
                "upgrade the knowledge bundle once the year is published."
            ),
        )


#: Public error codes (see the module docstring).
PUBLIC_ERROR_CODES: frozenset[str] = frozenset({
    "unknown_ccnl",
    "unknown_level",
    "out_of_scope",
    "data_integrity",
    "invalid_input",
    "missing_required_fact",
    "unsupported_tax_year",
    "missing_rule",
})
