"""The demo shows no tax lines for a household employer."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import types

_APP_PY = Path(__file__).resolve().parents[3] / "demo" / "app.py"


@pytest.fixture(scope="module")
def demo_app() -> types.ModuleType:
    """Load demo/app.py without adding demo/ to sys.path permanently.

    Returns:
        The loaded demo app module.
    """
    spec = importlib.util.spec_from_file_location("_test_demo_app_domestic", _APP_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_test_demo_app_domestic"] = module
    spec.loader.exec_module(module)
    return module


def test_household_employer_shows_no_tax(demo_app: types.ModuleType) -> None:
    """A household employer withholds nothing: no IRPEF and no credit."""
    payload = json.loads(
        demo_app.compute_salary("lavoro-domestico-convivente.json", "A", "permanent", 1)
    )

    assert payload["employer_withholds_irpef"] is False
    assert not payload["irpef_gross"]
    assert not payload["trattamento_integrativo"]
    assert payload["net_monthly"] < payload["gross_monthly"]


def test_company_employer_withholds(demo_app: types.ModuleType) -> None:
    """A company is a withholding agent."""
    payload = json.loads(
        demo_app.compute_salary("commercio-confcommercio.json", "4", "permanent", 1)
    )

    assert payload["employer_withholds_irpef"] is True
