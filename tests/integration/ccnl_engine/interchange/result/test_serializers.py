"""JSON form of a result: every field, the derived assessment, the versions."""

from __future__ import annotations

import json
from decimal import Decimal

from ccnl_engine import PayrollEngine, TaxYearPlan
from ccnl_engine.interchange.result.serializers import (
    RESULT_SCHEMA_VERSION,
    result_to_json,
)
from ccnl_engine.version import __version__ as engine_version
from tests.knowledge.ccnl_engine.period.builders import competence_year, regular_run

_ENGINE = PayrollEngine.bundled()


def test_a_period_result_is_written_with_its_fields_and_assessment() -> None:
    """The amounts are exact decimals and the assessment is derived."""
    result = _ENGINE.calculate_period(regular_run(1))
    payload = json.loads(result_to_json(result))
    assert payload["schema_version"] == RESULT_SCHEMA_VERSION
    assert payload["engine_version"] == engine_version
    fields = payload["result"]["fields"]
    assert payload["result"]["$type"] == "PeriodResult"
    assert Decimal(fields["period_net"]["$decimal"]) == result.period_net
    assert fields["payment_date"] == {"$date": result.payment_date.isoformat()}
    derived = payload["derived"]
    assert derived["is_payable"] is result.is_payable
    assert derived["is_net_pay_payable"] is result.is_net_pay_payable
    assert derived["is_employer_cost_complete"] is result.is_employer_cost_complete
    assert Decimal(derived["paid_gross"]["$decimal"]) == result.paid_gross
    assert len(derived["blockers"]["$tuple"]) == len(result.blockers)


def test_year_results_are_written_with_their_totals() -> None:
    """A competence year and a tax year carry the annual totals."""
    year = _ENGINE.calculate_competence_year(competence_year())
    tax_year = _ENGINE.calculate_tax_year(
        TaxYearPlan(tax_year=2026, competence_years=(competence_year(),))
    )
    for result in (year, tax_year):
        payload = json.loads(result_to_json(result))
        derived = payload["derived"]
        assert Decimal(derived["annual_net"]["$decimal"]) == result.annual_net
        assert Decimal(derived["annual_gross"]["$decimal"]) == result.annual_gross
        assert (
            Decimal(derived["annual_employer_cost"]["$decimal"])
            == result.annual_employer_cost
        )
        assert derived["is_payable"] is result.is_payable
        periods = payload["result"]["fields"]["period_results"]["$tuple"]
        assert len(periods) == len(result.period_results)


def test_the_text_of_a_result_is_stable() -> None:
    """One result, one text: a batch can diff two runs."""
    first = _ENGINE.calculate_period(regular_run(1))
    second = _ENGINE.calculate_period(regular_run(1))
    assert result_to_json(first) == result_to_json(second)
