"""Load the central catalog of contract families from the bundle."""

from __future__ import annotations

import json
from functools import cache

from pydantic import ValidationError

from ccnl_engine.agreement.family.models import FamilyCatalog
from ccnl_engine.bundle.loaders import read_resource
from ccnl_engine.errors import DataIntegrityError

__all__ = ["load_family_catalog"]

_FILE = "agreement/family/catalog.json"


@cache
def load_family_catalog() -> FamilyCatalog:
    """Return the catalog of contract families of the bundle.

    Returns:
        The validated catalog, shared by every caller.

    Raises:
        DataIntegrityError: When the file is missing or malformed.
    """
    try:
        data = json.loads(read_resource(_FILE))
        return FamilyCatalog.model_validate(data)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError) as exc:
        msg = f"Contract families: {_FILE} is not a valid catalog: {exc}"
        raise DataIntegrityError(msg) from exc
