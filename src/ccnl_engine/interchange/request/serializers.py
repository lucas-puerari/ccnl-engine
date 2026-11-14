"""JSON form of the requests of :class:`~ccnl_engine.PayrollEngine`.

A :class:`~ccnl_engine.PeriodInput`, a
:class:`~ccnl_engine.CompetenceYearPlan` or a
:class:`~ccnl_engine.TaxYearPlan` is written as the tagged tree of
:mod:`ccnl_engine.codec.serializers`, in an envelope that carries
its schema version, and read back through the constructors of
:data:`REQUEST_TYPES`, so a request read from JSON is validated like one
built in Python.

Unlike a persisted state, a request carries no engine or bundle version: it
states facts, not balances computed by a version of the rules, so a request
written by one release is read by the next as long as its schema holds.
"""

from __future__ import annotations

import json
from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.codec.serializers import encode, loads, reject
from ccnl_engine.codec.tree.serializers import read_tree
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.interchange.request.types import REQUEST_TYPES
from ccnl_engine.period.inputs import PeriodInput
from ccnl_engine.year.competence.inputs import CompetenceYearPlan
from ccnl_engine.year.tax_year.inputs import TaxYearPlan

if TYPE_CHECKING:
    from collections.abc import Mapping


__all__ = [
    "REQUEST_SCHEMA_VERSION",
    "REQUEST_TYPES",
    "Request",
    "read_request",
    "request_from_json",
    "request_to_json",
]

#: Version of the JSON form of a request: bumped when a field of a request
#: type is renamed, removed or changes meaning.  Version 2 names the CCNL of
#: an ``Employment`` by ``ccnl_id`` (version 1: ``ccnl_slug``, never merged).
REQUEST_SCHEMA_VERSION = 2
#: What to do with a request of another schema: there is no migration.
_OLD_SCHEMA = (
    "a stored request is read by the release that wrote it: install that "
    "release to replay it, or build the request again with the input types"
)

_FEATURE = "request_json"
_SUBJECT = "the request"

#: A request of :class:`~ccnl_engine.PayrollEngine`.
type Request = PeriodInput | CompetenceYearPlan | TaxYearPlan


_NAMES: Mapping[type, str] = MappingProxyType({
    cls: name for name, cls in REQUEST_TYPES.items()
})


def request_to_json(request: Request) -> str:
    """Return ``request`` as JSON text, with its schema version.

    Decimals are written as strings and dates in ISO 8601, so the text
    reads back equal with :func:`request_from_json`.

    Returns:
        The JSON text of the request.
    """
    payload = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "request": encode(request, _NAMES),
    }
    return json.dumps(payload, sort_keys=True)


def request_from_json[R: (PeriodInput, CompetenceYearPlan, TaxYearPlan)](
    text: str, kind: type[R]
) -> R:
    """Return the request of type ``kind`` written by :func:`request_to_json`.

    Every value is rebuilt through its constructor, so the request is
    validated as if built in Python.  A text that is not such JSON, of
    another schema version or holding another kind of request raises
    :class:`~ccnl_engine.errors.InvalidInputError`, and so does the first
    rejected value, with its path, e.g.
    ``"PeriodInput.facts.events[1].hours"``, as field.

    Args:
        text: The JSON text.
        kind: :class:`~ccnl_engine.PeriodInput`,
            :class:`~ccnl_engine.CompetenceYearPlan` or
            :class:`~ccnl_engine.TaxYearPlan`.

    Returns:
        The request.
    """
    request, errors = read_request(text, kind)
    if errors:
        raise errors[0]
    return request


def read_request[R: (PeriodInput, CompetenceYearPlan, TaxYearPlan)](
    text: str, kind: type[R]
) -> tuple[R, tuple[InvalidInputError, ...]]:
    """Read the request of type ``kind`` and every error of its values.

    A text that is not such JSON, of another schema version or holding
    another kind of request raises
    :class:`~ccnl_engine.errors.InvalidInputError`: no value can be read.

    Returns:
        The request, meaningless when there is an error, and one error per
        rejected value, each with its path as field.

    Raises:
        InvalidInputError: When the request is of another schema version;
            there is no migration, the remediation says what to do.
    """
    payload = loads(text, subject=_SUBJECT, feature=_FEATURE)
    version = payload.get("schema_version")
    if version != REQUEST_SCHEMA_VERSION:
        msg = (
            f"{_SUBJECT}: schema_version {version!r} is not the "
            f"{REQUEST_SCHEMA_VERSION!r} this engine reads"
        )
        raise InvalidInputError(msg, feature=_FEATURE, remediation=_OLD_SCHEMA)
    tree = payload.get("request")
    if not isinstance(tree, dict) or tree.get("$type") != kind.__name__:
        reject(_SUBJECT, f"not a {kind.__name__}", feature=_FEATURE)
    request, errors = read_tree(
        tree, kind.__name__, types=REQUEST_TYPES, subject=_SUBJECT, feature=_FEATURE
    )
    return request, errors
