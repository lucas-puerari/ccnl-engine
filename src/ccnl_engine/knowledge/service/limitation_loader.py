"""Engine limitation loader: reads the limitations of shared code paths.

The limitations a CCNL file declares travel with its notes; this loader
reads the others, those of code paths several CCNLs share, from
``knowledge/limitations/data/engine.json``.  A malformed file or entry, or
an id declared twice, raises
:class:`~ccnl_engine.shared.domain.errors.DataIntegrityError`.
"""

from __future__ import annotations

import importlib.resources
import json
from functools import cache

from pydantic import ValidationError

from ccnl_engine.knowledge.service.bundled import read_bundled
from ccnl_engine.shared.domain.errors import DataIntegrityError
from ccnl_engine.shared.domain.limitation import ModelLimitation

__all__ = ["load_engine_limitations", "parse_engine_limitations"]

_SCHEMA_VERSION = 1
_FILE = "engine.json"


def load_engine_limitations() -> tuple[ModelLimitation, ...]:
    """Load the engine limitations from the bundled data file.

    Returns:
        The limitations, in file order.
    """
    return _load_cached()


@cache
def _load_cached() -> tuple[ModelLimitation, ...]:
    pkg = importlib.resources.files("ccnl_engine.knowledge.limitations.data")
    try:
        data = json.loads(read_bundled(pkg, _FILE))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        msg = f"Engine limitations: cannot read {_FILE}: {exc}"
        raise DataIntegrityError(msg) from exc
    return parse_engine_limitations(data)


def parse_engine_limitations(data: object) -> tuple[ModelLimitation, ...]:
    """Build the engine limitations from their decoded JSON document.

    Returns:
        The limitations, in document order.

    Raises:
        DataIntegrityError: When the document or an entry is malformed, or
            an id is declared twice.
    """
    if not isinstance(data, dict) or data.get("schema_version") != _SCHEMA_VERSION:
        msg = f"Engine limitations: expected an object of schema {_SCHEMA_VERSION}"
        raise DataIntegrityError(msg)
    entries = data.get("limitations")
    if not isinstance(entries, list):
        msg = "Engine limitations: 'limitations' must be a list"
        raise DataIntegrityError(msg)
    try:
        limitations = tuple(ModelLimitation.model_validate(e) for e in entries)
    except ValidationError as exc:
        msg = f"Engine limitations: invalid entry: {exc}"
        raise DataIntegrityError(msg) from exc
    ids = [limitation.id for limitation in limitations]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        msg = f"Engine limitations: ids declared twice: {duplicates}"
        raise DataIntegrityError(msg)
    return limitations
