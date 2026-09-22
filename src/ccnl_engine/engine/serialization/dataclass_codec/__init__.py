"""JSON round-trip codec for frozen dataclasses and Pydantic models."""

from ccnl_engine.engine.serialization.dataclass_codec._dump import (
    _deep_freeze,
    _deep_thaw,
    _dump,
)
from ccnl_engine.engine.serialization.dataclass_codec._load import (
    _FIELD_RENAMES,
    _NO_MATCH,
    _load_by_hint,
    _load_dataclass,
    _load_union,
    _try_union_member,
)

__all__ = [
    "_FIELD_RENAMES",
    "_NO_MATCH",
    "_deep_freeze",
    "_deep_thaw",
    "_dump",
    "_load_by_hint",
    "_load_dataclass",
    "_load_union",
    "_try_union_member",
]
