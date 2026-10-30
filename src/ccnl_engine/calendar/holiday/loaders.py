"""Load the national holidays from the bundle."""

from __future__ import annotations

import json
from functools import cache

from pydantic import ValidationError

from ccnl_engine.bundle.loaders import read_resource
from ccnl_engine.calendar.holiday.models import NationalHolidays
from ccnl_engine.errors import DataIntegrityError

__all__ = ["load_national_holidays"]

_FILE = "calendar/holiday/national.json"


@cache
def load_national_holidays() -> NationalHolidays:
    """Return the national holidays of the bundle.

    Returns:
        The validated list.

    Raises:
        DataIntegrityError: When the file is missing or malformed.
    """
    try:
        return NationalHolidays.model_validate(json.loads(read_resource(_FILE)))
    except (FileNotFoundError, json.JSONDecodeError, ValidationError) as exc:
        msg = f"National holidays: {_FILE} is not a valid list: {exc}"
        raise DataIntegrityError(msg) from exc
