"""Every error of a request in JSON, found in one pass.

A batch import UI shows the caller all that is wrong with a row at once,
not one error per attempt.  The request JSON of
:mod:`ccnl_engine.interchange.request.serializers` is read node by node:
each rejected value is one error with its path from the root, and a node
whose children are rejected is not built, so no error is a consequence of
another.
"""

from __future__ import annotations

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.interchange.request.serializers import read_request
from ccnl_engine.period.inputs import PeriodInput
from ccnl_engine.year.competence.inputs import CompetenceYearPlan
from ccnl_engine.year.tax_year.inputs import TaxYearPlan

__all__ = ["validate_request_json"]


def validate_request_json[R: (PeriodInput, CompetenceYearPlan, TaxYearPlan)](
    text: str, kind: type[R]
) -> tuple[InvalidInputError, ...]:
    """Return every error of the request of type ``kind`` in ``text``.

    ``text`` is the JSON of :func:`~ccnl_engine.inputs.request_to_json`.
    Each error is an :class:`~ccnl_engine.errors.InvalidInputError` whose
    ``field`` is the path of the rejected value from the root, e.g.
    ``"PeriodInput.facts.events[1].hours"``.  A text that is not such JSON,
    of another schema version or of another kind of request is one error
    with no field: no value can be read.

    What is checked is what the constructors check, so a text without
    errors reads with :func:`~ccnl_engine.inputs.request_from_json`.  An
    object reports at most one error of its own, the first its constructor
    finds, and is checked only once its children are valid.  Whether the
    bundle holds the CCNL and the level is not checked: the run reports it.

    Args:
        text: The JSON text.
        kind: :class:`~ccnl_engine.PeriodInput`,
            :class:`~ccnl_engine.CompetenceYearPlan` or
            :class:`~ccnl_engine.TaxYearPlan`.

    Returns:
        The errors in the order of the JSON, ``()`` when it is valid.
    """
    try:
        _, errors = read_request(text, kind)
    except InvalidInputError as exc:
        return (exc,)
    return errors
