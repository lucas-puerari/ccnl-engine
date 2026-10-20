"""JSON form of the results of :class:`~ccnl_engine.PayrollEngine`.

A :class:`~ccnl_engine.PeriodResult`, a
:class:`~ccnl_engine.CompetenceYearResult` or a
:class:`~ccnl_engine.TaxYearResult` is written as the tagged tree of
:mod:`ccnl_engine.codec.serializers`, for a payroll system or an
archive that does not run Python.  The JSON is output only: a result is
recomputed from its request, never read back, so its types need no
registry and every dataclass, Pydantic model and enum is tagged by its
class name.

Next to the fields, ``derived`` holds what the result computes from them
and a reader outside Python could not: payability, the blockers and the
totals.
"""

from __future__ import annotations

import json
from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.codec.serializers import encode
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.version import __version__ as engine_version
from ccnl_engine.year.results import CompetenceYearResult, TaxYearResult

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["RESULT_SCHEMA_VERSION", "result_to_json"]

#: Version of the JSON form of a result: bumped when a field of a result
#: type is renamed, removed or changes meaning.
RESULT_SCHEMA_VERSION = 1

_ASSESSMENT = (
    "is_payable",
    "is_net_pay_payable",
    "is_employer_cost_complete",
    "blockers",
)
_YEAR = ("annual_gross", "annual_net", "annual_employer_cost", *_ASSESSMENT)

#: Properties written under ``derived``, by result type.
_DERIVED: Mapping[type, tuple[str, ...]] = MappingProxyType({
    PeriodResult: ("paid_gross", *_ASSESSMENT),
    CompetenceYearResult: _YEAR,
    TaxYearResult: _YEAR,
})


def result_to_json(
    result: PeriodResult | CompetenceYearResult | TaxYearResult,
) -> str:
    """Return ``result`` as JSON text, with its schema and engine versions.

    Decimals are written as strings and dates in ISO 8601.  The JSON holds
    every field of the result under ``result`` and, under ``derived``,
    ``is_payable``, ``is_net_pay_payable``, ``is_employer_cost_complete``,
    ``blockers`` and the totals: ``paid_gross`` for a period,
    ``annual_gross``, ``annual_net`` and ``annual_employer_cost`` for a
    year.  It is output only: there is no reader.

    Returns:
        The JSON text of the result.
    """
    derived = {name: encode(getattr(result, name)) for name in _DERIVED[type(result)]}
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "engine_version": engine_version,
        "result": encode(result),
        "derived": derived,
    }
    return json.dumps(payload, sort_keys=True)
