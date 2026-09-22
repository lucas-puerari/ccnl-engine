"""Feature coverage and confidence of a payroll result."""

from ccnl_engine.engine.payroll.service.scope._scope import (
    _limitations_scope,
    build_scope,
    ccnl_notes_to_limitations,
    compute_confidence,
    compute_result_status,
)

__all__ = [
    "_limitations_scope",
    "build_scope",
    "ccnl_notes_to_limitations",
    "compute_confidence",
    "compute_result_status",
]
