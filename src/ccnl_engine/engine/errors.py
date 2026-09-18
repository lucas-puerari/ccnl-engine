"""Structured error hierarchy for ccnl-engine."""

from __future__ import annotations


class CcnlEngineError(Exception):
    """Base class for all ccnl-engine errors."""


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
        """Initialise with the bad identifier and optional suggestions."""
        self.ccnl_id = ccnl_id
        self.suggestions = suggestions
        parts = [f"Unknown CCNL: {ccnl_id!r}"]
        if suggestions:
            shown = ", ".join(repr(s) for s in suggestions[:3])
            parts.append(f"Did you mean: {shown}?")
        super().__init__(" ".join(parts))


class UnknownLevelError(CcnlEngineError):
    """Raised when a level code cannot be resolved within a CCNL.

    Attributes:
        level_code: The unresolvable level code.
        ccnl_id: The CCNL slug in which the lookup failed.
    """

    def __init__(self, level_code: str, ccnl_id: str) -> None:
        """Initialise with the level code and the CCNL it was looked up in."""
        self.level_code = level_code
        self.ccnl_id = ccnl_id
        super().__init__(f"Unknown level {level_code!r} in CCNL {ccnl_id!r}")
