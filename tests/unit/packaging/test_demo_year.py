"""Tests that demo/app.py derives _DEFAULT_YEAR from the bundle, not the clock."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    import types

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_APP_PY = _PROJECT_ROOT / "demo" / "app.py"


@pytest.fixture(scope="module")
def demo_app() -> types.ModuleType:
    """Load demo/app.py without adding demo/ to sys.path permanently.

    Returns:
        The loaded demo app module.
    """
    spec = importlib.util.spec_from_file_location("_test_demo_app", _APP_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_test_demo_app"] = module
    spec.loader.exec_module(module)
    return module


class TestDemoDefaultYear:
    """demo/app.py resolves _DEFAULT_YEAR from the surtax bundle, not the clock."""

    def test_default_year_matches_bundle(self, demo_app: types.ModuleType) -> None:
        """_DEFAULT_YEAR equals _latest_bundled_year(), not datetime.now().year."""
        assert demo_app._latest_bundled_year() == demo_app._DEFAULT_YEAR

    def test_latest_bundled_year_falls_back_at_future_system_date(
        self, demo_app: types.ModuleType
    ) -> None:
        """_latest_bundled_year() returns 2026 when the system year has no data."""
        future_now = MagicMock()
        future_now.year = 2027
        with patch.object(demo_app, "datetime") as mock_dt:
            mock_dt.now.return_value = future_now
            year = demo_app._latest_bundled_year()
        assert year == 2026

    def test_latest_bundled_year_raises_when_no_data_found(
        self, demo_app: types.ModuleType
    ) -> None:
        """RuntimeError is raised when no bundled year exists before the 2020 floor."""
        old_now = MagicMock()
        old_now.year = 2020
        with (
            patch.object(demo_app, "datetime") as mock_dt,
            patch.object(demo_app, "read_bundled", side_effect=FileNotFoundError),
        ):
            mock_dt.now.return_value = old_now
            with pytest.raises(RuntimeError, match="No bundled surtax data"):
                demo_app._latest_bundled_year()

    def test_list_regioni_returns_all_regions(self, demo_app: types.ModuleType) -> None:
        """list_regioni() returns all 21 Italian regions."""
        result = json.loads(demo_app.list_regioni())
        assert len(result) == 21

    def test_list_comuni_returns_nonempty(self, demo_app: types.ModuleType) -> None:
        """list_comuni() returns a non-empty list of municipalities."""
        result = json.loads(demo_app.list_comuni())
        assert len(result) > 0
