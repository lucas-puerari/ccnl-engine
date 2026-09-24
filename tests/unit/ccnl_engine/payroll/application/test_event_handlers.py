"""Registry exhaustiveness test for the event handler dispatch table.

Asserts that every concrete WorkEvent type has a registered handler so that
the registry provides the same exhaustiveness guarantee as the isinstance chain
it replaced.
"""

from __future__ import annotations

from typing import get_args

from ccnl_engine.payroll.application._event_handlers import _HANDLER_REGISTRY
from ccnl_engine.payroll.domain.events import WorkEvent


def test_registry_covers_all_work_event_types() -> None:
    """Every concrete WorkEvent type must have a handler in the registry.

    If a new event type is added to the WorkEvent union without registering a
    handler, this test fails — providing the same exhaustiveness guarantee as
    the ``assert_never`` branch that the registry replaced.
    """
    expected = set(get_args(WorkEvent))
    actual = set(_HANDLER_REGISTRY.keys())
    assert actual == expected, (
        f"Handler registry is incomplete.\n"
        f"Missing types: {expected - actual}\n"
        f"Extra types: {actual - expected}"
    )
