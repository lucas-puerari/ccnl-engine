"""Smoke tests — verify the package is importable and correctly versioned."""

import ccnl_engine


def test_package_importable() -> None:
    """ccnl_engine must be importable without errors."""
    assert ccnl_engine is not None
