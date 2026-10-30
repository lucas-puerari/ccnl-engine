"""Load the census of a CCNL from the bundle."""

from __future__ import annotations

import json
from functools import cache

from pydantic import ValidationError

from ccnl_engine.agreement.census.models import Census
from ccnl_engine.bundle.loaders import read_resource
from ccnl_engine.errors import DataIntegrityError

__all__ = ["load_census"]

#: Version of the census format the loader reads.
CENSUS_SCHEMA = 1


@cache
def load_census(ccnl_id: str) -> Census | None:
    """Return the census of the CCNL *ccnl_id*, ``None`` when it has none.

    A CCNL without a census is not complete: the completeness report lists
    it as not yet censused.

    Returns:
        The validated census of ``knowledge/census/<ccnl_id>.json``.

    Raises:
        DataIntegrityError: When the file is malformed, of another schema
            or of another CCNL.
    """
    path = f"census/{ccnl_id}.json"
    try:
        data = json.loads(read_resource(path))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        msg = f"Census: {path} is not JSON: {exc}"
        raise DataIntegrityError(msg) from exc
    try:
        census = Census.model_validate(data)
    except ValidationError as exc:
        msg = f"Census: {path} is not a valid census: {exc}"
        raise DataIntegrityError(msg) from exc
    if census.schema_version != CENSUS_SCHEMA or census.ccnl_id != ccnl_id:
        msg = (
            f"Census: {path} must be schema {CENSUS_SCHEMA} of {ccnl_id!r}, "
            f"not schema {census.schema_version} of {census.ccnl_id!r}"
        )
        raise DataIntegrityError(msg)
    return census
