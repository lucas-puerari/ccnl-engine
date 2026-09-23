"""Tests for ccnl_engine.engine.diff module-level lazy imports."""

from __future__ import annotations

import pytest

import ccnl_engine.engine.diff as _diff_mod


def test_impact_result_accessible_from_diff_namespace() -> None:
    """ImpactResult is reachable via the package namespace (lazy-loaded)."""
    cls = _diff_mod.ImpactResult
    assert cls.__name__ == "ImpactResult"


def test_count_affected_scenarios_accessible_from_diff_namespace() -> None:
    """count_affected_scenarios is reachable via the package namespace (lazy-loaded)."""
    fn = _diff_mod.count_affected_scenarios
    assert callable(fn)


def test_unknown_attribute_raises_attribute_error() -> None:
    """Accessing a non-existent name raises AttributeError."""
    with pytest.raises(AttributeError, match="has no attribute"):
        _ = _diff_mod.nonexistent_name
