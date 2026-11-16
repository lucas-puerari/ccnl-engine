"""A direct hourly floor names the level and the date of the event."""

from __future__ import annotations

from datetime import date
from typing import NoReturn

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.working_time.hourly.direct import direct_hourly_base
from ccnl_engine.working_time.subsector.rules import with_subsector


def _reject(field: str, feature: str, day: date, reason: str) -> NoReturn:
    msg = f"{field} {feature} {day}: {reason}"
    raise LookupError(msg)


def test_a_date_before_the_first_table_is_rejected() -> None:
    """Tabella n. 2 of the florovivaisti starts in 2023: 2022 has no floor."""
    ccnl, _ = with_subsector(
        load_ccnl("operai-agricoli-florovivaisti"),
        "florovivaisti",
        WorkerCategory.OPERAIO,
    )
    assert ccnl.work_rules is not None
    with pytest.raises(LookupError, match="no hourly minimum for this level and date"):
        direct_hourly_base(
            ccnl.work_rules.time_supplements,
            "Area1",
            None,
            date(2022, 12, 31),
            "hours",
            "holiday_work",
            None,
            _reject,
        )
