"""Every error of a request in JSON, each at its path, in one pass."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from typing import Any

from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.inputs import Apprentice, Employment
from ccnl_engine.interchange.request.serializers import request_to_json
from ccnl_engine.interchange.request.validators import validate_request_json
from ccnl_engine.period.inputs import PeriodFacts, PeriodInput
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.working_time.inputs import OvertimeEvent
from ccnl_engine.year.tax_year.inputs import TaxYearPlan


def _request() -> PeriodInput:
    overtime = OvertimeEvent(date(2026, 3, 10), Decimal(2), Decimal("15.00"))
    return PeriodInput(
        run=PayrollRun.regular(2026, 3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            contract_type=Apprentice(months_elapsed=7),
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=PeriodFacts(events=(overtime, overtime)),
    )


def _payload() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(request_to_json(_request()))
    return payload


def test_a_valid_request_has_no_error() -> None:
    """The JSON of a request built in Python validates clean."""
    assert validate_request_json(request_to_json(_request()), PeriodInput) == ()


def test_three_independent_errors_are_returned_with_their_paths() -> None:
    """A bad date, a rejected contract and a rejected event: three errors."""
    payload = _payload()
    request = payload["request"]["fields"]
    request["payment_date"] = {"$date": "2026-02-30"}
    contract = request["employment"]["fields"]["contract_type"]["fields"]
    contract["months_elapsed"] = -1
    events = request["facts"]["fields"]["events"]["$tuple"]
    events[1]["fields"]["hours"] = {"$decimal": "-2"}
    errors = validate_request_json(json.dumps(payload), PeriodInput)
    assert [error.field for error in errors] == [
        "PeriodInput.employment.contract_type.months_elapsed",
        "PeriodInput.facts.events[1].hours",
        "PeriodInput.payment_date",
    ]
    assert all(error.code == "invalid_input" for error in errors)


def test_a_text_that_cannot_be_read_is_one_error_without_a_field() -> None:
    """No value can be read from text that is not a request of the kind."""
    (not_json,) = validate_request_json("not json", PeriodInput)
    (other_kind,) = validate_request_json(request_to_json(_request()), TaxYearPlan)
    assert not_json.field is None
    assert other_kind.field is None
