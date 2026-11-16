"""The daily-quota method of a sick day, read from the CCNL work rules."""

from __future__ import annotations

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.sickness.services import _method


def test_a_ccnl_without_work_rules_has_no_sick_day_method() -> None:
    """No sickness nor absence rules: no daily-quota method."""
    ccnl = load_ccnl("commercio-confcommercio").model_copy(update={"work_rules": None})
    assert _method(ccnl) is None
