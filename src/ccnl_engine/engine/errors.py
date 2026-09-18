"""Structured error hierarchy for ccnl-engine.

Public error codes are declared in ``PUBLIC_ERROR_CODES``.  A code is a
permanent commitment: its name and semantics cannot change without a major
version bump.

Note: Pydantic ``@field_validator`` and ``@model_validator`` methods in the
domain layer must keep raising ``ValueError`` so Pydantic wraps them in
``ValidationError``.  Do not replace those with structured subclasses.
"""

from __future__ import annotations


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
            remediation="Call list_ccnl() to retrieve the valid CCNL identifiers.",
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


class InvalidInputError(ValueError, CcnlEngineError):
    """Raised when caller-supplied inputs are invalid or incompatible.

    Subclasses ``ValueError`` for backward compatibility with existing callers
    that catch ``ValueError``.  New callers should catch ``InvalidInputError``
    or ``CcnlEngineError`` directly.
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
        CcnlEngineError.__init__(
            self,
            message,
            code="invalid_input",
            feature=feature,
            ruleset=ruleset,
            remediation=remediation,
        )


#: Public error codes. Each code is a permanent commitment: its name and
#: semantics cannot change without a major version bump.
PUBLIC_ERROR_CODES: frozenset[str] = frozenset({
    "unknown_ccnl",
    "unknown_level",
    "out_of_scope",
    "data_integrity",
    "invalid_input",
})
