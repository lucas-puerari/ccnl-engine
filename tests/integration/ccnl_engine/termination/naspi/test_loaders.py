"""load_naspi_dismissal_rules: the checks of a NASpI contribution file."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.termination.naspi.loaders import load_naspi_dismissal_rules

_READ = "ccnl_engine.termination.naspi.loaders.read_year_json"


def test_invalid_table_raises() -> None:
    """A table that does not validate is a data integrity error."""
    load_naspi_dismissal_rules.cache_clear()
    with (
        patch(_READ, return_value={"year": 2026, "rate": {}}),
        pytest.raises(DataIntegrityError, match="not a valid NASpI dismissal"),
    ):
        load_naspi_dismissal_rules(2026)
    load_naspi_dismissal_rules.cache_clear()


def test_year_mismatch_raises() -> None:
    """A file of another year under the 2026 name is rejected."""
    rules = load_naspi_dismissal_rules(2026)
    assert rules is not None
    raw = rules.model_dump(mode="json", exclude={"ruleset"}) | {"year": 2025}
    load_naspi_dismissal_rules.cache_clear()
    with (
        patch(_READ, return_value=raw),
        pytest.raises(DataIntegrityError, match="does not match requested year"),
    ):
        load_naspi_dismissal_rules(2026)
    load_naspi_dismissal_rules.cache_clear()
